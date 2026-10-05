from __future__ import annotations
import copy, json, tempfile, unittest
from pathlib import Path
import render_handoff
from validate_ux_ui_teardown import validate, MODULES, ACCESS

def fixture():
    evidence=[
        {"id":"EVID-001","evidence_class":"interaction_reproduction","title":"Primary journey run","locator":"local://run-1","accessed_at":"2026-10-05","volatile":False,"summary":"Primary quote journey reproduced at mobile and desktop with pointer and keyboard.","limitations":[]},
        {"id":"EVID-002","evidence_class":"standard_reference","title":"WCAG 2.2","locator":"https://www.w3.org/TR/WCAG22/","accessed_at":"2026-10-05","volatile":False,"summary":"Applicable accessibility baseline.","limitations":[]},
    ]
    findings={
        "schema_version":"ux-ui-teardown-v1",
        "audit":{"project_name":"Fixture","project_locator":"repo://fixture","audited_revision":"abc123","production_locator":"https://example.test","production_revision_status":"verified","audit_start_date":"2026-10-05","audit_end_date":"2026-10-05","review_status":"complete","project_type":"web_app","primary_user_groups":["customer"],"primary_goals":["request a quote"]},
        "evidence_sources":evidence,
        "journeys":[{"id":"JOURNEY-001","title":"Request quote","user_group":"customer","trigger":"needs service","intended_outcome":"submit request","criticality":"primary","entry_points":["home"],"steps":["open home","choose quote","submit"],"required_states":["default","focus","validation","success"],"viewport_ids":["VIEW-001","VIEW-002"],"input_modes":["pointer_touch","keyboard"],"evidence_ids":["EVID-001"],"status":"passed","limitations":[]}],
        "findings":[{"id":"UXUI-001","title":"Focus state is not visually distinguishable","kind":"gap","domains":["accessibility.focus"],"status":"open","severity":"high","confidence":"confirmed","verification_state":"observed","judgment_basis":"standard_requirement","standard_refs":["WCAG 2.2 2.4.7 Focus Visible"],"journey_ids":["JOURNEY-001"],"surface_targets":["quote button"],"evidence_ids":["EVID-001","EVID-002"],"observed_condition":"Keyboard focus on the primary quote control has no visible indicator.","desired_condition":"Keyboard focus is clearly visible.","user_consequence":"Observed keyboard navigation does not expose current focus on the primary action.","business_risk":"Keyboard users can lose position before the primary conversion action.","recommendation":"Provide a visible focus treatment that remains distinguishable across supported backgrounds.","acceptance_criteria":["Primary quote control has a visible focus indicator"],"verification_methods":["Keyboard-run the primary journey"],"implementation_targets":["components/QuoteButton"],"preservation_constraints":[],"dependencies":[],"conflicts":[],"non_goals":["visual rebrand"]}]
    }
    modules=[]
    for mid in sorted(MODULES):
        modules.append({"id":mid,"materiality":"high" if mid in {"accessibility_semantics_keyboard","interaction_affordance_feedback"} else "medium","status":"failed" if mid=="accessibility_semantics_keyboard" else "passed","finding_ids":["UXUI-001"] if mid=="accessibility_semantics_keyboard" else [],"evidence_ids":["EVID-001"],"limitations":[]})
    coverage={
        "schema_version":"ux-ui-teardown-coverage-v1","review_status":"complete",
        "access":[{"category":cat,"status":"available" if cat in {"source_repository","production_experience"} else "not_applicable","material_to_comprehensive":False,"evidence_ids":["EVID-001"] if cat in {"source_repository","production_experience"} else [],"limitations":[],"next_step":"none"} for cat in sorted(ACCESS)],
        "modules":modules,
        "viewports":[
            {"id":"VIEW-001","label":"mobile","width":390,"height":844,"class":"narrow_mobile","status":"observed","journey_ids":["JOURNEY-001"],"evidence_ids":["EVID-001"],"limitations":[]},
            {"id":"VIEW-002","label":"desktop","width":1440,"height":900,"class":"desktop","status":"observed","journey_ids":["JOURNEY-001"],"evidence_ids":["EVID-001"],"limitations":[]}
        ],
        "input_modes":[
            {"mode":"pointer_touch","status":"observed","journey_ids":["JOURNEY-001"],"evidence_ids":["EVID-001"],"limitations":[]},
            {"mode":"keyboard","status":"observed","journey_ids":["JOURNEY-001"],"evidence_ids":["EVID-001"],"limitations":[]}
        ],
        "state_coverage":[{"state":"focus","status":"observed","journey_ids":["JOURNEY-001"],"evidence_ids":["EVID-001"],"limitations":[]}],
        "material_limitations":[],
        "validator":{"name":"validate_ux_ui_teardown.py","status":"passed","validated_at":"2026-10-05"}
    }
    return findings,coverage

def write_fixture(root, f=None, c=None):
    findings,coverage=fixture()
    if f is not None: findings=f
    if c is not None: coverage=c
    (root/"findings.json").write_text(json.dumps(findings,indent=2),encoding="utf-8")
    (root/"coverage.json").write_text(json.dumps(coverage,indent=2),encoding="utf-8")

class ValidatorTests(unittest.TestCase):
    def test_valid_fixture(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p); self.assertEqual(validate(p),[])
    def test_aesthetic_cannot_be_high(self):
        f,c=fixture(); f["findings"][0]["judgment_basis"]="aesthetic_preference"; f["findings"][0]["severity"]="high"; f["findings"][0]["standard_refs"]=[]
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p,f,c)
            self.assertTrue(any("aesthetic_preference" in e for e in validate(p)))
    def test_standard_requires_reference(self):
        f,c=fixture(); f["findings"][0]["standard_refs"]=[]
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p,f,c)
            self.assertTrue(any("requires standard_refs" in e for e in validate(p)))
    def test_complete_rejects_open_limitation(self):
        f,c=fixture(); c["material_limitations"]=[{"id":"LIMIT-001","description":"No screen-reader run","status":"open","completion_requirement":"run it","affected_module_ids":["accessibility_semantics_keyboard"]}]
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p,f,c)
            self.assertTrue(any("open material limitations" in e for e in validate(p)))
    def test_complete_requires_keyboard(self):
        f,c=fixture(); c["input_modes"]=c["input_modes"][:1]
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p,f,c)
            self.assertTrue(any("pointer_touch and keyboard" in e for e in validate(p)))
    def test_renderer_is_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p)
            a=render_handoff.render(p); b=render_handoff.render(p); self.assertEqual(a,b)
    def test_malformed_nested_value_returns_error_not_exception(self):
        f,c=fixture(); f["findings"][0]["dependencies"]=[{}]
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p,f,c)
            errors=validate(p); self.assertTrue(errors)

if __name__=="__main__":
    unittest.main()
