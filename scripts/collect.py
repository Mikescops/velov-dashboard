#!/usr/bin/env python3
"""Ajoute un relevé de la station Vélo'v Tabareau à data/history.jsonl.

Utilisé par .github/workflows/collect-data.yml, appelé toutes les 15 minutes.
Chaque ligne est un petit objet JSON : {"t": <epoch>, "elec": n, "meca": n, "docks": n}.
Le fichier est aussi purgé des relevés de plus de ~120 jours pour ne pas grossir indéfiniment.
"""
import json
import sys
import time

STATION_ID = "4021"  # TABAREAU
MAX_AGE_DAYS = 120


def main(status_path, out_path):
    with open(status_path, encoding="utf-8") as f:
        data = json.load(f)

    station = next(
        (s for s in data.get("data", {}).get("stations", []) if s.get("station_id") == STATION_ID),
        None,
    )
    if station is None:
        print("Station Tabareau introuvable dans le flux, on ignore ce relevé.")
        return

    vt = station.get("vehicle_types_available", [])
    elec = next((v["count"] for v in vt if v.get("vehicle_type_id") == "electrical"), None)
    meca = next((v["count"] for v in vt if v.get("vehicle_type_id") == "mechanical"), None)
    if elec is None:
        elec = station.get("num_bikes_available", 0)
    if meca is None:
        meca = 0
    docks = station.get("num_docks_available", 0)
    t = station.get("last_reported") or int(time.time())

    row = {"t": int(t), "elec": int(elec), "meca": int(meca), "docks": int(docks)}

    try:
        with open(out_path, encoding="utf-8") as f:
            existing = [line for line in f if line.strip()]
    except FileNotFoundError:
        existing = []

    cutoff = time.time() - MAX_AGE_DAYS * 86400
    kept = []
    for line in existing:
        try:
            obj = json.loads(line)
            if obj.get("t", 0) >= cutoff:
                kept.append(line.rstrip("\n"))
        except json.JSONDecodeError:
            continue

    kept.append(json.dumps(row, separators=(",", ":")))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(kept) + "\n")

    print(f"Relevé ajouté : {row} (total {len(kept)} lignes conservées)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
