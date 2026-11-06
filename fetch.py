"""Download Pokémon data from PokéAPI into data/pokemon.json.

Run with `uv run fetch.py`. Already-saved Pokémon are skipped, so re-running
only fetches what is missing (and retries any that failed last time).
"""

import json
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ingest import DATA as OUT

BASE = "https://pokeapi.co/api/v2"  # https://pokeapi.co/docs/v2
LAST_ID = 1025

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

ability_cache = {}


def get_json(url):
    """GET a URL and return its JSON body.

    Retries on 429/5xx (via the session) and raises requests.HTTPError on
    any remaining error status, so failures surface here, not as KeyErrors later.
    """
    resp = session.get(url, timeout=10)
    resp.raise_for_status()  # 404/429/5xx → HTTPError, not KeyError later
    return resp.json()


def get_ability(url):
    """Return ability JSON, fetching each ability URL at most once per run."""
    if url not in ability_cache:
        ability_cache[url] = get_json(url)
    return ability_cache[url]


def fetch_pokemon(i):
    """Fetch one Pokémon by National Dex number and return it as a search document.

    Combines the /pokemon and /pokemon-species endpoints plus each ability's
    English short effect. Text fields are flattened to strings so they can be
    indexed directly.

    Raises:
        requests.RequestException: if any request fails after retries.
    """
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

    return {
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


def save(docs):
    """Write documents to data/pokemon.json, sorted by id for stable diffs."""
    OUT.parent.mkdir(exist_ok=True)
    docs.sort(key=lambda d: d["id"])
    with OUT.open("w") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)


def fetch_all():
    """Fetch every Pokémon up to LAST_ID that isn't already saved, then save.

    Failed Pokémon are logged and skipped; they will be retried on the next run.
    """
    docs = json.loads(OUT.read_text()) if OUT.exists() else []
    have = {d["id"] for d in docs}
    todo = [i for i in range(1, LAST_ID + 1) if i not in have]
    print(f"{len(have)} already saved, fetching {len(todo)}")

    for i in todo:
        try:
            docs.append(fetch_pokemon(i))
        except requests.RequestException as e:
            print(f"Skipping #{i}: {e}")
            continue
        time.sleep(0.1)

    save(docs)


if __name__ == "__main__":
    fetch_all()
