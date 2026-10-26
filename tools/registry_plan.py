"""Generate guarded apply/restore SQL from YOUR consistent backup. No TV connection."""
from pathlib import Path
import argparse, hashlib, json, sqlite3
TABLE='package_app_info'
IDENTITY=('app_id','package','app_exec','app_component','app_type','app_removable','app_package_system')
FIELDS=('app_disable','app_onboot','app_autorestart')
TARGET=('true','false','false')
def quote(v):
    if v is None:return 'NULL'
    if not isinstance(v,str):raise ValueError('Expected text or NULL registry value')
    return "'"+v.replace("'","''")+"'"
def where(row,keys):return ' AND '.join(k+' IS '+quote(row[k]) for k in keys)
def guard(sql):return 'INSERT INTO plan_guard SELECT '+sql+';'
def generate(database,profile):
    with sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Backup integrity failed')
        if db.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger' AND tbl_name=?",(TABLE,)).fetchone()[0]:raise ValueError('Unexpected registry trigger')
        cols={r[1] for r in db.execute('PRAGMA table_info('+TABLE+')')}
        if not set(IDENTITY+FIELDS)<=cols:raise ValueError('Unrecognized schema')
        apps=profile['apps']; ids=[x['app_id'] for x in apps]
        if not apps or len(ids)!=len(set(ids)):raise ValueError('Empty/duplicate selection')
        rows=[]
        for expected in apps:
            found=db.execute('SELECT * FROM '+TABLE+' WHERE app_id=?',(expected['app_id'],)).fetchall()
            if len(found)!=1:raise ValueError('Missing/ambiguous app: '+expected['app_id'])
            row=dict(found[0])
            if any(row[k]!=expected[k] for k in IDENTITY):raise ValueError('Identity differs from reviewed profile: '+row['app_id'])
            if any(row[k] not in ('true','false') for k in FIELDS):raise ValueError('Unexpected registry flags')
            rows.append(row)
    start=['BEGIN IMMEDIATE;','CREATE TEMP TABLE plan_guard(ok INTEGER NOT NULL CHECK(ok=1));',guard("count(*)=0 FROM sqlite_master WHERE type='trigger' AND tbl_name='"+TABLE+"'")]
    apply=start.copy();restore=start.copy()
    for r in rows:
        current=dict(r);current.update(zip(FIELDS,TARGET));ident=where(r,IDENTITY)
        apply.append(guard('count(*)=1 FROM '+TABLE+' WHERE '+where(r,IDENTITY+FIELDS)))
        restore.append(guard('count(*)=1 FROM '+TABLE+' WHERE '+ident+' AND (('+where(r,FIELDS)+') OR ('+where(current,FIELDS)+'))'))
    for r in rows:
        ident=where(r,IDENTITY)
        apply.append('UPDATE '+TABLE+' SET '+','.join(k+'='+quote(v) for k,v in zip(FIELDS,TARGET))+' WHERE '+ident+';')
        apply.append(guard('changes()=1'))
        restore.append('UPDATE '+TABLE+' SET '+','.join(k+'='+quote(r[k]) for k in FIELDS)+' WHERE '+ident+';')
        restore.append(guard('changes()=1'))
    for script in (apply,restore):script+=['DROP TABLE plan_guard;','COMMIT;']
    return '\n'.join(apply)+'\n','\n'.join(restore)+'\n',rows

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--backup',type=Path,required=True);ap.add_argument('--profile',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    if args.out.exists():ap.error('Output must be a NEW directory; preserve earlier plans')
    profile=json.loads(args.profile.read_text())
    apply,restore,rows=generate(args.backup,profile)
    args.out.mkdir(parents=True,mode=0o700)
    for name,text in [('apply.sql',apply),('restore.sql',restore)]:
        f=args.out/name;f.write_text(text);f.chmod(0o600)
    manifest={'status':'offline_plan_not_live_authorization','reference_model':profile['model'],'reference_build':profile['build'],'backup_sha256':hashlib.sha256(args.backup.read_bytes()).hexdigest(),'profile_sha256':hashlib.sha256(args.profile.read_bytes()).hexdigest(),'selected_app_count':len(rows),'files':{n:hashlib.sha256((args.out/n).read_bytes()).hexdigest() for n in ('apply.sql','restore.sql')}}
    (args.out/'PLAN.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared',len(rows),'selected app records at',args.out)
    print('No TV contacted. Revalidate live model/build, database, dependencies and backup before execution.')
if __name__=='__main__':main()
