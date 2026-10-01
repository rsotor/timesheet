#!/usr/bin/env python3
"""Timesheet multi-provider: BambooHR + Productive.io"""

import sys

from timesheet.common import missing_env, parse_args, working_days
from timesheet import bamboo, productive


PROVIDERS = {
    "bamboo": bamboo,
    "productive": productive,
}


def main():
    start_date, end_date, provider_names, skip_confirm = parse_args(sys.argv[1:])
    days = working_days(start_date, end_date)

    # BambooHR siempre es necesario: se usa para detectar días libres
    required = list(bamboo.REQUIRED_ENV)
    if "productive" in provider_names:
        required += productive.REQUIRED_ENV
    missing = missing_env(tuple(required))
    if missing:
        print("❌ Faltan variables en .env:")
        for name in missing:
            print(f"   - {name}")
        print("   Copia .env.example a .env y complétalo (ver README).")
        sys.exit(1)

    provider_label = " + ".join(p.capitalize() for p in provider_names)
    print(f"\n📅 Timesheet: {start_date} → {end_date} ({len(days)} días laborables)")
    print(f"Destino: {provider_label}")

    if not skip_confirm:
        answer = input("Continuar? [Y/n] ").strip().lower()
        if answer and answer != "y":
            print("Cancelado.")
            sys.exit(0)

    stats = {name: {"done": 0, "exists": 0, "error": 0} for name in provider_names}
    off_days = 0
    productive_days: list = []

    for day in days:
        print(f"\n⏰ {day}")

        if bamboo.is_off_day(day):
            print("   🏖️ Día libre — skip")
            off_days += 1
            continue

        for name in provider_names:
            provider = PROVIDERS[name]
            label = f"   {name.capitalize() + ':':15}"
            if provider.has_entries(day):
                print(f"{label}⏭️ Ya existe")
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

    print(f"\n--- Resumen ---")
    for name in provider_names:
        s = stats[name]
        parts = []
        if s["exists"]:
            parts.append(f"{s['exists']} ya existían")
        if s["error"]:
            parts.append(f"{s['error']} errores")
        detail = f" ({', '.join(parts)})" if parts else ""
        print(f"✅ {name.capitalize():12} {s['done']}/{len(days)} días registrados{detail}")
    if off_days:
        print(f"🏖️ Días libres: {off_days}")

    if productive_days:
        answer = input(f"\n¿Enviar a aprobación en Productive {len(productive_days)} día(s)? [y/N] ").strip().lower()
        if answer == "y":
            submit_stats = {"done": 0, "exists": 0, "error": 0}
            for day in productive_days:
                result = productive.submit_day(day)
                icon = {"done": "✅", "exists": "⏭️", "error": "❌"}[result]
                print(f"   {day}  {icon} {result}")
                submit_stats[result] += 1
            parts = []
            if submit_stats["exists"]:
                parts.append(f"{submit_stats['exists']} ya enviados")
            if submit_stats["error"]:
                parts.append(f"{submit_stats['error']} errores")
            detail = f" ({', '.join(parts)})" if parts else ""
            print(f"📤 Enviados: {submit_stats['done']}/{len(productive_days)}{detail}")


if __name__ == "__main__":
    main()
