# Forward-Testing Protocol

Unit tests prove contract behavior. They do not prove the skill produces a useful teardown.

Before a material release, run at least two read-only forward tests on materially different products:

1. a public marketing/service experience with a conversion or contact journey;
2. an authenticated or application-style product with richer interaction/state behavior.

For each:

- freeze the audited revision/environment;
- execute the skill from its normal user-facing trigger;
- do not seed expected findings;
- produce the full canonical artifact;
- run renderer and validator;
- independently review whether the artifact found real issues, preserved strengths, separated evidence from taste, and covered journeys/states rather than screenshots;
- record false positives, false negatives, severity inflation, missing state coverage, unsupported user-outcome claims, and any validator loophole;
- fix the general contract/methodology rather than encoding project-specific answers;
- rerun regression tests;
- rerun the materially affected forward test.

A forward test passes only when the artifact is useful enough for `ux-ui-revision` to implement without reconstructing the audit from scratch.

Do not call runtime portability verified unless each claimed runtime/surface is separately exercised.
