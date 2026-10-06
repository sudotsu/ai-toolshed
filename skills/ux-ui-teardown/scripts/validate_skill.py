#!/usr/bin/env python3
"""Minimal package validator; repository generic validator performs the shared checks."""
import argparse,json,py_compile,tempfile
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root',nargs='?',default='.'); a=ap.parse_args(); root=Path(a.root).resolve(); errors=[]
    try:m=json.loads((root/'skill-manifest.json').read_text())
    except Exception as e: print('invalid manifest:',e); return 1
    for rel in m.get('required_files',[]):
        if not (root/rel).is_file(): errors.append(f'missing {rel}')
    with tempfile.TemporaryDirectory() as t:
        for p in (root/'scripts').glob('*.py'):
            try: py_compile.compile(str(p),cfile=str(Path(t)/(p.stem+'.pyc')),doraise=True)
            except Exception as e: errors.append(f'{p.name}: {e}')
    if errors:
        print('\n'.join(errors)); return 1
    print('ux-ui-teardown package validation passed'); return 0
if __name__=='__main__': raise SystemExit(main())
