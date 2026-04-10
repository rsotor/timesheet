# Timesheet Automation

A Python CLI to automatically submit timesheet entries to **BambooHR** and/or **Productive.io** via their APIs.

## Features

- 🕐 Registers 8 hours per working day (08:00–13:00, 14:00–17:00) in BambooHR
- 📅 Flexible period selection: today, week, month, last-month, day number, or explicit date range
- 🏖️ Skips days with approved time-off requests (checked via BambooHR)
- ✅ Prevents duplicate entries in both providers
- 🔧 Patches 0-minute entries in Productive.io instead of creating duplicates
- 🎯 Provider selection flags: run against one or both providers
- ⚡ Skip confirmation prompt with `-y`

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager
- BambooHR account with API access
- Productive.io account with API access

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd bamboo-timesheeet
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your credentials (see [Getting Credentials](#getting-credentials) below).

## Getting Credentials

### BambooHR

**Employee ID:**
- Check your profile URL: `https://company.bamboohr.com/employees/employee.php?id=XXXX`
- Or ask your HR administrator

**API Key:**
1. Log in to BambooHR
2. Click your name → **API Keys**
3. Click **Generate new key** and copy it to `.env`

### Productive.io

**API Token:**
1. Go to **Settings → API integrations**
2. Click **Generate new token** and copy it to `.env`

**Organization ID:**
- Found in your Productive URL or in API settings

**Person ID:**
```bash
curl -H "X-Auth-Token: YOUR_TOKEN" \
     "https://api.productive.io/api/v2/people?filter[email]=your@email.com"
```

**Service ID:**
```bash
curl -H "X-Auth-Token: YOUR_TOKEN" \
     "https://api.productive.io/api/v2/time_entries?filter[person_id]=YOUR_PERSON_ID&page[size]=1"
# Check the `service` relationship in the response
```

## Usage

```bash
uv run timesheet.py [period] [--bamboo | --productive | --both] [-y]
```

### Period options

| Argument | Description |
|---|---|
| *(none)* | Today |
| `today` | Today |
| `week` | Monday of current week → today |
| `month` | 1st of current month → today |
| `last-month` | Full previous month |
| `22` | 1st of current month → day 22 |
| `01-03-2025 31-03-2025` | Explicit range (DD-MM-YYYY) |

### Examples

```bash
# Register today in both providers (default)
uv run timesheet.py

# Register the full current week, skip confirmation
uv run timesheet.py week -y

# Register from the 1st to the 15th of this month, BambooHR only
uv run timesheet.py 15 --bamboo

# Register last month in Productive.io only
uv run timesheet.py last-month --productive

# Register a custom range in both providers
uv run timesheet.py 01-03-2025 31-03-2025 --both
```

### Provider flags

| Flag | Description |
|---|---|
| `--bamboo` | Submit to BambooHR only |
| `--productive` | Submit to Productive.io only |
| `--both` | Submit to both (default) |
| `-y` / `--yes` | Skip the confirmation prompt |

## How It Works

For each working day in the selected range:

1. 🏖️ Checks BambooHR for approved time-off — skips if found
2. ✅ Checks each provider for existing entries — skips if already registered
3. 📝 Creates entries in each selected provider:
   - **BambooHR:** two clock entries (08:00–13:00 and 14:00–17:00)
   - **Productive.io:** one time entry (480 minutes); patches existing 0-minute entries if present

## Project Structure

```
bamboo-timesheeet/
├── timesheet.py          # CLI entry point
├── timesheet/
│   ├── __init__.py
│   ├── common.py         # Argument parsing and working-day helpers
│   ├── bamboo.py         # BambooHR provider (is_off_day, has_entries, clock_day)
│   └── productive.py     # Productive.io provider (has_entries, clock_day)
├── tests/
│   ├── __init__.py
│   └── test_common.py
├── .env.example
└── pyproject.toml
```

## Running Tests

```bash
uv sync --extra dev
uv run pytest tests/ -v
```
