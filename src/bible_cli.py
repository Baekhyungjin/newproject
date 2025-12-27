#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_data.json"

COLORS = {
    "reset": "\033[0m",
    "heading": "\033[96m",
    "accent": "\033[92m",
    "muted": "\033[90m",
}


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


def colorize(text: str, tone: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{COLORS[tone]}{text}{COLORS['reset']}"


def suggest_verses(verses: list[dict], query: str, limit: int = 3) -> list[dict]:
    tokens = {token for token in query.strip().split() if token}

    def score(verse: dict) -> int:
        verse_text = f"{verse['reference']} {verse['text']}"
        return sum(1 for token in tokens if token in verse_text)

    ranked = sorted(verses, key=score, reverse=True)
    return [verse for verse in ranked if score(verse) > 0][:limit]


def print_search(data: dict, query: str, use_color: bool) -> None:
    verse = find_verse(data["verses"], query)
    if not verse:
        print("검색 결과가 없습니다.")
        suggestions = suggest_verses(data["verses"], query)
        if suggestions:
            print(colorize("추천 구절:", "muted", use_color))
            for suggestion in suggestions:
                print(f" - {suggestion['reference']} {suggestion['text']}")
        return
    perspective_templates = data["perspectives"][:3]

    print()
    print(format_separator())
    print(colorize("📖 본문", "heading", use_color))
    print(verse["reference"])
    print(verse["text"])
    print()
    print(format_separator())
    print(colorize("🧭 관점 제안", "heading", use_color))
    for index, perspective in enumerate(perspective_templates, start=1):
        print(f"{index}) {colorize(perspective['title'], 'accent', use_color)}")
        for point in perspective["bullets"]:
            print(f"   - {point}")
    print()
    print(format_separator())
    print(colorize("📝 오늘의 묵상", "heading", use_color))
    meditation = data["meditations"][0]
    print(f"요약: {meditation['summary']}")
    print("적용 질문:")
    for question in meditation["application_questions"]:
        print(f" - {question}")
    print("기도:")
    print(f" - {meditation['prayer']}")
    print()
    print("Tip: `bible today`로 오늘의 묵상을 바로 확인할 수 있습니다.")


def pick_today_meditation(data: dict, today: date) -> dict:
    meditation = next(
        (item for item in data["meditations"] if item["date"] == today.isoformat()),
        None,
    )
    if meditation:
        return meditation
    index = today.toordinal() % len(data["meditations"])
    return data["meditations"][index]


def print_today(data: dict, use_color: bool) -> None:
    today_str = date.today().isoformat()
    meditation = pick_today_meditation(data, date.today())
    print()
    print(format_separator())
    print(colorize(f"🗓️ {today_str} 오늘의 묵상", "heading", use_color))
    print(f"오늘의 말씀: {meditation['reference']}")
    print(f"오늘의 요약: {meditation['summary']}")
    print("오늘의 적용 질문:")
    for question in meditation["application_questions"]:
        print(f" - {question}")
    print("오늘의 기도:")
    print(f" - {meditation['prayer']}")


def print_meditate(data: dict, query: str, use_color: bool) -> None:
    verse = find_verse(data["verses"], query)
    if not verse:
        print("묵상할 본문을 찾지 못했습니다.")
        suggestions = suggest_verses(data["verses"], query)
        if suggestions:
            print(colorize("추천 구절:", "muted", use_color))
            for suggestion in suggestions:
                print(f" - {suggestion['reference']} {suggestion['text']}")
        return
    prompts = data["meditation_prompts"]

    print()
    print(format_separator())
    print(colorize("🧘 묵상 시작", "heading", use_color))
    print(f"본문: {verse['reference']}")
    print(f"요약: {verse['summary']}")
    print("묵상 안내:")
    for index, prompt in enumerate(prompts, start=1):
        print(f"{index}. {prompt}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bible", description="Bible CLI sample.")
    parser.add_argument("--no-color", action="store_true", help="컬러 출력을 끕니다.")
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
    use_color = not args.no_color

    if args.command == "search":
        print_search(data, args.query, use_color)
    elif args.command == "today":
        print_today(data, use_color)
    elif args.command == "meditate":
        print_meditate(data, args.query, use_color)


if __name__ == "__main__":
    main()
