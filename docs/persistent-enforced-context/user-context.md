# USER CONTEXT — Facts, Preferences, and Rationale

USER CONTEXT contains durable information that helps a model interpret a person or working relationship. It is not an instruction dump and not the behavioral source of truth.

## Memory and instructions are different

An instruction says what the system should do:

> Match confidence to evidence.

User context explains why that behavior matters and how to interpret the preference:

> False confidence can misallocate years of effort, so calibration matters more than reassurance.

The first belongs in [CORE](core.md) and the platform's instruction surface. The second belongs in memory or user context. Repeating an especially important concern in both can be appropriate because each copy serves a different function: one directs behavior; the other supplies causal and interpretive context.

Memory should not be the only home for a hard behavioral requirement. Products may synthesize, reprioritize, update, or selectively retrieve memory. A rule that must guide every response belongs in the strongest available instruction surface; if it must be technically guaranteed, it belongs in deterministic controls rather than prose.

## Canonical user-context content

Adapt the nouns and details to the actual user, but preserve the distinction between fact and command:

- Epistemic calibration matters because false confidence can waste years of effort, money, or attention.
- Favorable conclusions may be stress-tested because warrant matters more than emotional valence.
- Skepticism does not imply a preference for negative answers; supported positive and negative judgments are both useful.
- Unsupported motive attribution, invented premises, strawmen, reflexive disclaimers, and corrective framing against claims never made materially damage trust.
- The user wants observable results separated from inference and model evaluation.
- Direct disagreement is useful when warranted; position changes should follow new evidence or better reasoning.
- Intellectual honesty matters more than reassurance or confidence theater.

These statements provide context. They do not replace the operational rules in CORE.

## What belongs here

- stable preferences and communication sensitivities;
- long-lived goals, roles, constraints, and relevant background;
- the reason a behavioral preference matters;
- facts that improve interpretation across otherwise unrelated conversations; and
- durable distinctions such as “skeptical does not mean negative answers are preferred.”

## What does not belong here

- large engineering workflows;
- repository-specific build commands;
- long specifications or research reports;
- temporary task state;
- a transcript used as the only record of a decision;
- secrets, credentials, or facts the user does not want persisted; or
- a behavioral command that has no canonical copy in an instruction surface.

Long material belongs in project sources or repository documentation. Project-specific rules belong in project instructions. Historical conversation belongs in searchable or episodic retrieval so the original evidence can be recovered when a summary is insufficient.

## ChatGPT implementation

The canonical, ready-to-paste ChatGPT Memory Summary is in [Ready-to-use ChatGPT configuration](chatgpt-configuration.md#memory-summary). It applies to ChatGPT Chat and Work, including those surfaces in the desktop app; it is not the memory or instruction mechanism for a Codex coding session. It deliberately describes durable context and rationale rather than trying to smuggle the entire behavioral contract into memory.

Evaluate memory changes alongside the instruction configuration. A memory rewrite can alter behavior even when Custom Instructions are unchanged, so record both during [behavioral regression testing](behavioral-regression-tests.md).
