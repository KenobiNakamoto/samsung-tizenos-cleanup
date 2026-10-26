from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class IdentityTests(unittest.TestCase):
 def test_independent_identity_remains_consistent_and_cannot_reinitialize(self):
  with tempfile.TemporaryDirectory(prefix='tizen-identity-test-') as directory:
   root=Path(directory)
   shutil.copytree(ROOT/'app',root/'app')
   for name in ('tools/project.py','native-home/Control.cs','tests/launcher.test.js'):
    target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
   def run(*args):return subprocess.run([sys.executable,'tools/project.py',*args],cwd=root,capture_output=True,text=True)
   self.assertEqual(run('init','--package','INVALID').returncode,2)
   result=run('init','--package','Fh1234abcd');self.assertEqual(result.returncode,0,result.stderr)
   self.assertEqual(run('check').returncode,0)
   self.assertIn('Fh1234abcd.FamilyHome',(root/'app/device.js').read_text())
   self.assertIn('/opt/usr/apps/Fh1234abcd',(root/'native-home/Control.cs').read_text())
   self.assertEqual(run('init','--package','Fh9876abcd').returncode,2)
if __name__=='__main__':unittest.main()
