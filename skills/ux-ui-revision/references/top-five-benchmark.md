# UX/UI skills: peer cohort and flagship evidence plan

Status: **benchmark incomplete**. Research snapshot: 2026-10-08. This document does not establish that either Toolshed skill is in the top five or performs at top-five quality.

## Compare the product that actually ships

`ux-ui-teardown` and `ux-ui-revision` are portable agent skills. Their direct comparison set should therefore be agent skills used to inspect, design, or improve digital interfaces under the same model, project access, and task brief. UX research platforms such as Baymard, UserTesting, Maze, Dscout, and Contentsquare remain useful sources of research practice. They are not direct peer skills, and their proprietary panels, analytics collection, or research corpora cannot be treated as capabilities these files have matched.

## Provisional peer cohort

These five public, current, inspectable agent-skill projects are a **test cohort**, not a verified ranking of the world's five best. They were selected for visible adoption or publisher credibility, active code, and complementary coverage of visual craft, UX review, and implementation. Popularity helps identify relevant peers; it does not establish quality. Reassess the cohort before a market-ranking claim.

| Peer, pinned source | Capability to test against | Selection limit |
| --- | --- | --- |
| [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/1a2c459b35f26116fd165b0a0f30597f252749ff) | Searchable design guidance, styles, palettes, type, UX rules, and implementation direction across stacks | Strong direct design-intelligence peer; its database size is not an outcome measure. |
| [Impeccable](https://github.com/pbakaus/impeccable/tree/778c8a7b71ccd5bfe3ca6ac68c15d9d872d0f87d) | Audit/critique, craft and polish workflows, browser iteration, deterministic frontend checks | Broadest visible audit-to-improvement peer; advertised rules require outcome testing. |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill/tree/b482f7a970abb98c4108d4a9f761e458c64cefc8) | Distinctive visual direction and redesign guidance | More creation focused than evidence-led audit. |
| [Anthropic frontend-design](https://github.com/anthropics/skills/tree/683bc88e56f3e09ba94f7055977f3d3aa499f202/skills/frontend-design) | Original widely distributed frontend craft skill | Focuses on generation; publisher prominence does not prove superior UX outcomes. |
| [Vercel web-design-guidelines](https://github.com/vercel-labs/agent-skills/tree/063bee94c3f4df8453406c830b0a7df0f2860278/skills/web-design-guidelines) | Structured web interface review against published guidelines | Narrower review scope; guideline coverage is not a complete revision workflow. |

The cohort deliberately spans review and creation because the Toolshed pair claims to do both diagnosis and improvement. Report each peer's supported role separately. Do not hide a peer's strength by scoring it only on an unsupported role, and do not credit Toolshed for breadth without judging the delivered result.

## Known gaps to test directly

UI/UX Pro Max supplies a searchable design corpus and design-system suggestions; Toolshed has no equivalent built-in reference library. Impeccable supplies a broad command vocabulary, live browser iteration, and deterministic frontend detectors; Toolshed has no equivalent detector suite. Taste Skill and Anthropic frontend-design are explicit about visual direction and new UI creation, whereas Toolshed's revision half starts from an existing teardown. Those differences may matter substantially for visual output and speed. The test must expose them rather than credit Toolshed's more detailed audit artifact as a substitute for a better interface.

## What must be demonstrated

The intended advantage is an evidence chain from observed issue through owner decision, change, rendered verification, and regression review. It must be judged on actual outputs, not on the presence of fields or instructions. Compare at least:

1. Finding accuracy, missed material issues, severity, and unsupported claims.
2. Visual craft judgment: composition, typography, color, imagery, responsive behavior, and distinctiveness.
3. Journey quality: task completion, feedback, recovery, effort and payoff, inclusive usability, and manipulative friction.
4. Use of behavioral and user evidence when the conclusion needs it.
5. Recommendation quality and risk of making the product worse.
6. Implementation quality, preservation of strengths, rendered verification, and new regressions.
7. Time, agent turns, tool use, artifact usability, installation friction, and runtime portability.

## Reproducible evaluation

Before running a candidate, record the project revision, test brief, permitted tools, model and version, runtime and version, candidate commit, install path, settings, and any unavailable evidence. Preserve the raw prompt, transcript, produced artifacts, screenshots or recordings, validator results, and reviewer notes. Keep all candidates on the same input and access budget; allow each skill to use its own intended workflow. A no-skill baseline helps distinguish a skill's contribution from the model's native ability.

Use a diversified set of real products and tasks: a high-consideration service flow, a low-friction transaction, commerce checkout, SaaS onboarding/core task, information-heavy navigation, and a mobile-dominant or localized experience. Include at least one case with genuine first-party behavior or user evidence. Record failures and abandoned runs. Do not tune the skill on held-out cases and then score those cases as independent evidence.

For each case, establish reference findings and desired outcomes **before** inspecting candidate results. Use qualified independent UX reviewers, real task observation, reliable existing research, or a combination. Blind reviewers to the candidate where practical. Score issue-level precision and recall, severity agreement, harmful recommendations, strength preservation, and whether implementation passes its acceptance criteria without regressions. Record disagreement and confidence. A second pass by the author or the same model is useful debugging, not independent ground truth.

Run the teardown and revision roles separately. For revision, provide the same validated starting findings and authorization to every candidate capable of implementation. Reinspect the resulting UI at the relevant viewports and states. A passed JSON validator is not proof that an intervention worked.

Use independent testbeds as additional evidence, with the benchmark labels hidden from every candidate. [UXBench at `15f87a9`](https://github.com/Jackwwj619/UXBench/tree/15f87a975cd5670533d8892b1395c9ba5a556eb5) has 41 runnable fixtures across ten interface families and a fixed downstream repair-and-score method for critique actionability. Adapt the Toolshed and peer outputs to its report contract before comparing them; do not treat its published model leaderboard as a score for these skills. [UIJudgeBench at `022f3b4`](https://github.com/gojiplus/uijudge-bench/tree/022f3b4e950dcbdce1ddd09d13cb4d1aa40c3f32) has auditable labels for accessibility, layout, localization and computed-style judgments. Its design-preference pilot pairs are not yet scored ground truth, so use it for defect detection rather than visual-taste superiority. Pin benchmark and data versions and preserve the prediction files. Neither testbed alone covers the full teardown-to-revision job.

## Current evidence and release decision

The PR has package/unit tests and two described forward smoke tests on OmahaTreeCare and TipJar. The PR does not contain preserved, independently scored peer runs or a blinded reference corpus. Thus it has **workflow viability evidence**, not demonstrated peer parity. The five projects above have not yet been run against the same cases in this repository.

A further isolated Codex CLI 0.161.0 / `gpt-6.1-sol` source-only TipJar smoke on revision `d2fb37e` produced a validated provisional handoff: seven findings, four explicitly untested journeys, and no rendered or competitor claims. It used 62,857 agent tokens. This is a useful evidence-discipline signal and an operational cost problem, not a quality benchmark. The bootstrap added after that run still needs its own runtime cost measurement; the raw agent transcript was not preserved, so this run cannot enter a reproducible peer scorecard.

Treat the pair as flagship only after: the reproducible comparison is complete; the two skill packages pass their correctness and runtime gates; independent review finds no unresolved material gap; and the observed results are at least competitive with the strongest applicable peers across the core dimensions above. If a peer wins a dimension, document the gap and either close it or state the narrower scope. Do not translate a green CI run, a good demo, or this cohort list into a top-five claim.
