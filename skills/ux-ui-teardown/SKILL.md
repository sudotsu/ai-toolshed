---
name: ux-ui-teardown
description: Perform a read-only UX/UI teardown centered on visual craft, real user experience, contextual engagement, and evidence-based competitor calibration, producing a validated implementation-ready handoff without changing the audited product.
---

# UX/UI Teardown

Evaluate the experience a real person receives: what they see, what they understand, what feels intentional or off, whether the product pulls them forward, where journeys break, and how the result compares with legitimately selected competitors.

The center of this skill is **not compliance machinery**. The center is the product experience.

Use three primary lenses together:

1. **UI craft** — literal visual quality: composition, color, typography, spacing, hierarchy, consistency, responsive presentation, imagery, density, interaction polish, motion, and visual anomalies.
2. **UX experience** — what it is like to use: orientation, journey logic, friction, feedback, progress, recovery, engagement quality, effort/payoff, relevance, trust, momentum, autonomy, and whether a person would want to continue.
3. **Competitive calibration** — compare against relevant competitors selected with current evidence. Compare patterns and outcomes; never copy their design.

Accessibility/readability is a supporting quality dimension. It includes contrast, legibility, focus, keyboard behavior, target usability, semantics, and assistive-technology checks when material. Do not let deep accessibility testing displace the main UI/UX investigation unless the product, owner, audience, or observed risk makes it material.

## Operating rules

- Read only. Do not change the audited product, repository, CMS, design file, production environment, analytics, ads, profiles, or public content.
- Use the product like a real user. Source inspection cannot replace rendered experience.
- Audit journeys, not screenshots in isolation.
- Match the method to the question. Rendered inspection, cognitive walkthrough, analytics, user research, automated measurement, and competitive evidence answer different questions; do not pretend one substitutes for all the others.
- Treat project context as evidence. A five-question guided flow can be excellent for a high-consideration service and terrible for a tiny transaction.
- Do not optimize mechanically for fewer clicks, more clicks, or more engagement. Judge whether effort is justified by relevance, clarity, progress, and payoff.
- Treat participation as valuable only when it reduces later complexity, improves relevance, or creates meaningful progress without feeling like busywork.
- Separate observed facts, measured comparison, behavioral analytics, user research/sentiment, standards, heuristics, visual-craft judgment, and taste.
- Do not claim that users "feel" something as observed unless user research/sentiment evidence supports it. You may state a bounded inference such as "likely to read as..." and explain why.
- Preserve strengths. A teardown that only finds defects is incomplete.
- Never invent analytics, research, competitor status, rankings, market position, browser/device coverage, performance measurements, eye-tracking/attention results, or assistive-technology outcomes.

Read before auditing:

- [audit-methodology.md](references/audit-methodology.md)
- [experience-and-visual-craft.md](references/experience-and-visual-craft.md)
- [competitive-benchmarking.md](references/competitive-benchmarking.md)
- [report-contract.md](references/report-contract.md)
- [forward-testing.md](references/forward-testing.md) when changing this skill

## 1. Establish product and audience context

Record the project, immutable revision when available, production alignment, project type, audience scope (`local|regional|national|global|mixed|internal`), primary users, goals, and owner-supplied context.

Explicitly identify context that changes UX judgment:

- stakes and risk of the task;
- expected frequency and urgency;
- likely user knowledge;
- expected effort tolerance;
- whether personalization can actually alter the result;
- local/human specificity versus global consistency/localization needs;
- constraints the owner already knows that a generic heuristic would miss.

Do not assume the same interaction is good because it worked on another project.

## 2. Choose evidence and escalation before judging

Inventory the evidence actually available for the question at hand: rendered product, source, first-party analytics, user research, user sentiment, design-system evidence, automated measurements, and competitor measurements/observations.

Use the strongest relevant evidence that is actually available:

- **Rendered behavior** answers what the interface currently does and looks like.
- **First-party behavioral evidence** answers what people actually do at scale: task completion, drop-off, path deviations, repeated/missed clicks, errors, abandonment, device/segment differences, and—when available—funnels, session replay, heatmaps/zoning, error telemetry, and speed measurements.
- **User research** answers why people act that way and what they understand, expect, trust, prefer, enjoy, dislike, or misunderstand. Use representative task-based research when the decision materially depends on those questions.
- **Automated measurement** can support performance, accessibility, and visual-attention questions, but is evidence rather than final judgment.
- **Heuristics/cognitive walkthroughs** are useful for likely usability risks when real behavior data is absent; label the resulting confidence accordingly.

Do not require analytics or user testing for every audit. Require them only when the conclusion materially depends on evidence the audit cannot otherwise possess. If a high-stakes conclusion about motivation, comprehension, preference, trust, satisfaction, or real-world behavior cannot be supported, keep that conclusion provisional or create an investigation finding instead of manufacturing certainty.

For web performance that affects experience, use real measurements such as field/lab loading, responsiveness, and visual-stability data when available; deep performance engineering remains outside this skill, but the user-visible consequence is in scope.

Predictive attention/eye-tracking tools may be used to test first-impression hierarchy when available. Treat them as measurement evidence, not proof of comprehension or preference.

## 3. Select competitors with evidence

For public/commercial products, competitive calibration is required by default unless there is a concrete reason it is not useful.

Select competitors from current measurement appropriate to the market, such as:

- search/category visibility and query overlap;
- traffic or audience estimates;
- review volume/quality and local prominence;
- app-store/category rank;
- market share, usage, customer count, or credible industry data;
- direct owner-supplied competitors, **after** separately establishing whether they are benchmark leaders.

A competitor is not "top" because the model remembers the name.

For a complete audit that requires competitive calibration, use at least two competitors with measured selection evidence. If measurement is unavailable, keep the audit provisional rather than guessing.

Comparison asks what the best relevant products do differently and why it may work. **Do not copy layouts, copy, branding, illustrations, or interaction details.** Extract principles and opportunities.

## 4. Build material journeys

Identify the smallest set of journeys representing real value and risk.

For each journey capture:

- user and trigger;
- intended outcome;
- steps and decision points;
- effort budget (`low|moderate|high|contextual`);
- engagement intent;
- expected payoff for the effort requested;
- context notes explaining why the flow is appropriate for this product;
- loading, validation, error, success, destructive, timeout, empty, and recovery states that materially affect it;
- responsive exposure and input modes.

A journey can be technically functional and still be bad UX.

When behavioral analytics or task-test data exists, compare the modeled journey with observed paths. Look for unexpected detours, abandonment, misclick/retry patterns, repeated scrolling, error clusters, and device/segment differences. Do not infer intent from behavior alone when several explanations fit.

## 5. Run the UI craft pass

Inspect rendered surfaces at representative widths. Deliberately hunt for things that look unintentionally wrong, weak, inconsistent, generic, or out of place.

Evaluate at minimum:

- color system and surface/background relationships;
- typography, line length, hierarchy, and density;
- composition, alignment, spacing rhythm, container widths, and visual balance;
- CTA prominence and competition between elements;
- imagery, cropping, icon style, illustration consistency, and media quality;
- borders, radii, shadows, cards, section transitions, and component-family coherence;
- interaction polish: hover/press/focus/selected states, transition timing, perceived latency, loading feedback, and whether motion clarifies or distracts;
- desktop/mobile consistency without requiring identical layout;
- dead zones, cramped areas, accidental asymmetry, awkward wrapping, and visually weak sections;
- template-like or AI-generated sameness versus intentional specificity;
- audience fit: local/human specificity when appropriate, and globally credible consistency/localization when appropriate;
- for global/mixed audiences when material: language expansion, truncation, date/number/currency/time-zone presentation, locale assumptions, and RTL/layout resilience;
- perceived performance and visual stability where slow response, delayed feedback, or layout shift changes how the interface feels.

Distinguish **visual craft** from **aesthetic preference**. "I prefer purple" is taste. Broken spacing rhythm, incoherent palette structure, weak hierarchy, or mismatched component language are craft problems.

## 6. Run the UX experience pass

Use each material journey. Ask from the user's point of view:

- Do I immediately understand where I am and what I can do?
- Does each next step make sense?
- Is it pleasing, satisfying, or at least frictionless to navigate?
- Does the interface give useful feedback and a sense of progress?
- Does requested effort produce enough relevance or payoff?
- Do small interactions help me think about what I actually need, or just make me work?
- Is personalization real, or cosmetic funnel theater?
- Does the experience reduce generalized information I must sort through later?
- Do I hit dead ends, 404s, wrong destinations, lost state, nonsensical back behavior, missing mobile actions, or inconsistent information?
- Are recovery paths obvious and safe?
- Does the product feel intentional, specific, coherent, and appropriate for its audience rather than cookie-cutter or soulless?
- Does the interface respect user autonomy, or does it obscure choices, preselect business-favorable outcomes, manufacture urgency, make refusal/cancellation harder than acceptance, or otherwise create coercive/manipulative friction?
- Would the intended user have a reason to keep going?

Use the engagement model as a diagnostic, not a formula:

```text
effort -> feedback -> progress -> payoff
```

The user should not feel "here comes a challenge." When participation is good, the payoff is apparent before the effort registers as work.

Engagement is not automatically good. A pattern that increases time-on-task by trapping, pressuring, confusing, or repeatedly interrupting the user is a UX defect, not a success metric.

## 7. Calibrate against competitors, analytics, and user evidence

Compare the audited product against the measured competitor set on equivalent surfaces/journeys:

- first impression and orientation;
- visual hierarchy, color, typography, imagery, and overall craft;
- interaction quality and perceived responsiveness;
- amount and quality of effort requested;
- feedback/progress/payoff;
- trust and specificity;
- form and conversion-flow design;
- mobile experience;
- authenticity/distinctiveness versus generic patterns;
- where the audited product is already better.

When first-party behavioral evidence exists, use it to challenge the heuristic/rendered conclusions rather than cherry-picking confirmation. When public user sentiment or actual user research exists and is relevant, use it as evidence and retain disagreement between evidence sources instead of forcing a false consensus.

Do not systematize "feel" into a fake score. Use structured evidence to support human-readable judgment.

## 8. Accessibility/readability pass

Check core readability and operability without turning the audit into a compliance project:

- text contrast and legibility;
- readable sizing/line-height and zoom/reflow where material;
- touch/click target usability;
- visible focus and basic keyboard completion of representative interactive flows;
- semantics for custom controls;
- screen-reader/assistive-tech behavior when requested, materially risky, or readily testable and important to the product.

Use current applicable accessibility standards when making standards-based claims. Automated accessibility tools are evidence, not proof that the experience is accessible.

Serious accessibility failures can still be high severity. The point is proportional effort, not ignoring accessibility.

## 9. Run a challenge pass

Before finalizing, actively try to disprove the audit's important conclusions:

- Which finding is based on the weakest evidence?
- What strong existing behavior might the proposed change accidentally destroy?
- What did the audit probably miss because it followed the expected path?
- Do analytics, research, source, rendered behavior, and competitor evidence disagree anywhere?
- Is a supposedly "better" interaction actually more work with no downstream payoff?
- Is a recommendation optimizing a business metric at the user's expense?
- Is a visual judgment actually taste disguised as craft?
- Did local/global assumptions leak into a project where they do not belong?

When an independent evaluator/reviewer is practically available for a broad or high-stakes heuristic audit, use one and compare findings before convergence. A second pass by the same evaluator is useful but is **not** independent evidence; label it honestly.

## 10. Produce bounded findings

Every finding needs observable evidence, consequence, acceptance criteria, and verification methods.

Allowed judgment bases include `visual_craft`, `measured_comparison`, `observed_behavior`, `user_sentiment`, `user_research`, `first_party_measurement`, `standard_requirement`, `heuristic`, `design_system_convention`, `owner_context`, and `aesthetic_preference`.

Aesthetic preference alone cannot exceed low severity. Visual-craft judgment may be material when the problem is systemic or clearly affects hierarchy, comprehension, trust, coherence, or competitive quality, but visual craft alone cannot be critical.

## 11. Completion rules

A `complete` audit requires:

- defining UI-craft and UX-experience passes actually executed;
- every primary/high-risk journey exercised at material states;
- desktop and narrow-mobile coverage per material web journey, not merely somewhere in the site;
- rendered evidence for visual conclusions;
- representative keyboard/readability checks for interactive web products, without requiring screen-reader coverage by default;
- measured competitor calibration when the product requires it;
- any analytics/user-research evidence explicitly marked material to the conclusion either examined or represented as a material limitation;
- no blocked/partial access explicitly marked material to completion;
- no open material limitation;
- verified source/production alignment when the production experience is part of the verdict.

Otherwise mark the audit `provisional`.

## 12. Canonical handoff

Create:

```text
ux-ui-teardown/
├── findings.json
├── coverage.json
├── README.md
├── findings.md
├── journey-map.md
├── experience.md
├── benchmark.md
├── coverage.md
└── evidence/
```

Start a new handoff with the bundled scaffold, using the actual project values. The scaffold is deliberately `provisional` and contains an open limitation; replace its placeholders with observed evidence and coverage. Use [report-contract.md](references/report-contract.md) to author the JSON. Run the validator after writing; inspect validator source only when the contract or an error does not explain a field.

```bash
python3 <skill-directory>/scripts/bootstrap_teardown.py <ux-ui-teardown-directory> \
  --project-name '<name>' --project-locator '<source>' --audited-revision '<revision>' \
  --project-type <type> --audience-scope <scope> \
  --primary-user '<user>' --primary-goal '<goal>'
```

Validate and render:

```bash
python3 <skill-directory>/scripts/validate_ux_ui_teardown.py <ux-ui-teardown-directory>
python3 <skill-directory>/scripts/render_handoff.py <ux-ui-teardown-directory>
```

Validator success proves contract compliance, not that design judgment is automatically correct.
