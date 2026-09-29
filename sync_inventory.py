#!/usr/bin/env python3
"""Sincroniza catalog-data.json y product-measures.json con el inventario real
(Inventario Pro / API publica de decada). Se ejecuta en CI (ver
.github/workflows/sync-inventory.yml) cada cierto tiempo, o a mano:

    python3 sync_inventory.py

Después hay que correr build.py para regenerar el HTML con los datos nuevos.
No toca product-measures.json a mano: las medidas se regeneran siempre desde
el inventario (si hace falta corregir una medida, se corrige en Inventario Pro).
"""
import json
import sys
import urllib.request
from pathlib import Path

API_BASE = "https://inventario-pro-beta.vercel.app"
ROOT = Path(__file__).parent

GENDER_MAP = {"HOMBRE": "hombre", "MUJER": "mujer", "NINO": "ninos"}
# Mismas etiquetas que build.py espera dentro de "meta" (ver build.py linea ~45)
CONDITION_META = {"EXCELLENT": "EXCELLENT", "VERY_GOOD": "MUY BUENO", "GOOD": "BUENO"}
SIZECM_MAP = {
    "chest": "PECHO",
    "waist": "CINTURA",
    "length": "LARGO",
    "shoulders": "HOMBROS",
    "inseam": "ENTREPIERNA",
}


def fetch(path):
    req = urllib.request.Request(API_BASE + path, headers={"User-Agent": "decada-web-sync/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def price_str(cents):
    euros = (cents or 0) / 100
    return f"{euros:.2f} €".replace(".", ",")


def main():
    try:
        data = fetch("/api/public/decada/products")
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR al llamar al inventario: {exc}", file=sys.stderr)
        return 1

    products = data.get("products", [])
    if not products:
        print("ERROR: el inventario devolvio 0 productos, no se toca catalog-data.json", file=sys.stderr)
        return 1

    catalog = {"hombre": [], "mujer": [], "ninos": []}
    measures = {}
    skipped = 0

    for p in products:
        if p.get("sold"):
            continue
        gender = GENDER_MAP.get(p.get("gender") or "")
        if not gender:
            skipped += 1
            continue
        images = [u for u in (p.get("images") or []) if u]
        slug = p.get("slug")
        name = p.get("name")
        if not images or not slug or not name:
            skipped += 1
            continue

        cond_label = CONDITION_META.get(p.get("condition") or "", "")
        size = p.get("size") or "Consultar talla"
        meta = f"TALLA {size} · {cond_label}" if cond_label else f"TALLA {size}"

        catalog[gender].append({
            "imgs": images,
            "meta": meta,
            "name": name,
            "price": price_str(p.get("priceInCents")),
            "slug": slug,
            "condition": "",
        })

        size_cm = p.get("sizeCm") or {}
        m = {
            SIZECM_MAP[k]: f"{round(v)} cm"
            for k, v in size_cm.items()
            if k in SIZECM_MAP and isinstance(v, (int, float))
        }
        if m:
            measures[slug] = m

    (ROOT / "catalog-data.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (ROOT / "product-measures.json").write_text(
        json.dumps(measures, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )

    total = sum(len(v) for v in catalog.values())
    print(
        f"Sincronizados {total} productos ({skipped} omitidos). "
        f"hombre={len(catalog['hombre'])} mujer={len(catalog['mujer'])} ninos={len(catalog['ninos'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
