#!/usr/bin/env python3
"""Ajoute un relevé pour chaque station suivie à data/history.jsonl.

Utilisé par .github/workflows/collect-data.yml, appelé toutes les 15 minutes.

Deux fichiers sont maintenus :
- data/history.jsonl        : détail brut (un relevé par station toutes les
                               15 min), gardé sur une fenêtre glissante de
                               RAW_RETENTION_DAYS jours.
- data/history-hourly.jsonl : au-delà de cette fenêtre, les relevés ne sont
                               PAS supprimés mais résumés en une moyenne par
                               station/date/heure — l'historique complet est
                               ainsi conservé indéfiniment, sans que le fichier
                               brut ne grossisse sans limite.

Les identifiants de station suivis doivent rester alignés avec TABAREAU/NEARBY
dans index.html.
"""
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
    PARIS = ZoneInfo("Europe/Paris")
except Exception:  # pragma: no cover - fallback if tzdata is unavailable
    PARIS = timezone.utc

# TABAREAU + les 4 stations de secours définies dans index.html (NEARBY).
STATION_IDS = ["4021", "4002", "4009", "4006", "4017"]
RAW_RETENTION_DAYS = 30
RAW_PATH_DEFAULT = "data/history.jsonl"
HOURLY_PATH_DEFAULT = "data/history-hourly.jsonl"


def read_jsonl(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
        if not rows:
            f.write("")


def collect_new_rows(status_path):
    with open(status_path, encoding="utf-8") as f:
        data = json.load(f)
    stations = {s.get("station_id"): s for s in data.get("data", {}).get("stations", [])}

    rows = []
    for sid in STATION_IDS:
        station = stations.get(sid)
        if station is None:
            continue
        vt = station.get("vehicle_types_available", [])
        elec = next((v["count"] for v in vt if v.get("vehicle_type_id") == "electrical"), None)
        meca = next((v["count"] for v in vt if v.get("vehicle_type_id") == "mechanical"), None)
        if elec is None:
            elec = station.get("num_bikes_available", 0)
        if meca is None:
            meca = 0
        docks = station.get("num_docks_available", 0)
        t = station.get("last_reported") or int(time.time())
        rows.append({"t": int(t), "id": sid, "elec": int(elec), "meca": int(meca), "docks": int(docks)})
    return rows


def normalize_raw(rows, default_id):
    """Compat : d'anciens relevés (avant collecte multi-stations) n'ont pas de champ 'id'."""
    out = []
    for r in rows:
        r = dict(r)
        r.setdefault("id", default_id)
        out.append(r)
    return out


def merge_into_hourly(hourly_rows, rows_to_aggregate):
    rollup = {}
    for r in hourly_rows:
        key = (r["date"], r["hour"], r["id"])
        rollup[key] = r

    groups = defaultdict(list)
    for r in rows_to_aggregate:
        local = datetime.fromtimestamp(r["t"], tz=timezone.utc).astimezone(PARIS)
        key = (local.strftime("%Y-%m-%d"), local.hour, r["id"])
        groups[key].append(r)

    for key, grp in groups.items():
        date, hour, sid = key
        n_new = len(grp)
        sum_elec = sum(g["elec"] for g in grp)
        sum_docks = sum(g["docks"] for g in grp)
        if key in rollup:
            existing = rollup[key]
            total_n = existing["n"] + n_new
            elec = (existing["elec"] * existing["n"] + sum_elec) / total_n
            docks = (existing["docks"] * existing["n"] + sum_docks) / total_n
            rollup[key] = {"date": date, "hour": hour, "id": sid, "elec": round(elec, 2), "docks": round(docks, 2), "n": total_n}
        else:
            rollup[key] = {"date": date, "hour": hour, "id": sid, "elec": round(sum_elec / n_new, 2), "docks": round(sum_docks / n_new, 2), "n": n_new}

    return sorted(rollup.values(), key=lambda r: (r["date"], r["hour"], r["id"]))


def main(status_path, raw_path=RAW_PATH_DEFAULT, hourly_path=HOURLY_PATH_DEFAULT):
    new_rows = collect_new_rows(status_path)
    if not new_rows:
        print("Aucune station connue trouvée dans le flux, on ignore ce relevé.")
        return

    existing_raw = normalize_raw(read_jsonl(raw_path), STATION_IDS[0])
    all_raw = existing_raw + new_rows

    cutoff = time.time() - RAW_RETENTION_DAYS * 86400
    kept_raw = [r for r in all_raw if r.get("t", 0) >= cutoff]
    aged_out = [r for r in all_raw if r.get("t", 0) < cutoff]

    write_jsonl(raw_path, sorted(kept_raw, key=lambda r: (r["t"], r["id"])))

    if aged_out:
        existing_hourly = read_jsonl(hourly_path)
        merged_hourly = merge_into_hourly(existing_hourly, aged_out)
        write_jsonl(hourly_path, merged_hourly)
        print(f"{len(aged_out)} relevé(s) de plus de {RAW_RETENTION_DAYS} jours résumé(s) dans {hourly_path}.")

    print(f"{len(new_rows)} nouveau(x) relevé(s) ajouté(s) ({len(kept_raw)} lignes brutes conservées).")


if __name__ == "__main__":
    status_arg = sys.argv[1]
    raw_arg = sys.argv[2] if len(sys.argv) > 2 else RAW_PATH_DEFAULT
    hourly_arg = sys.argv[3] if len(sys.argv) > 3 else HOURLY_PATH_DEFAULT
    main(status_arg, raw_arg, hourly_arg)
