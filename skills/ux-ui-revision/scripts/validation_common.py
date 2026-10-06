from __future__ import annotations
import os,subprocess,sys
from pathlib import Path

def candidates():
    here=Path(__file__).resolve().parents[2]
    env=os.environ.get('UX_UI_TEARDOWN_SKILL')
    out=[]
    if env: out.append(Path(env))
    out += [here/'ux-ui-teardown',Path.home()/'.agents/skills/ux-ui-teardown',Path.home()/'.claude/skills/ux-ui-teardown']
    return out

def find_teardown_skill():
    for root in candidates():
        skill=root/'SKILL.md'; val=root/'scripts/validate_ux_ui_teardown.py'
        if skill.is_file() and val.is_file():
            text=skill.read_text(encoding='utf-8')
            if '\nname: ux-ui-teardown\n' in text or text.startswith('---\nname: ux-ui-teardown\n'):
                return root
    return None

def run_upstream_validator(teardown:Path):
    root=find_teardown_skill()
    if not root: return False,'cannot locate exact ux-ui-teardown validator'
    proc=subprocess.run([sys.executable,str(root/'scripts/validate_ux_ui_teardown.py'),str(teardown)],capture_output=True,text=True,check=False)
    return proc.returncode==0,(proc.stdout+proc.stderr).strip()
