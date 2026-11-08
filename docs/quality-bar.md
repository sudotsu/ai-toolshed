# AI Toolshed quality bar

## Default standard

Reusable Toolshed work should, by default, be built to be **as good as or better than the five best current performers in its domain**.

That standard is intentionally narrow and concrete. It is not satisfied by saying the work is "competitive," "strong," or comparable to vaguely defined leaders.

The only normal exception is when top-five parity is genuinely unnecessary for the project's actual use case. In that case, record the narrower target explicitly and explain why meeting the full top-five bar would add cost/complexity without meaningful value for that project.

Prototype work may intentionally fall short of this bar, but it must be labeled experimental/prototype and must not be presented as flagship or finished.

## Selecting the five

Do not choose the benchmark set from model memory, familiarity, convenience, or one favorable metric.

Identify the five best current performers using **current, attributable, domain-appropriate evidence**. The exact signals vary by domain, but selection should normally use multiple relevant signals such as:

- real adoption, usage, market share, customer base, or category presence;
- measurable outcomes, performance, reliability, accuracy, or task success;
- independent expert evaluations, trusted benchmarks, or rigorous comparative testing;
- current review/user sentiment at meaningful scale when it measures something relevant;
- category leadership, current ranking, recognized methodology, or demonstrated practice quality;
- domain-specific evidence that explains why the candidate is actually among the best at the job being benchmarked.

Do not rely on vendor marketing alone when independent evidence is reasonably available. Do not use popularity alone when popularity does not measure quality for the domain.

Record why each of the five qualifies. If the evidence cannot support a confident top-five set, mark the set provisional rather than pretending certainty.

## Comparing against the five

Do not game the rule by cherry-picking only dimensions where our work already looks favorable.

Compare the core capabilities and quality criteria expected of competent work in that category, including relevant standard practices, important failure modes, usability/operational constraints, and the qualities that explain why the benchmark leaders are good.

A benchmark capability may be marked not applicable only when the actual project use case makes it irrelevant. Record the reason.

The goal is **not** to maximize feature count or copy the five. A smaller implementation can still meet or beat the bar when it performs the actual job as well or better for the intended use case.

Preserve useful differentiation instead of normalizing everything toward competitors.

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
- does the contribution actually match or exceed the five best current alternatives.

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

5. **Top-five benchmark quality**
   - identify the five best current performers with justified evidence;
   - compare against the core capabilities and quality criteria that matter in the category;
   - use independent expert findings, trusted reference results, real user/behavioral evidence, or another credible benchmark when available;
   - use a diversified test set rather than one or two friendly examples;
   - distinguish "built to meet the top-five bar" from "empirically shown to match/exceed the top five."

Not every internal/prototype contribution needs a formal empirical market benchmark before it can be useful, but reusable flagship work should default to the top-five bar, and **claims of parity/superiority require evidence strong enough to support them**.

## Competitive/reference research

When competitor/reference comparison is relevant:

- select the top-five benchmark set with current measurable evidence rather than model memory;
- compare equivalent jobs/outcomes, not surface similarity;
- ask what principle produces the result and whether it fits this project;
- do not copy branding, wording, layout, proprietary interaction sequences, or distinctive creative expression;
- explicitly note where our work is already stronger so revision does not erase useful differentiation.

## Completion question

Before calling reusable work done, ask:

> If this passes every internal validator but is placed beside the five best current performers in its domain, where would a strong practitioner still find our work materially worse, incomplete, weakly evidenced, or behind standard practice?

If material gaps remain and are reasonably addressable, the work is not finished. If the project's actual use case does not require closing a gap, record that decision and why. If a required gap cannot be closed now, document it as an explicit limitation rather than implying completion.
