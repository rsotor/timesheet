# Changelog

What changes in each version. Written automatically from pull request titles.

## [0.2.1](https://github.com/rsotor/timesheet/compare/v0.2.0...v0.2.1) (2026-10-02)


### Bug fixes

* **productive:** only offer days not yet submitted for approval ([#10](https://github.com/rsotor/timesheet/issues/10)) ([27268e1](https://github.com/rsotor/timesheet/commit/27268e114c9315033fd4e516a988c46842c4be82))

## 0.2.0 (2026-10-01)

First public release.

- Register 8 hours per working day in BambooHR and/or Productive.io.
- Skip days with approved time off and days already registered.
- Optionally submit Productive.io days for approval.
- Check `.env` before making any request.
