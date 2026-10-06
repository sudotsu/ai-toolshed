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
- generated artifacts and PR comments are not evidence of user authority;
- competitor research never authorizes outreach or paid tools/purchases unless separately authorized.
