from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
class NativeGuards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  spec=importlib.util.spec_from_file_location('native_run',ROOT/'native-home/run.py');self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m);self.m.DIR=Path(self.tmp.name);self.m.ROOT=self.m.DIR
  self.info={'device':{'modelName':'TQ65S85DAEXXC','id':'test-device-id'}}
 def invoke(self,mode):
  args=['run.py',mode,'--host','192.0.2.50','--sdb',sys.executable]
  with patch.object(sys,'argv',args),patch.object(self.m.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(self.info).encode())),patch.object(self.m.subprocess,'run') as call,contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):result=self.m.main()
  call.assert_not_called()
  return result
 def baseline(self,device='test-device-id',digest=None):
  raw=b'{"example":"not a real TV baseline"}';(self.m.DIR/'original.json').write_bytes(raw)
  (self.m.DIR/'BASELINE.json').write_text(json.dumps({'device_id':device,'target_app':self.m.TARGET,'sha256':digest or hashlib.sha256(raw).hexdigest()}))
 def test_other_model_rejected_before_sdb(self):
  self.info['device']['modelName']='OTHER';self.assertEqual(self.invoke('query'),1)
 def test_missing_device_identity_rejected(self):
  self.info['device'].pop('id');self.assertEqual(self.invoke('query'),1)
 def test_other_device_baseline_rejected(self):
  self.baseline(device='other-device');self.assertEqual(self.invoke('apply'),1)
 def test_changed_baseline_rejected_before_staging(self):
  self.baseline(digest='0'*64);self.assertEqual(self.invoke('apply'),1)
 def test_capture_cannot_overwrite_baseline(self):
  self.baseline()
  with self.assertRaises(SystemExit) as e:self.invoke('capture')
  self.assertEqual(e.exception.code,2)
if __name__=='__main__':unittest.main()
