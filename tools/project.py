"""Local-only validation, independent app identity and unsigned widget packaging."""
from pathlib import Path
import argparse, hashlib, json, re, uuid, zipfile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'app'
def identity():
    root=ET.parse(APP/'config.xml').getroot()
    item=root.find('{http://tizen.org/ns/widgets}application')
    return item.attrib['package'],item.attrib['id']
def check():
    package,app=identity()
    assert re.fullmatch(r'[A-Za-z0-9]{10}',package), 'Package must be ten alphanumeric characters'
    assert app==package+'.FamilyHome', 'Application identity mismatch'
    assert "var SELF = '"+app+"';" in (APP/'device.js').read_text(), 'Self-filter identity mismatch'
    assert 'const string Target="'+app+'";' in (ROOT/'native-home/Control.cs').read_text(), 'Native target mismatch'
    assert 'connect-src \'none\'' in (APP/'index.html').read_text(), 'Expected offline CSP'
    for file in APP.rglob('*'):
        assert not file.is_symlink(), 'Symlink: '+str(file)
        if file.is_file():
            assert file.suffix not in ('.p12','.pfx','.key','.pem','.wgt'), 'Private/generated material'
    allowed={'manrope.woff2':'e310b55a7fd9677f5e3555e6c6c4d064fa1f1d24393f0ddbe217cea12a8c432f'}
    for item in json.loads((APP/'assets/fonts/SOURCES.json').read_text()):
        if Path(item['file']).suffix in ('.woff2','.woff','.ttf','.otf'):
            allowed['fonts/'+item['file']]=item['sha256']
    for f in (APP/'assets').rglob('*'):
        if f.suffix in ('.woff2','.woff','.ttf','.otf'):
            assert allowed.get(f.relative_to(APP/'assets').as_posix())==hashlib.sha256(f.read_bytes()).hexdigest(), 'Unreviewed font'
    for name in ('index.html','main.js','device.js','family-layout.js','LICENSE','THIRD_PARTY_NOTICES.md'):
        assert (APP/name).is_file(), 'Missing '+name
    return package,app
def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='mode',required=True)
    sub.add_parser('check'); sub.add_parser('build')
    init=sub.add_parser('init');init.add_argument('--package',default=None)
    args=ap.parse_args()
    if args.mode=='init':
        package=args.package or 'Fh'+uuid.uuid4().hex[:8]
        if not re.fullmatch(r'[A-Za-z0-9]{10}',package):ap.error('Use exactly ten alphanumeric characters')
        old,_=identity()
        if old!='FamHome001':ap.error('Identity already customized. Keep it stable for updates.')
        if package==old:ap.error('Choose a fresh identity for an independent installation')
        for f in (APP/'config.xml',APP/'device.js',ROOT/'native-home/Control.cs',ROOT/'tests/launcher.test.js'):
            f.write_text(f.read_text().replace(old,package))
        print('Independent identity:',package+'.FamilyHome','Keep this identity and your author certificate for all updates.')
    package,app=check()
    if args.mode=='build':
        dest=ROOT/'dist/FamilyHome-unsigned.wgt';dest.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for f in sorted(APP.rglob('*')):
                if f.is_file() and f.name!='.DS_Store':z.write(f,f.relative_to(APP).as_posix())
        print(dest);print('SHA256',hashlib.sha256(dest.read_bytes()).hexdigest());print('Unsigned: sign with your own Samsung profile before installing.')
    else:print('Checked',app)
if __name__=='__main__':main()
