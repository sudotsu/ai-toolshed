#!/usr/bin/env python3
"""Validate the ux-ui-revision skill package and run its regression suite."""

from __future__ import annotations
import argparse,json,py_compile,re,subprocess,sys,tempfile
from pathlib import Path

REQUIRED={
"SKILL.md","skill-manifest.json","agents/openai.yaml","assets/icon.svg",
"references/revision-contract.md","references/authority-and-external-actions.md","references/verification-and-convergence.md","references/forward-testing.md",
"scripts/bootstrap_revision.py","scripts/render_revision.py","scripts/validate_ux_ui_revision.py","scripts/test_validator.py","scripts/validate_skill.py"
}
LINK=re.compile(r"\[[^\]]+\]\(([^)]+)\)")

def validate(root:Path,run_tests=True):
    errors=[]
    for rel in REQUIRED:
        if not (root/rel).is_file(): errors.append(f"missing skill file: {rel}")
    if errors:return errors
    try: manifest=json.loads((root/"skill-manifest.json").read_text(encoding="utf-8"))
    except Exception as exc:return [f"manifest invalid: {exc}"]
    if manifest.get("name")!="ux-ui-revision": errors.append("manifest name mismatch")
    text=(root/"SKILL.md").read_text(encoding="utf-8")
    if not re.search(r"^name:\s*ux-ui-revision\s*$",text,re.M): errors.append("SKILL.md name mismatch")
    for path in root.rglob("*.md"):
        for target in LINK.findall(path.read_text(encoding="utf-8")):
            clean=target.split("#",1)[0]
            if not clean or "://" in clean or clean.startswith("mailto:"): continue
            dest=(path.parent/clean).resolve()
            try: dest.relative_to(root.resolve())
            except ValueError: errors.append(f"{path.relative_to(root)} links outside skill: {target}"); continue
            if not dest.exists(): errors.append(f"broken link in {path.relative_to(root)}: {target}")
    with tempfile.TemporaryDirectory() as t:
        for path in (root/"scripts").glob("*.py"):
            try: py_compile.compile(str(path),cfile=str(Path(t)/(path.stem+".pyc")),doraise=True)
            except py_compile.PyCompileError as exc: errors.append(f"compile failed {path.name}: {exc.msg}")
    if run_tests and not errors:
        proc=subprocess.run([sys.executable,"-m","unittest","discover","-s","scripts","-p","test_*.py","-v"],cwd=root,capture_output=True,text=True)
        if proc.returncode: errors.append("regression suite failed:\n"+proc.stdout+proc.stderr)
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("root",nargs="?",type=Path,default=Path(__file__).resolve().parents[1]); ap.add_argument("--no-tests",action="store_true"); a=ap.parse_args()
    errors=validate(a.root.resolve(),not a.no_tests)
    if errors:
        print(f"skill validation failed with {len(errors)} error(s):"); [print("-",e) for e in errors]; return 1
    print("ux-ui-revision skill validation passed"); return 0
if __name__=="__main__": raise SystemExit(main())
