#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_data.json"

app = FastAPI(title="Bible CLI API", version="0.1.0")


def load_data() -> dict[str, Any]:
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def find_verse(verses: list[dict[str, Any]], query: str) -> dict[str, Any] | None:
    normalized = query.strip()
    if ":" in normalized:
        return next((verse for verse in verses if verse["reference"] == normalized), None)
    return next(
        (
            verse
            for verse in verses
            if normalized in verse["text"] or normalized in verse["reference"]
        ),
        None,
    )


def suggest_verses(
    verses: list[dict[str, Any]], query: str, limit: int = 3
) -> list[dict[str, Any]]:
    tokens = {token for token in query.strip().split() if token}

    def score(verse: dict[str, Any]) -> int:
        verse_text = f"{verse['reference']} {verse['text']}"
        return sum(1 for token in tokens if token in verse_text)

    ranked = sorted(verses, key=score, reverse=True)
    return [verse for verse in ranked if score(verse) > 0][:limit]


def pick_today_meditation(data: dict[str, Any], today: date) -> dict[str, Any]:
    meditation = next(
        (item for item in data["meditations"] if item["date"] == today.isoformat()),
        None,
    )
    if meditation:
        return meditation
    index = today.toordinal() % len(data["meditations"])
    return data["meditations"][index]


@app.get("/api/search")
def search(query: str = Query(..., min_length=1)) -> dict[str, Any]:
    data = load_data()
    verse = find_verse(data["verses"], query)
    if not verse:
        return {
            "query": query,
            "results": [],
            "suggestions": suggest_verses(data["verses"], query),
        }
    return {
        "query": query,
        "results": [
            {
                "reference": verse["reference"],
                "text": verse["text"],
                "summary": verse["summary"],
                "perspectives": data["perspectives"][:3],
                "meditation": data["meditations"][0],
            }
        ],
        "suggestions": [],
    }


@app.get("/api/today")
def today() -> dict[str, Any]:
    data = load_data()
    selected = pick_today_meditation(data, date.today())
    return {
        "date": date.today().isoformat(),
        "reference": selected["reference"],
        "summary": selected["summary"],
        "application_questions": selected["application_questions"],
        "prayer": selected["prayer"],
    }


@app.get("/api/meditate")
def meditate(query: str = Query(..., min_length=1)) -> dict[str, Any]:
    data = load_data()
    verse = find_verse(data["verses"], query)
    if not verse:
        return {
            "query": query,
            "result": None,
            "suggestions": suggest_verses(data["verses"], query),
        }
    return {
        "query": query,
        "result": {
            "reference": verse["reference"],
            "summary": verse["summary"],
            "prompts": data["meditation_prompts"],
        },
        "suggestions": [],
    }


@app.get("/api/verses")
def verses() -> dict[str, Any]:
    data = load_data()
    return {"verses": data["verses"]}


@app.get("/api/perspectives")
def perspectives() -> dict[str, Any]:
    data = load_data()
    return {"perspectives": data["perspectives"]}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
