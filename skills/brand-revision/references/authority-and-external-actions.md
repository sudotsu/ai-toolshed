# Brand Revision Authority and External Actions

Brand revision frequently crosses from repository edits into public identity, profiles, listings, CMS content, deployment, and outreach. Those actions have different authority and different rollback costs. No row implies another.

The canonical `authority_matrix` in `revision.json` contains exactly these IDs:

| ID | Action class | Default |
| --- | --- | --- |
| `AUTH-REPOSITORY-EDIT` | edit local/project repository files | not-authorized |
| `AUTH-CONTENT-EDIT` | edit copy/content in an authorized local source or draft surface | not-authorized |
| `AUTH-ASSET-EDIT` | create/replace brand assets in an authorized local source | not-authorized |
| `AUTH-CONFIGURATION-EDIT` | change shared identity/configuration/metadata source | not-authorized |
| `AUTH-CMS-MUTATION` | mutate a connected CMS or hosted content system | not-authorized |
| `AUTH-COMMIT` | create commits | not-authorized |
| `AUTH-PUSH` | push commits/branches | not-authorized |
| `AUTH-PULL-REQUEST` | create or update a pull request | not-authorized |
| `AUTH-MERGE` | merge a pull request or branch | not-authorized |
| `AUTH-DEPLOY` | trigger or approve deployment | not-authorized |
| `AUTH-PUBLISH` | make content publicly visible | not-authorized |
| `AUTH-SOCIAL-PROFILE` | mutate social profile/company-page identity or content | not-authorized |
| `AUTH-BUSINESS-LISTING` | mutate business/listing/directory records | not-authorized |
| `AUTH-OUTREACH` | contact customers, partners, media, reviewers, or third parties | not-authorized |
| `AUTH-PURCHASE` | buy domains, assets, ads, research, subscriptions, or services | not-authorized |

Each row records:

```text
id, state, scope, evidence_ids, limitations
```

`state` is `authorized|not-authorized|not-requested|blocked`.

## Rules

- Authorization must come from the owner/user or an already-authorized connected workflow. A teardown recommendation is not authorization.
- Scope must be concrete. “Fix the brand” does not authorize every external row.
- Repository editing does not authorize commit, push, PR, merge, deployment, CMS mutation, publication, profile/listing changes, outreach, or purchase.
- PR creation does not authorize merge. Merge does not authorize deploy. Deploy does not authorize publication if the deployment can remain non-public or draft.
- Publication of one owned website does not authorize publication on social profiles or listings.
- A user instruction such as “fix these and push to the PR” can authorize repository edit, content/asset/config edits required by the finding, commit/push, and PR update for that branch; it does not automatically authorize merge or deploy unless stated.
- Existing authenticated access does not imply authorization to mutate it.
- Never request raw credentials in chat. Use an already configured secure connection or mark the action blocked.
- External actions that can create irreversible identity drift, customer confusion, public claims, financial cost, or third-party communication require explicit scope even when technically reversible.

## High-risk brand actions

Treat these as high risk and require explicit owner approval plus rollback planning before execution:

- company, product, service, domain, or sub-brand renaming;
- parent/sub-brand relationship changes;
- canonical domain changes or public redirect/migration plans;
- removal of a recognizable legacy identity;
- major primary-promise or audience-positioning change;
- guarantee, credential, certification, licensing, safety, price, availability, or outcome claim changes;
- publication of new proof/testimonial/case material;
- large visual identity replacement affecting recognition;
- mass profile/listing updates;
- deletion of public content that materially supports discoverability or trust;
- customer/reviewer outreach;
- purchase of domains, paid research, ads, or creative assets.

## Safe defaults

When authority is missing or ambiguous:

- produce the local draft or plan;
- preserve current public state;
- record the exact blocked action and completion gate;
- do not infer that a “ready” state authorizes execution.
