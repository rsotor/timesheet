#!/usr/bin/env python3
"""Timesheet multi-provider: BambooHR + Productive.io"""

import sys

from timesheet.common import config_errors, parse_args, working_days
from timesheet import bamboo, productive


PROVIDERS = {
    "bamboo": bamboo,
    "productive": productive,
}


def main():
    # Windows uses a legacy code page (e.g. cp1252) when output is redirected,
    # which cannot encode the emoji in our messages.
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")

    start_date, end_date, provider_names, skip_confirm = parse_args(sys.argv[1:])
    days = working_days(start_date, end_date)

    # BambooHR is always required: it is used to detect days off
    required = dict(bamboo.REQUIRED_ENV)
    if "productive" in provider_names:
        required.update(productive.REQUIRED_ENV)
    errors = config_errors(required)
    if errors:
        print("❌ Invalid configuration in .env:")
        for error in errors:
            print(f"   - {error}")
        print("   Copy .env.example to .env and fill it in (see README).")
        sys.exit(1)

    provider_label = " + ".join(p.capitalize() for p in provider_names)
    print(f"\n📅 Timesheet: {start_date} → {end_date} ({len(days)} working {'day' if len(days) == 1 else 'days'})")
    print(f"Target: {provider_label}")

    if not skip_confirm:
        answer = input("Continue? [Y/n] ").strip().lower()
        if answer and answer != "y":
            print("Cancelled.")
            sys.exit(0)

    stats = {name: {"done": 0, "exists": 0, "error": 0} for name in provider_names}
    off_days = 0
    productive_days: list = []

    for day in days:
        print(f"\n⏰ {day}")

        if bamboo.is_off_day(day):
            print("   🏖️ Day off — skipped")
            off_days += 1
            continue

        for name in provider_names:
            provider = PROVIDERS[name]
            label = f"   {name.capitalize() + ':':15}"
            if provider.has_entries(day):
                print(f"{label}⏭️ Already registered")
                stats[name]["exists"] += 1
                if name == "productive":
                    productive_days.append(day)
            elif provider.clock_day(day):
                print(f"{label}✅ Done")
                stats[name]["done"] += 1
                if name == "productive":
                    productive_days.append(day)
            else:
                print(f"{label}❌ Error")
                stats[name]["error"] += 1

    print("\n--- Summary ---")
    for name in provider_names:
        s = stats[name]
        parts = []
        if s["exists"]:
            parts.append(f"{s['exists']} already registered")
        if s["error"]:
            parts.append(f"{s['error']} errors")
        detail = f" ({', '.join(parts)})" if parts else ""
        print(f"✅ {name.capitalize():12} {s['done']}/{len(days)} days registered{detail}")
    if off_days:
        print(f"🏖️ Days off: {off_days}")

    if productive_days:
        answer = input(f"\nSubmit {len(productive_days)} day(s) for approval in Productive? [y/N] ").strip().lower()
        if answer == "y":
            submit_stats = {"done": 0, "exists": 0, "error": 0}
            for day in productive_days:
                result = productive.submit_day(day)
                icon, text = {
                    "done": ("✅", "Submitted"),
                    "exists": ("⏭️", "Already submitted"),
                    "error": ("❌", "Error"),
                }[result]
                print(f"   {day}  {icon} {text}")
                submit_stats[result] += 1
            parts = []
            if submit_stats["exists"]:
                parts.append(f"{submit_stats['exists']} already submitted")
            if submit_stats["error"]:
                parts.append(f"{submit_stats['error']} errors")
            detail = f" ({', '.join(parts)})" if parts else ""
            print(f"📤 Submitted: {submit_stats['done']}/{len(productive_days)}{detail}")


if __name__ == "__main__":
    main()
