# Direct AI Media App 구현 가이드

이 저장소는 프롬프트 작성 → 이미지 생성 → SORA2 영상 요청의 3단계 파이프라인을 빠르게 프로토타이핑하기 위한 예제입니다. 아래 절차를 따르면 목업 상태의 프론트를 실제 서비스로 전환할 수 있습니다.

## 1. 시스템 아키텍처 설계
1. **프론트엔드**: 현재 `index.html`은 Tailwind CDN을 활용한 정적 앱입니다. Vite/Next.js 등으로 마이그레이션하면 상태 관리와 라우팅을 확장하기 쉽습니다.
2. **백엔드 게이트웨이**: 프롬프트, 이미지, 영상 생성 요청을 대행할 REST API를 준비합니다. Node.js(Express/Fastify) 또는 Python(FastAPI) 기반으로 구축하면 빠르게 프로토타이핑할 수 있습니다.
3. **AI 공급자 연동**:
   - **프롬프트 보조**: GPT 계열 모델을 호출해 사용자 입력을 정제합니다.
   - **이미지 생성**: DALL·E, Stable Diffusion API, 또는 자체 호스팅 모델을 호출합니다.
   - **SORA2 영상**: SORA2가 제공하는 비디오 생성 API 엔드포인트를 비동기 잡 형태로 호출하고, 완료 웹훅을 수신합니다.
4. **미디어 저장소**: 생성된 이미지/영상은 S3, Cloud Storage 등에 업로드하고, 프론트에는 서명된 URL을 전달합니다.

## 2. 백엔드 API 설계
| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/prompts` | POST | `{ idea, style, mood, camera, ratio, extra }`를 받아 LLM으로 확장 프롬프트 생성 |
| `/api/images` | POST | `{ prompt }`를 받아 이미지 생성 후 `imageUrl` 반환 |
| `/api/videos` | POST | `{ prompt }`를 받아 SORA2 작업을 생성하고 `jobId` 즉시 반환 |
| `/api/videos/:jobId` | GET | 작업 상태 및 완료 시 `videoUrl` 전달 |
| `/webhooks/sora2` | POST | SORA2 완료 알림을 수신하여 DB 상태 갱신 |

### 예시: FastAPI 스켈레톤
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PromptPayload(BaseModel):
    idea: str
    style: str
    mood: str
    camera: str
    ratio: str
    extra: str | None = None

@app.post('/api/prompts')
async def generate_prompt(payload: PromptPayload):
    prompt = await call_llm(payload)
    return {"prompt": prompt}
```
각 엔드포인트에서는 인증 토큰 검증, 레이트 리밋, 오류 처리 로직을 추가합니다.

## 3. 프론트엔드 연동
1. `index.html`의 `API_ENDPOINTS`를 실제 백엔드 URL로 변경하고, `USE_MOCK_API = false` 설정합니다.
2. 이미지/영상 요청은 비동기 처리 시간이 길 수 있으므로 **폴링** 또는 **웹소켓**으로 상태를 갱신합니다.
3. Tailwind CDN 대신 빌드 툴을 사용하면 환경 변수(`VITE_API_BASE_URL`)로 엔드포인트를 관리하고, 토큰 기반 인증 헤더를 자동으로 주입할 수 있습니다.
4. SORA2 영상은 인코딩 시간이 길기 때문에 “대기열에 등록되었습니다” 메시지와 진행률 UI를 구성합니다.

## 4. 인증 및 권한
- 백엔드는 JWT 또는 세션 기반 인증을 적용합니다.
- 이미지/영상 생성 비용이 크므로, 사용자 단위 쿼터/크레딧 관리 로직을 추가합니다.
- 관리자 페이지에서 작업 내역을 모니터링할 수 있도록 로그를 저장합니다.

## 5. 배포 전략
1. **프론트**: GitHub Pages, Netlify, Vercel 등에서 정적 파일을 호스팅합니다.
2. **백엔드**: Render, Railway, AWS Elastic Beanstalk 등 컨테이너 기반 서비스를 이용하거나 Kubernetes 클러스터에 배포합니다.
3. **CI/CD**: GitHub Actions로 테스트 → 빌드 → 배포 파이프라인을 자동화합니다.
4. **관찰성**: Sentry, Datadog, Prometheus를 통해 오류/성능을 모니터링합니다.

## 6. 운영 팁
- 실제 API 키는 `.env` 등 비공개 스토리지에 보관하고, 클라이언트에 직접 노출하지 않습니다.
- 프롬프트, 이미지, 영상 기록을 DB에 저장하여 히스토리를 제공하고, 재생성 기능을 지원합니다.
- SORA2 API 정책과 사용 제한을 미리 파악하여 사용자에게 명확히 안내합니다.

이 가이드를 기반으로 백엔드와 인프라를 구축하고 `index.html`의 목업 호출을 실제 API로 연결하면, 프로덕션 수준의 Direct AI Media App을 완성할 수 있습니다.
