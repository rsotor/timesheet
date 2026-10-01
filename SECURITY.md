# Security policy

## Reporting a vulnerability

Please **do not open a public issue**. Report it privately at
<https://github.com/rsotor/timesheet/security/advisories/new>.

Include what you found, how to reproduce it and its impact. You will get an answer as soon as possible.

## What counts

- Credentials from `.env` being leaked: printed, logged, sent anywhere other than the BambooHR or
  Productive.io APIs, or ending up in a file that git could commit.
- Requests sent to a host other than `<subdomain>.bamboohr.com` or `api.productive.io`.
- A dependency with a known vulnerability that affects this tool.

## What does not count

- Leaking your own credentials by sharing your `.env` or committing it yourself.
- Behaviour of the BambooHR or Productive.io APIs themselves: report those to the vendor.
