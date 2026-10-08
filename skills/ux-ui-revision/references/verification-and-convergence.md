# Verification and convergence

## Evidence types

Evidence types answer different questions. They are not a single ladder where any later type proves every earlier type:

1. `source_inspection`
2. `rendered_experience`
3. `assistive_technology`
4. `published_experience`
5. `user_observation`
6. `first_party_measurement`
7. `business_outcome`

A CSS diff can prove code changed. Business outcome data can show an outcome changed. Neither alone proves the interface looks better. Visual and interaction fixes require linked `rendered_experience` or `published_experience` evidence even when stronger behavioral evidence is also available.

## Verification by change type

Visual-craft change:
- render affected surfaces at representative widths;
- inspect hierarchy, color, spacing, typography, composition, and neighboring components.

Journey/interaction change:
- rerun from realistic entry to outcome;
- verify relevant states, back/recovery behavior, and mobile path;
- re-evaluate effort -> feedback -> progress -> payoff.

Competitive-calibration change:
- verify the principle improved the project without cloning competitor expression;
- preserve areas where the project was already stronger.

Accessibility/readability change:
- verify the actual issue and representative interaction; use assistive technology when the finding requires it.

## Convergence

The adversarial pass specifically looks for fixes that are locally correct but globally worse: more steps, less authenticity, new visual inconsistency, broken mobile layouts, or removed strengths.
