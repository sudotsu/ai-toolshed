# Authority and External Actions

Use this matrix before implementation and again before every production or external mutation.

## Required authority IDs

Record all fourteen IDs exactly once in `revision.json`:

| ID | Authority |
|---|---|
| `local_repository_edits` | Local repository or working-copy edits |
| `cms_content_database_edits` | CMS or content-database edits |
| `commit_push` | Commit and push |
| `pull_request` | Pull-request creation or update |
| `merge` | Merge |
| `deployment` | Deployment |
| `publication` | Publication or unpublishing |
| `search_controls_activation` | Redirect, canonical, robots, noindex, sitemap, feed, or URL-migration activation |
| `search_platform_actions` | Search Console or Bing Webmaster actions |
| `profile_listing_actions` | Business Profile, Merchant Center, listing, citation, review, or profile changes |
| `analytics_tracking_actions` | Analytics, tag-manager, consent, call-tracking, or conversion-definition changes |
| `outreach_third_party` | Outreach, digital PR, link acquisition, partnerships, or communications |
| `purchases_external_services` | Purchases, ads, subscriptions, paid tools, or external services |
| `regulated_content_approval` | Legal, regulated, safety, medical, financial, gambling, or credentialed-content approval |

Allowed authority states are `authorized`, `not-authorized`, `not-requested`, and `blocked`.

Every row must state the exact authorized scope, evidence of authorization where applicable, and limitations. An `authorized` state never expands beyond its recorded scope.

## Non-implication rules

- Local edits do not authorize commit or push.
- Commit and push do not authorize a pull request, merge, deployment, or publication.
- Deployment does not authorize publication, search-control activation, platform submissions, analytics changes, or profile edits.
- Source changes to redirects, canonicals, robots, noindex, sitemap, feeds, or URL migrations do not authorize activating them in production.
- A profile/listing permission does not authorize review solicitation, citation creation, outreach, or paid placement.
- A content approval does not authorize regulated claims or invented credentials.
- Readiness is an assessment. It is never authority.

Default every external authority to `not-requested` unless the owner explicitly authorizes it.

## External mutation procedure

Before an authorized external action:

1. Resolve the exact system, account, property, record, route, or profile.
2. Capture the current value and timestamp.
3. Confirm canonical owner facts and conflicting sources.
4. Preview the exact change and consequence.
5. Confirm rollback or correction steps.
6. Perform only the authorized action.
7. Re-read the external system and record evidence of the resulting value.
8. Record failures or partial application honestly.

Do not claim an external change from a submitted request, local source edit, planned action, screenshot of a form, or unverified tool response.

## High-risk search controls

The following require an inventory, representative samples, collision checks, staged rollout where practical, and rollback instructions:

- Redirects and URL migrations.
- Canonicals and `noindex`.
- Robots and sitemap changes.
- Feed removals or replacements.
- Templated or programmatic page generation.
- Content deletion or consolidation.
- Analytics, consent, and conversion-definition changes.
- Profile and listing changes.
- Regulated or safety claims.

If a safe preview or rollback is unavailable, leave activation blocked and distinguish deployment-ready source from authorized production state.

## Credentials and sensitive data

Never request credentials, tokens, recovery codes, private keys, or secrets through chat. Use configured secure connectors, environment-backed credentials already authorized for the task, or a user-operated handoff. Sanitize artifacts, commands, evidence, screenshots, and logs.
