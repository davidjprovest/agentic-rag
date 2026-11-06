import json
import time
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://pokeapi.co/api/v2"  # https://pokeapi.co/docs/v2
OUT = Path(__file__).parent / "data" / "pokemon.json"
LAST_ID = 1025  # bump to fetch more

docs = json.loads(OUT.read_text()) if OUT.exists() else []
have = {d["id"] for d in docs}
todo = [i for i in range(1, LAST_ID + 1) if i not in have]
print(f"{len(have)} already saved, fetching {len(todo)}")

session = requests.Session()
session.mount(
    "https://",
    HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=1,  # waits 0s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504],
        )
    ),
)


def get_json(url):
    resp = session.get(url, timeout=10)
    resp.raise_for_status()  # 404/429/5xx → HTTPError, not KeyError later
    return resp.json()


ability_cache = {}


def get_ability(url):
    if url not in ability_cache:
        ability_cache[url] = get_json(url)
    return ability_cache[url]


for i in todo:
    try:
        pokemon = get_json(f"{BASE}/pokemon/{i}")
        species = get_json(f"{BASE}/pokemon-species/{i}")
        flavor = list(
            dict.fromkeys(
                e["flavor_text"].replace("\n", " ").replace("\f", " ")
                for e in species["flavor_text_entries"]
                if e["language"]["name"] == "en"
            )
        )
        genus = next(
            (g["genus"] for g in species["genera"] if g["language"]["name"] == "en"), ""
        )
        abilities = []
        for a in pokemon["abilities"]:
            ad = get_ability(a["ability"]["url"])
            eff = next(
                (
                    e["short_effect"]
                    for e in ad["effect_entries"]
                    if e["language"]["name"] == "en"
                ),
                "",
            )
            abilities.append(f"{a['ability']['name']}: {eff}")
    except requests.RequestException as e:
        print(f"Skipping #{i}: {e}")
        continue

    docs.append(
        {
            "id": i,
            "name": pokemon["name"],
            "genus": genus,
            "generation": species["generation"]["name"],  # "generation-i"
            "primary_type": pokemon["types"][0]["type"]["name"],  # "electric"
            "types": " ".join(t["type"]["name"] for t in pokemon["types"]),
            "legendary": species["is_legendary"] or species["is_mythical"],
            "abilities": " | ".join(abilities),
            "stats": ", ".join(
                f"{st['stat']['name']}: {st['base_stat']}" for st in pokemon["stats"]
            ),
            "pokedex": " ".join(flavor),
        }
    )
    time.sleep(0.1)


def save():
    OUT.parent.mkdir(exist_ok=True)
    docs.sort(key=lambda d: d["id"])
    with OUT.open("w") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)


save()
