"""Decode one archive-root base64 command result after identity/cleanup/hash checks."""
from pathlib import Path
import argparse,base64,hashlib,json,re

def extract(report,command,sha256):
    if not re.fullmatch(r'[a-fA-F0-9]{64}',sha256):raise ValueError('Expected a SHA-256 digest')
    if report.get('authenticated') is not True or any(type(report.get(k)) is not int or report[k]!=0 for k in ('uid','euid','gid','egid')):raise ValueError('Root identity not verified')
    if report.get('staging_cleaned') is not True or report.get('system_files_unchanged') is not True:raise ValueError('Root cleanup checks not successful')
    results=[r for r in report.get('commands',[]) if r.get('command')==command]
    if len(results)!=1:raise ValueError('Command result missing or ambiguous')
    r=results[0]
    if r.get('exit_code')!=0 or r.get('timed_out') is not False:raise ValueError('Command failed or timed out')
    value=r.get('stdout')
    if not isinstance(value,str) or len(value)>64*1024*1024:raise ValueError('Missing/oversized payload')
    raw=base64.b64decode(''.join(value.split()),validate=True)
    if hashlib.sha256(raw).hexdigest()!=sha256.lower():raise ValueError('Backup hash mismatch')
    return raw

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--report',type=Path,required=True);p.add_argument('--command',required=True,help='Exact command string from report, for example base64 /path/registry.db');p.add_argument('--sha256',required=True,help='Digest independently read on the TV');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    raw=extract(json.loads(a.report.read_text()),a.command,a.sha256)
    with a.out.open('xb') as f:f.write(raw)
    a.out.chmod(0o600);print('Verified backup saved:',a.out,'bytes',len(raw))
if __name__=='__main__':main()
