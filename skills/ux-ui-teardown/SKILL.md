---
name: ux-ui-teardown
description: Perform a read-only, evidence-led UX/UI teardown of a website or application by tracing real user journeys, interaction states, responsive behavior, accessibility, visual hierarchy, trust, and design-system consistency into a validated implementation-ready handoff.
---

# UX/UI Teardown

Evaluate the experience people actually receive, not the design the project intended to ship.

This skill is a read-only investigation. It uses the product like a real user, inspects the implementation where available, distinguishes standards from heuristics and taste, traces complete journeys across states and inputs, and produces a deterministic handoff that `ux-ui-revision` can consume.

## Operating contract

- Do not change the audited product, repository, CMS, design file, production environment, analytics, or public surface.
- Audit journeys, not isolated screenshots. A page can look polished while the actual task flow is confusing or broken.
- Inspect both rendered behavior and source when available. Neither alone proves the other.
- Treat accessibility as part of UX, not a detached compliance appendix.
- Separate standards, observed user-impact evidence, heuristics, conventions, and aesthetic preference. Do not promote taste into a high-severity finding.
- Keep `severity`, `confidence`, and `verification_state` separate.
- Do not claim user confusion, trust loss, conversion lift, or business impact as observed unless actual user or first-party evidence exists. Otherwise state the consequence as a reasoned risk.
- Preserve strengths. A teardown that only finds defects is incomplete when the product has useful interaction patterns, recognizable hierarchy, effective copy, or accessible components worth protecting.
- Record every material unknown. Lack of access is a limitation, not permission to infer a result.
- Treat automated accessibility, lint, performance, and screenshot tools as evidence sources, not final adjudicators.
- Never invent personas, user research, analytics, device coverage, browser results, or assistive-technology outcomes.

Read before auditing:

- [audit-methodology.md](references/audit-methodology.md)
- [evidence-and-standards.md](references/evidence-and-standards.md)
- [report-contract.md](references/report-contract.md)
- [forward-testing.md](references/forward-testing.md) when changing or evaluating this skill

## 1. Establish scope and baseline

Record:

- project name and locator;
- immutable source revision when available;
- production locator and whether production/source alignment is verified;
- project type and primary user groups;
- primary and secondary user goals;
- available source, production, analytics, research, design-system, and accessibility evidence;
- audit window and material access limitations.

Do not infer production/source alignment from visual similarity.

## 2. Build the journey map before judging screens

Identify the smallest set of journeys that represent the product's real value and risk.

For each journey define:

- actor or user group;
- trigger;
- intended outcome;
- entry points;
- ordered steps;
- decision points;
- destructive or irreversible actions;
- required feedback;
- success state;
- empty, loading, validation, error, permission, offline, timeout, and recovery states where applicable;
- responsive and input-mode exposure;
- business criticality.

Prefer actual product flows over imagined happy paths.

## 3. Exercise representative states

For each material journey, inspect the states that can change comprehension or task completion:

- initial / default;
- hover where applicable;
- focus;
- active / pressed;
- disabled;
- selected / expanded;
- loading / skeleton / progress;
- empty;
- validation;
- error;
- success / confirmation;
- destructive confirmation and undo/recovery;
- permission denied;
- offline / timeout / retry;
- long content / localization stress when material.

A component that works only in its default state is not verified.

## 4. Test responsive behavior and input modes

For web products, include at minimum:

- narrow mobile;
- wide mobile or small tablet when layout materially changes;
- desktop.

Also inspect relevant zoom/reflow behavior when accessibility or dense layout is material.

Exercise:

- pointer/touch;
- keyboard;
- assistive-technology semantics where tooling/access allows;
- platform-native gestures only when the product depends on them.

Do not call a layout responsive because it avoids horizontal scrolling. Verify hierarchy, navigation, task order, target access, disclosures, sticky/fixed UI, overlays, virtual keyboards, and state visibility.

## 5. Evaluate the ten UX/UI modules

Audit all applicable modules:

1. `orientation_comprehension`
2. `information_architecture_navigation`
3. `interaction_affordance_feedback`
4. `task_flow_forms_recovery`
5. `responsive_adaptive_layout`
6. `accessibility_semantics_keyboard`
7. `visual_hierarchy_legibility`
8. `trust_conversion`
9. `design_system_consistency`
10. `performance_perception`

Use the facet list and completion rules in [report-contract.md](references/report-contract.md).

## 6. Classify evidence before writing findings

Use these judgment bases:

- `standard_requirement`
- `observed_behavior`
- `user_research`
- `first_party_measurement`
- `heuristic`
- `design_system_convention`
- `aesthetic_preference`

Use standards only when the standard actually applies. WCAG and ARIA claims must identify the relevant criterion/pattern or concrete requirement.

Heuristics identify probable usability problems; they do not prove a user failed.

Design-system conventions are context-sensitive. Apple, Material, GOV.UK, platform conventions, and project design systems can inform judgment without becoming universal requirements.

Aesthetic preference is valid only as low-severity polish unless independent evidence establishes a stronger consequence.

## 7. Create findings with consequence and proof boundaries

Every finding must include:

- observed condition;
- desired condition;
- journey and surfaces affected;
- concrete user consequence or reasoned risk;
- evidence and judgment basis;
- severity, confidence, and verification state;
- acceptance criteria;
- verification methods;
- implementation targets when source is available;
- preservation constraints;
- dependencies/conflicts;
- explicit non-goals.

Do not write findings such as "make this more modern", "CTA should pop", or "add more whitespace" without a bounded user or system consequence.

Use strengths for patterns that revision must preserve.

## 8. Reconcile coverage honestly

A comprehensive audit requires evidence that the material modules, journeys, states, viewports, and input modes were actually exercised.

`complete` is allowed only when:

- every defining/high-materiality module is passed or failed rather than blocked/not-tested;
- every primary journey has at least one completed journey run;
- required viewport/input coverage is present;
- available work is completed;
- no open material limitation prevents a material conclusion;
- production alignment is verified when public production state is part of the verdict.

Otherwise use `provisional`.

## 9. Produce the canonical handoff

Create:

```text
ux-ui-teardown/
├── README.md                    # generated
├── findings.json                # canonical
├── coverage.json                # canonical
├── findings.md                  # generated
├── journey-map.md               # generated
├── coverage.md                  # generated
└── evidence/
```

`findings.json` and `coverage.json` are authoritative.

Render:

```bash
python3 <skill-directory>/scripts/render_handoff.py <ux-ui-teardown-directory>
```

Validate:

```bash
python3 <skill-directory>/scripts/validate_ux_ui_teardown.py <ux-ui-teardown-directory>
```

Fix every validation error. Validator success proves structural/semantic contract compliance, not that the auditor's judgment is automatically good.

## Handoff

Report:

1. exact audited revision/environment;
2. review status and material limitations;
3. primary journeys and coverage;
4. severity-ordered findings and retained strengths;
5. accessibility/keyboard findings with standard references where applicable;
6. responsive/input/state gaps;
7. exact owner decisions or research needs, if any;
8. canonical artifact path and validator result;
9. what remains unverified.
