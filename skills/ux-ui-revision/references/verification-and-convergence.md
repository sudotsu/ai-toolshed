# Verification and Convergence

## Evidence ladder

Use the strongest directly obtained level:

1. `source_inspection`
2. `rendered_experience`
3. `assistive_technology`
4. `published_experience`
5. `user_observation`
6. `first_party_measurement`
7. `business_outcome`

Never infer a higher level from a lower one.

## Journey verification

For each fixed material finding, rerun the affected journey at the viewports/input modes/states named by teardown acceptance criteria.

Minimum questions:

- Can the user still enter the flow?
- Is orientation clear?
- Is the intended action discoverable?
- Is focus visible and ordered?
- Are labels/semantics accurate?
- Are loading/validation/error/success states coherent?
- Is state preserved across errors/retry?
- Does mobile preserve hierarchy and access?
- Did shared-component changes regress another journey?

## Accessibility verification

Use the correct tool for the claim:

- DOM/source inspection for semantics;
- keyboard exercise for keyboard claims;
- contrast computation for contrast claims;
- screen-reader/assistive-tech run for announcement/interaction claims;
- reflow/zoom tests for layout claims.

Static ARIA inspection does not prove the component behaves correctly.

## Convergence loop

1. freeze exact head/revision;
2. review baseline-to-current diff;
3. rerun material journeys;
4. inspect responsive/input/state coverage;
5. inspect current PR/CI/review leads;
6. create `REVUX-###` for valid new defects;
7. fix in severity/dependency order;
8. repeat until no new blocking defect appears.

A review bot saying "looks good" is evidence that no issue was reported by that reviewer, not proof of UX quality.
