from __future__ import annotations
import copy, json, tempfile, unittest
from pathlib import Path
import render_handoff
from validate_ux_ui_teardown import validate, MODULES, ACCESS


def fixture():
    evidence = [
        {"id":"EVID-001","evidence_class":"interaction_reproduction","title":"Primary journey run","locator":"local://run-1","accessed_at":"2026-10-05","volatile":False,"summary":"Primary quote journey reproduced at mobile and desktop with pointer and keyboard.","limitations":[]},
        {"id":"EVID-002","evidence_class":"standard_reference","title":"WCAG 2.2","locator":"https://www.w3.org/TR/WCAG22/","accessed_at":"2026-10-05","volatile":False,"summary":"Applicable accessibility baseline.","limitations":[]},
    ]
    findings = {
        "schema_version":"ux-ui-teardown-v1",
        "audit":{"project_name":"Fixture","project_locator":"repo://fixture","audited_revision":"abc123","production_locator":"https://example.test","production_revision_status":"verified","audit_start_date":"2026-10-05","audit_end_date":"2026-10-05","review_status":"complete","project_type":"web_app","primary_user_groups":["customer"],"primary_goals":["request a quote"]},
        "evidence_sources":evidence,
        "journeys":[{"id":"JOURNEY-001","title":"Request quote","user_group":"customer","trigger":"needs service","intended_outcome":"submit request","criticality":"primary","entry_points":["home"],"steps":["open home","choose quote","submit"],"required_states":["default","focus","validation","success"],"viewport_ids":["VIEW-001","VIEW-002"],"input_modes":["pointer_touch","keyboard"],"evidence_ids":["EVID-001"],"status":"passed","limitations":[]}],
        "findings":[{"id":"UXUI-001","title":"Focus state is not visually distinguishable","kind":"gap","domains":["accessibility.focus"],"status":"open","severity":"high","confidence":"confirmed","verification_state":"observed","judgment_basis":"standard_requirement","standard_refs":["WCAG 2.2 2.4.7 Focus Visible"],"journey_ids":["JOURNEY-001"],"surface_targets":["quote button"],"evidence_ids":["EVID-001","EVID-002"],"observed_condition":"Keyboard focus on the primary quote control has no visible indicator.","desired_condition":"Keyboard focus is clearly visible.","user_consequence":"Observed keyboard navigation does not expose current focus on the primary action.","business_risk":"Keyboard users can lose position before the primary conversion action.","recommendation":"Provide a visible focus treatment that remains distinguishable across supported backgrounds.","acceptance_criteria":["Primary quote control has a visible focus indicator"],"verification_methods":["Keyboard-run the primary journey"],"implementation_targets":["components/QuoteButton"],"preservation_constraints":[],"dependencies":[],"conflicts":[],"non_goals":["visual rebrand"]}]
    }
    modules = []
    for mid in sorted(MODULES):
        modules.append({"id":mid,"materiality":"high" if mid in {"accessibility_semantics_keyboard","interaction_affordance_feedback"} else "medium","status":"failed" if mid=="accessibility_semantics_keyboard" else "passed","finding_ids":["UXUI-001"] if mid=="accessibility_semantics_keyboard" else [],"evidence_ids":["EVID-001"],"limitations":[]})
    coverage = {
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
        "state_coverage":[
            {"id":"STATE-001","state":"default","label":"Quote entry ready","journey_id":"JOURNEY-001","step":"open home","surface_target":"quote entry","trigger":"page loaded","status":"observed","viewport_ids":["VIEW-001","VIEW-002"],"input_modes":["pointer_touch","keyboard"],"evidence_ids":["EVID-001"],"finding_ids":[],"limitations":[]},
            {"id":"STATE-002","state":"focus","label":"Primary quote button focused","journey_id":"JOURNEY-001","step":"choose quote","surface_target":"quote button","trigger":"keyboard Tab reaches primary action","status":"observed","viewport_ids":["VIEW-001","VIEW-002"],"input_modes":["keyboard"],"evidence_ids":["EVID-001"],"finding_ids":["UXUI-001"],"limitations":[]},
            {"id":"STATE-003","state":"validation","label":"Required-field correction","journey_id":"JOURNEY-001","step":"submit","surface_target":"quote form","trigger":"submit incomplete form","status":"observed","viewport_ids":["VIEW-001","VIEW-002"],"input_modes":["pointer_touch","keyboard"],"evidence_ids":["EVID-001"],"finding_ids":[],"limitations":[]},
            {"id":"STATE-004","state":"success","label":"Quote request accepted","journey_id":"JOURNEY-001","step":"submit","surface_target":"quote confirmation","trigger":"submit valid form","status":"observed","viewport_ids":["VIEW-001","VIEW-002"],"input_modes":["pointer_touch","keyboard"],"evidence_ids":["EVID-001"],"finding_ids":[],"limitations":[]}
        ],
        "material_limitations":[],
        "validator":{"name":"validate_ux_ui_teardown.py","status":"passed","validated_at":"2026-10-05"}
    }
    return findings, coverage


def write_fixture(root, f=None, c=None):
    findings,coverage=fixture()
    if f is not None: findings=f
    if c is not None: coverage=c
    (root/"findings.json").write_text(json.dumps(findings,indent=2),encoding="utf-8")
    (root/"coverage.json").write_text(json.dumps(coverage,indent=2),encoding="utf-8")


class ValidatorTests(unittest.TestCase):
    def run_errors(self, f, c):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p,f,c); return validate(p)

    def test_valid_fixture(self):
        f,c=fixture(); self.assertEqual(self.run_errors(f,c),[])

    def test_aesthetic_cannot_be_high(self):
        f,c=fixture(); f["findings"][0]["judgment_basis"]="aesthetic_preference"; f["findings"][0]["severity"]="high"; f["findings"][0]["standard_refs"]=[]
        self.assertTrue(any("aesthetic_preference" in e for e in self.run_errors(f,c)))

    def test_standard_requires_reference(self):
        f,c=fixture(); f["findings"][0]["standard_refs"]=[]
        self.assertTrue(any("requires standard_refs" in e for e in self.run_errors(f,c)))

    def test_complete_rejects_open_limitation(self):
        f,c=fixture(); c["material_limitations"]=[{"id":"LIMIT-001","description":"No screen-reader run","status":"open","completion_requirement":"run it","affected_module_ids":["accessibility_semantics_keyboard"]}]
        self.assertTrue(any("open material limitations" in e for e in self.run_errors(f,c)))

    def test_complete_requires_keyboard_on_material_journey(self):
        f,c=fixture(); c["input_modes"][1]["journey_ids"]=[]
        self.assertTrue(any("JOURNEY-001" in e and "input modes" in e for e in self.run_errors(f,c)))

    def test_complete_requires_mobile_and_desktop_on_material_journey(self):
        f,c=fixture(); c["viewports"][0]["journey_ids"]=[]
        self.assertTrue(any("JOURNEY-001" in e and "viewport classes" in e for e in self.run_errors(f,c)))

    def test_complete_requires_every_declared_state(self):
        f,c=fixture(); c["state_coverage"]=[row for row in c["state_coverage"] if row["state"]!="validation"]
        self.assertTrue(any("missing observed required states" in e and "validation" in e for e in self.run_errors(f,c)))

    def test_state_instance_references_are_validated(self):
        f,c=fixture(); c["state_coverage"][0]["journey_id"]="JOURNEY-999"
        self.assertTrue(any("STATE-001.journey_id" in e for e in self.run_errors(f,c)))

    def test_duplicate_state_ids_rejected(self):
        f,c=fixture(); duplicate=copy.deepcopy(c["state_coverage"][0]); duplicate["label"]="Second default instance"; c["state_coverage"].append(duplicate)
        self.assertTrue(any("state_coverage duplicate id" in e for e in self.run_errors(f,c)))

    def test_multiple_same_class_state_instances_are_allowed(self):
        f,c=fixture()
        c["state_coverage"].append({"id":"STATE-005","state":"validation","label":"Server-side validation retry","journey_id":"JOURNEY-001","step":"submit","surface_target":"quote form","trigger":"server rejects submission","status":"observed","viewport_ids":["VIEW-001"],"input_modes":["pointer_touch"],"evidence_ids":["EVID-001"],"finding_ids":[],"limitations":[]})
        self.assertEqual(self.run_errors(f,c),[])

    def test_state_viewport_must_link_back_to_journey(self):
        f,c=fixture(); c["viewports"][0]["journey_ids"]=[]
        errors=self.run_errors(f,c)
        self.assertTrue(any("STATE-001 viewport VIEW-001 is not linked" in e for e in errors))

    def test_renderer_is_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t); write_fixture(p)
            a=render_handoff.render(p); b=render_handoff.render(p); self.assertEqual(a,b)

    def test_malformed_nested_value_returns_error_not_exception(self):
        f,c=fixture(); f["findings"][0]["dependencies"]=[{}]
        self.assertTrue(self.run_errors(f,c))

    def test_malformed_state_row_returns_error_not_exception(self):
        f,c=fixture(); c["state_coverage"][0]["viewport_ids"]=[{}]
        self.assertTrue(self.run_errors(f,c))


if __name__=="__main__":
    unittest.main()
