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

## 자동 배포 (Docker 이미지)

이 저장소는 `main` 브랜치에 push 되면 GitHub Actions가 자동으로
Docker 이미지를 빌드해서 GHCR(GitHub Container Registry)에 올립니다.

이미지 경로:
`ghcr.io/<OWNER>/bible-cli-api:<TAG>`

예시:

```bash
docker pull ghcr.io/<OWNER>/bible-cli-api:latest
docker run -p 8000:8000 ghcr.io/<OWNER>/bible-cli-api:latest
```
