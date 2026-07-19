# GSK calendar schedules vs meeting notes

Session learning: Genspark AI Meeting Notes UI can show upcoming meeting schedules. In GSK CLI these are retrieved via the calendar integration, not via `gsk meeting list/search/get`.

Commands verified:

```bash
# Discover connected calendar account(s)
gsk calendar accounts

# List upcoming events for a time range
gsk calendar list \
  --time_min "YYYY-MM-DDT00:00:00+09:00" \
  --time_max "YYYY-MM-DDT23:59:59+09:00" \
  -a "<calendar-account-email>"

# Keyword-filter upcoming events
gsk calendar list \
  --filter_query "定例" \
  --time_min "YYYY-MM-DDT00:00:00+09:00" \
  --time_max "YYYY-MM-DDT23:59:59+09:00" \
  -a "<calendar-account-email>"
```

Observed fields include `summary`, `description`, `location`, `start`, `end`, `attendees`, `organizer`, `status`, and `conferenceUrl`.

Pitfall:
- `gsk meeting list/search/get` is for created meeting notes / transcripts.
- `gsk meeting search` accepts date filters but still requires `--keyword`, and is not the right primary path for upcoming schedule listing.
- For future schedules, start with `gsk calendar accounts`, then `gsk calendar list` (or `gsk google_calendar list`).
