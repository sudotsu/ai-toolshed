# Forward-Testing Protocol

Use this protocol when changing the skill contract or validator.

## Test selection

Use at least two materially different public-web project shapes, for example:

- A local-service site with location intent, Business Profile, calls/forms, reviews, and service-area constraints.
- A publisher, SaaS, tool, ecommerce, marketplace, or international product with materially different search journeys and vertical modules.

A repository plus production is preferred. Representative raw artifacts are acceptable when access is limited. Never modify the test project.

## Prompt discipline

Give each agent only the project locator, allowed access, read-only boundary, and request to use `seo-teardown`. Do not reveal expected findings, known defects, or scoring criteria inside the audit prompt.

## Evaluation rubric

Judge each output on:

- Applicable module activation and absence of irrelevant checklist work.
- Evidence-class discipline and freshness.
- Separation of eligibility, observation, first-party performance, inference, correlation, and theory.
- Qualified-business relevance.
- Useful findings versus false positives.
- Explicit unknowns, blockers, and provisional status.
- Finding specificity, reproduction, consequence, acceptance, and verification.
- Complete coverage and implementation ordering.
- Agreement between Markdown and JSON.
- Compatibility: two agents should produce structurally valid handoffs that a future revision skill can consume without agent-specific interpretation.

## Failure-driven improvement

Record failures before editing the skill. Prefer contract or validator improvements over adding project-specific expected answers. Do not encode known findings from test projects into prompts, references, examples, or fixtures.

Useful failure classes:

- Generic best-practice false positive.
- Unsupported ranking claim.
- Invented metrics or SERP state.
- Relevant module omitted.
- Irrelevant module forced.
- Blocked evidence hidden behind a complete verdict.
- Experiment inflated into a defect.
- Dependency or ordering ambiguity.
- Narrative action missing from the findings register.
- Structurally incompatible handoff between agents.

## Full behavioral forward tests

Schema fixtures and abbreviated handoffs test validator discipline but do not establish audit depth. Before claiming full forward testing:

1. Run the skill from a neutral prompt against two materially different deployed public-web products.
2. Audit repository and production at route, query, render, claim, entity, conversion, policy, and measurement levels.
3. Produce multiple project-specific defects, opportunities, blockers, and strengths where evidence warrants them; never impose a quota.
4. Require complete facet checks, concrete-or-evidenced-unavailable SERP winners, method-specific URL samples, production-revision status, deliberate non-pursuits, and revision-ready finding fields.
5. Critique the handoffs for missed material issues, generic false positives, evidence misuse, weak acceptance criteria, poor ordering, hidden gaps, and deterministic consumption.
6. Improve the reusable contract only for systemic failures, then migrate and revalidate both complete handoffs.

Do not describe an execution as full when it only demonstrates schema validity or contains token findings.
