# Slack digest frontmatter-only repair pattern

Use this when a target-date Slack digest already exists and the body is richer than what a fresh ad-hoc reconstruction would produce, but the frontmatter predates the current `slack-capture` Output spec.

## When to repair rather than recapture

Repair metadata only when:

- The exact source wikilink is absent from `Daily/{YYYY-MM-DD}.md`; a linked digest has handed off to the core and must not be changed.
- Existing digest body already contains the qualifying messages for the target date.
- Body includes richer material worth preserving: attachment placeholders, original mention display text, thread permalinks, or manually validated counts.
- The only known defect is frontmatter shape, such as:
  - `source: "slack:daily:{channel_id}:{date}"` instead of `slack:digest:{channel_slug}:{date}`
  - timestamp-valued `created`
  - missing `is_private`, `user_authored`, `user_mentioned`, `message_count`, or `fetched_at`

Do **not** overwrite the body with a simplified search reconstruction just to fix metadata.

## Minimal repair steps

1. Resolve the target date from live clock in Asia/Tokyo and record `fetched_at`.
2. For each existing `Inbox/{YYYY-MM-DD}/slack/*.md`, compare:
   - frontmatter `message_count`
   - body line `- Qualifying messages: N`
   - number of timestamped message sections if needed
3. Replace only the YAML frontmatter with the current required fields:
   - `title`, `type: "capture"`, `status: "inbox"`, `tags`
   - `source: "slack:digest:{channel_slug}:{YYYY-MM-DD}"`
   - `channel`, `channel_id`, `is_dm`, `is_private`
   - `participants`
   - `user_authored`, `user_mentioned`
   - `message_count`
   - `fetched_at`
   - `created: YYYY-MM-DD` and `updated: YYYY-MM-DD` for the capture/repair run date
4. Preserve existing body text and richer optional fields such as valid `mentions: []` or populated `mentions` lists.
5. Verify:
   - no `slack:daily:` remains for the target date
   - no timestamp-valued `created:` remains
   - all required fields are present
   - `message_count` equals the body's `Qualifying messages`
   - `git diff --check -- Inbox/{YYYY-MM-DD}/slack` passes

## Caveat

If Slack API access is partial (`not_in_channel`, `channel_not_found`, rate limits, or scope limitations) but existing digest files are internally consistent, treat API gaps as coverage caveats. Do not degrade existing captures because a later run has less visibility.
