# AI Toolshed quality bar

## Default standard

Reusable Toolshed work should be built only when there is a defensible path to matching or exceeding strong current performers in its domain on the dimensions that matter to the real task.

That does **not** mean maximizing feature count, copying market leaders, or making absolute superiority claims without evidence. It means:

- understand what the best current products, workflows, or expert practices actually do well;
- identify which of those dimensions are relevant to this contribution;
- cover important standard practices, failure modes, and missed opportunities;
- preserve useful differentiation instead of normalizing everything toward competitors;
- refuse to call work finished merely because it is internally consistent or technically valid.

Prototype work may intentionally fall short of this bar, but it must be labeled experimental/prototype and must not be presented as flagship or finished.

## Validation is necessary, not sufficient

Validation answers questions such as:

- does the artifact conform to its schema/contract;
- do malformed inputs fail safely;
- do tests and CI pass;
- are runtime/package assumptions internally consistent;
- can the implementation perform the behaviors its code claims to perform.

Validation does **not** by itself answer:

- is the methodology complete;
- did we miss a high-value capability or common failure mode;
- is the evidence appropriate for the claim;
- is the domain judgment actually good;
- does the output help real users;
- does the contribution match or exceed strong external alternatives.

Green CI is therefore one release gate, not the definition of quality.

## Release gates

For a reusable skill/tool to be treated as finished, assess the applicable gates separately:

1. **Code and contract correctness**
   - compilation/tests pass;
   - malformed input is bounded;
   - schemas, manifests, links, entrypoints, and runtime contracts agree;
   - permissions/authority boundaries are enforced.

2. **Methodological coverage**
   - important domain practices and known failure modes are represented;
   - the workflow searches for missed opportunities and blind spots, not only expected defects;
   - context-sensitive choices are not flattened into universal heuristics;
   - strengths and tradeoffs are preserved, not only problems catalogued.

3. **Evidence quality**
   - claims use evidence appropriate to the claim;
   - source inspection is not substituted for rendered/behavioral proof when experience is being judged;
   - public/market claims use current attributable evidence;
   - unknowns remain provisional instead of being filled with model memory or inference.

4. **Real-world forward testing**
   - exercise the work on multiple real projects/cases with materially different conditions;
   - test whether it reaches the **right judgment or outcome**, not merely whether its output validates;
   - convert generic failures discovered in forward testing into regression tests or durable methodology changes.

5. **External/empirical benchmark quality**
   - before claiming parity or superiority to leading work, compare against independent expert findings, trusted reference results, real user/behavioral evidence, or another credible benchmark appropriate to the domain;
   - use a diversified test set rather than one or two friendly examples;
   - distinguish "designed to compete with the best" from "empirically shown to match/exceed the best."

Not every contribution needs a formal market benchmark before it can be useful, but **market-leading claims require market-leading evidence**.

## Competitive research

When competitor/reference comparison is relevant:

- identify leaders using current measurable evidence rather than model memory;
- compare equivalent jobs/outcomes, not surface similarity;
- ask what principle produces the result and whether it fits this project;
- do not copy branding, wording, layout, proprietary interaction sequences, or distinctive creative expression;
- explicitly note where our work is already stronger so revision does not erase useful differentiation.

## Completion question

Before calling reusable work done, ask:

> If this passes every internal validator but a strong practitioner or top competing product would still expose obvious omissions, blind spots, weak evidence, or materially better practice, what are those gaps?

If material gaps remain and are reasonably addressable, the work is not finished. If a gap cannot be closed now, document it as an explicit limitation rather than implying completion.
