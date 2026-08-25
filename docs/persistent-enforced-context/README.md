# Persistent & Enforced Context

Persistent AI behavior needs an architecture, not a bigger prompt.

This guide separates six layers that are often collapsed into one oversized instruction file. It preserves both ready-to-use configurations and the reasoning needed to revise them when model behavior or platform capabilities change.

## Start here

| Layer | Canonical document | What belongs there |
| --- | --- | --- |
| **CORE** | [Core epistemic and interaction contract](core.md) | Platform-agnostic calibration, unsupported-intent protection, anti-sycophancy, direct interaction, and the cross-domain quality standard. |
| **CODING** | [Coding-agent contract](coding.md) | Engineering workflow, root-cause diagnosis, tool and change discipline, validation, and release authority. |
| **USER CONTEXT** | [User context and memory](user-context.md) | Stable facts, preferences, and causal context that help interpret instructions; not the behavioral source of truth. |
| **PROJECT KERNEL** | [Minimal project kernel](project-kernel.md) | The few invariants worth repeating when a platform's project-local surface can displace global guidance. |
| **PLATFORM IMPLEMENTATIONS** | [ChatGPT, Claude Code, Codex, and desktop surfaces](platform-implementations.md) | Where each layer belongs on each platform, how inheritance differs, and which desktop surface uses which configuration. |
| **BEHAVIORAL REGRESSION TESTS** | [Regression suite](behavioral-regression-tests.md) | Reusable adversarial cases, execution protocol, scoring, and comparison gates. |

The current paste-ready ChatGPT Custom Instructions and Memory Summary live in [Ready-to-use ChatGPT configuration](chatgpt-configuration.md).

## The architecture

Different information belongs in different persistence mechanisms:

```text
Behavioral invariant
    -> instruction surface

Stable user/context fact
    -> memory

Project-specific rule
    -> project instruction

Long reference/rationale
    -> project source / repository documentation

Engineering operating policy
    -> coding-agent instructions

Historical conversation
    -> retrieval / episodic memory
```

These surfaces are not interchangeable:

- **Instructions** state how the system should reason, respond, or act.
- **Memory** carries useful context forward and may be synthesized, reprioritized, or updated by the product.
- **Project instructions** state rules that apply only to one project. Their relationship to global instructions is platform-specific.
- **Project sources** provide specifications, evidence, examples, and long rationale for retrieval. A source file is not a reliable substitute for an instruction surface.
- **Historical or episodic retrieval** finds prior conversations or records on demand. It supplies evidence and provenance, not an always-loaded behavioral contract.

The word **enforced** needs one boundary: model-facing instructions influence behavior but do not create a hard technical guarantee. If an action must be impossible regardless of model judgment, use the platform's deterministic controls—permissions, policies, hooks, sandboxing, or application code—where available. The architecture here makes behavioral guidance persistent and testable; it does not relabel prose as an access-control system.

## Why not one giant prompt?

A rule buried among hundreds of unrelated rules competes with them for attention. Longer files consume scarce context, increase the chance of conflict, and make it harder to tell which instruction caused a behavior. Splitting one giant file into imports may improve maintenance while leaving runtime dilution unchanged if every import is still loaded.

The resulting design rules are:

- keep global invariants concise;
- move domain-specific policy to the surface where it applies;
- keep project kernels short;
- avoid duplication when global and project instructions already stack;
- repeat only the invariants a platform's override behavior could otherwise displace; and
- keep long reasoning near the configuration without forcing all of it into every model context.

Longer is not automatically stronger. Concision is not an excuse to delete the causal reasoning that makes a rule generalize.

## From failure to a maintained configuration

Use this flow for every material rule:

```text
FAILURE
    -> WHY IT FAILED
    -> GENERAL PRINCIPLE
    -> PLATFORM-SPECIFIC CONSTRAINT
    -> RESULTING CONFIGURATION
    -> HOW TO TEST IT
```

The unsupported-intent rule demonstrates the full chain:

1. **Failure:** a build-planner research request received an unsolicited assurance that interaction patterns would be used "without stealing branding," although the user never proposed stealing anything.
2. **Why it failed:** the model invented suspect intent, answered that invention, and drifted away from the real task.
3. **General principle:** never add motives, premises, or corrective framing that the evidence and request do not support.
4. **Platform constraint:** the rule belongs in an instruction surface; the user's reason for caring belongs in user context; long analysis belongs in documentation or sources.
5. **Configuration:** put the full rule in [CORE](core.md), reinforce the trust consequence in [USER CONTEXT](user-context.md), and deploy it through the relevant [platform surface](platform-implementations.md).
6. **Test:** run [Unsupported intent](behavioral-regression-tests.md#1-unsupported-intent), [Unsupported corrective framing](behavioral-regression-tests.md#2-unsupported-corrective-framing), [Invented premise](behavioral-regression-tests.md#7-invented-premise), and [Reflexive disclaimer](behavioral-regression-tests.md#8-reflexive-disclaimer).

## Why a concise rationale can help

A blacklist can suppress the words it names while missing the same failure in a new form. A short causal sentence—such as “inventing unsupported intent creates strawmen, reduces epistemic accuracy, and derails the task”—gives the model a principle it can apply to unseen phrasing.

Rationale helps when it:

- identifies the mechanism or consequence;
- resolves ambiguity in the rule;
- supports generalization beyond listed examples; and
- stays short enough not to compete with the instruction.

Rationale hurts when it introduces exceptions, repeats the rule in several weaker forms, primes irrelevant failure scenarios, or becomes an essay inside the always-loaded prompt. Preserve the long reasoning here; carry only the minimum useful cause into the runtime contract.

## Source disposition

This architecture was extracted from real global `CLAUDE.md` and `AGENTS.md` configurations plus the incidents and tests that shaped them. The original files are source evidence, not files to copy blindly:

- machine state and private paths stay in local machine or project context;
- persistent epistemic and interaction policy becomes CORE;
- engineering workflow becomes CODING;
- stable user facts and the reasons behind preferences become USER CONTEXT; and
- the cross-domain quality standard stays in CORE rather than being misclassified as coding-only policy.

The original machine-specific files are intentionally not reproduced in this public repository. Copying them would publish local details, create a misleading one-size-fits-all configuration, and—in the case of a nested file literally named `AGENTS.md`—could change how Codex behaves while editing these docs. Their relevant principles are preserved in the canonical layers above.

## Maintenance rule

When a canonical instruction changes:

1. record the concrete failure or new platform constraint;
2. change the single canonical layer that owns the rule;
3. update platform composition only where inheritance requires it;
4. run the [behavioral regression suite](behavioral-regression-tests.md) against the current and candidate configurations; and
5. adopt the revision only when the evidence supports improvement without a material regression.

Do not accept model self-assessment—"these instructions should work better"—as validation. Observable behavior under controlled tests outranks the model's description of its own likely behavior.
