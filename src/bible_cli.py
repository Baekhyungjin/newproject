#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_data.json"


def load_data() -> dict:
    with DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def find_verse(verses: list[dict], query: str) -> dict | None:
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


def format_separator() -> str:
    return "─" * 60


def print_search(data: dict, query: str) -> None:
    verse = find_verse(data["verses"], query)
    if not verse:
        print("검색 결과가 없습니다.")
        return
    perspective_templates = data["perspectives"][:3]

    print()
    print(format_separator())
    print("📖 본문")
    print(verse["reference"])
    print(verse["text"])
    print()
    print(format_separator())
    print("🧭 관점 제안")
    for index, perspective in enumerate(perspective_templates, start=1):
        print(f"{index}) {perspective['title']}")
        for point in perspective["bullets"]:
            print(f"   - {point}")
    print()
    print(format_separator())
    print("📝 오늘의 묵상")
    meditation = data["meditations"][0]
    print(f"요약: {meditation['summary']}")
    print("적용 질문:")
    for question in meditation["application_questions"]:
        print(f" - {question}")
    print("기도:")
    print(f" - {meditation['prayer']}")
    print()
    print("Tip: `bible today`로 오늘의 묵상을 바로 확인할 수 있습니다.")


def print_today(data: dict) -> None:
    today_str = date.today().isoformat()
    meditation = next(
        (item for item in data["meditations"] if item["date"] == today_str),
        data["meditations"][0],
    )
    print()
    print(format_separator())
    print(f"🗓️ {today_str} 오늘의 묵상")
    print(f"오늘의 말씀: {meditation['reference']}")
    print(f"오늘의 요약: {meditation['summary']}")
    print("오늘의 적용 질문:")
    for question in meditation["application_questions"]:
        print(f" - {question}")
    print("오늘의 기도:")
    print(f" - {meditation['prayer']}")


def print_meditate(data: dict, query: str) -> None:
    verse = find_verse(data["verses"], query)
    if not verse:
        print("묵상할 본문을 찾지 못했습니다.")
        return
    prompts = data["meditation_prompts"]

    print()
    print(format_separator())
    print("🧘 묵상 시작")
    print(f"본문: {verse['reference']}")
    print(f"요약: {verse['summary']}")
    print("묵상 안내:")
    for index, prompt in enumerate(prompts, start=1):
        print(f"{index}. {prompt}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bible", description="Bible CLI sample.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search a verse.")
    search_parser.add_argument("query", help="검색어 또는 참조(예: 요한복음 3:16)")

    subparsers.add_parser("today", help="Show today's meditation.")

    meditate_parser = subparsers.add_parser("meditate", help="Start meditation.")
    meditate_parser.add_argument("query", help="묵상할 본문(예: 로마서 8:28)")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    data = load_data()

    if args.command == "search":
        print_search(data, args.query)
    elif args.command == "today":
        print_today(data)
    elif args.command == "meditate":
        print_meditate(data, args.query)


if __name__ == "__main__":
    main()
