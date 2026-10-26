from pathlib import Path
import importlib.util, sqlite3, tempfile, unittest
spec=importlib.util.spec_from_file_location('plan',Path(__file__).resolve().parents[1]/'tools/registry_plan.py');plan=importlib.util.module_from_spec(spec);spec.loader.exec_module(plan)
class PlanTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'registry.db';self.db=sqlite3.connect(self.path);self.addCleanup(self.db.close)
  self.row=dict(zip(plan.IDENTITY+plan.FIELDS,['example.app','example','/opt/usr/apps/example/bin/main','svcapp','capp','true','false','false','true','true']))
  self.db.execute('CREATE TABLE package_app_info('+','.join(k+' TEXT' for k in self.row)+')')
  self.db.execute('INSERT INTO package_app_info VALUES('+','.join('?' for _ in self.row)+')',tuple(self.row.values()));self.db.commit()
 def scripts(self):return plan.generate(self.path,{'apps':[self.row]})[:2]
 def test_round_trip_and_unrelated_change_preserved(self):
  a,r=self.scripts();self.db.executescript(a)
  self.db.execute("INSERT INTO package_app_info (app_id,app_disable) VALUES ('new.unrelated','true')");self.db.commit();self.db.executescript(r)
  self.assertEqual(self.db.execute('SELECT app_disable,app_onboot,app_autorestart FROM package_app_info WHERE app_id=?',('example.app',)).fetchone(),('false','true','true'))
  self.assertEqual(self.db.execute("SELECT app_disable FROM package_app_info WHERE app_id='new.unrelated'").fetchone()[0],'true')
 def test_drift_fails_without_changes(self):
  a,_=self.scripts();self.db.execute("UPDATE package_app_info SET app_exec='/changed'");self.db.commit()
  with self.assertRaises(sqlite3.IntegrityError):self.db.executescript(a)
  self.db.rollback();self.assertEqual(self.db.execute('SELECT app_disable FROM package_app_info').fetchone()[0],'false')
 def test_missing_app_rejected(self):
  self.db.execute('DELETE FROM package_app_info');self.db.commit()
  with self.assertRaises(ValueError):self.scripts()
 def test_trigger_rejected(self):
  self.db.execute('CREATE TRIGGER surprising AFTER UPDATE ON package_app_info BEGIN SELECT 1; END;');self.db.commit()
  with self.assertRaises(ValueError):self.scripts()
 def test_restore_drift_rejected(self):
  a,r=self.scripts();self.db.executescript(a);self.db.execute("UPDATE package_app_info SET app_autorestart='true'");self.db.commit()
  with self.assertRaises(sqlite3.IntegrityError):self.db.executescript(r)
  self.db.rollback();self.assertEqual(self.db.execute('SELECT app_autorestart FROM package_app_info').fetchone()[0],'true')
 def test_sql_quote_is_data(self):
  self.db.execute('UPDATE package_app_info SET app_exec=?',("/a'b",));self.db.commit();self.row['app_exec']="/a'b"
  a,r=self.scripts();self.db.executescript(a);self.db.executescript(r)
  self.assertEqual(self.db.execute('SELECT app_exec FROM package_app_info').fetchone()[0],"/a'b")
if __name__=='__main__':unittest.main()
