# newproject

성경 검색 + 관점 제안 + 매일 묵상 샘플 CLI입니다.

## 실행 방법

```bash
python3 src/bible_cli.py search "요한복음 3:16"
python3 src/bible_cli.py today
python3 src/bible_cli.py meditate "로마서 8:28"
python3 src/bible_cli.py --no-color today
```

## API 실행 방법

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn

uvicorn src.api:app --reload
```

### API 예시

```bash
curl "http://127.0.0.1:8000/api/search?query=요한복음%203:16"
curl "http://127.0.0.1:8000/api/today"
curl "http://127.0.0.1:8000/api/meditate?query=로마서%208:28"
```
