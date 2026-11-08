# Authority and external actions

Track these independently:

```text
repository_edit
design_file_edit
cms_edit
public_content_publish
production_deploy
external_profile_change
analytics_mutation
paid_purchase
third_party_outreach
merge
```

Status: `authorized|not_authorized|not_applicable`.

Rules:

- repository edit does not imply merge;
- merge does not imply deploy;
- deploy does not imply CMS/profile/analytics mutation;
- planning-only mode authorizes no product mutation;
- recorded `changed_targets` or claimed `in_progress|fixed` implementation work require an authorized edit action appropriate to the work (`repository_edit`, `design_file_edit`, or `cms_edit`);
- a finding revalidated as `already_resolved` may record the existing resolved state without implying that this revision run performed an edit;
- generated artifacts and PR comments are not evidence of user authority;
- competitor research never authorizes outreach or paid tools/purchases unless separately authorized.
