# 🐍 EZL App Server - Python Implementation

기존 `log-generator.sh`의 Python 버전으로, 실제 HTTP 서버 기능과 Secrets Store CSI 통합이 추가되었습니다.

## 📋 주요 기능

### 🔄 로그 생성 (백그라운드)
- 기존 bash 스크립트와 동일한 로그 패턴 생성
- 주기적으로 다양한 형태의 로그 출력
- JSON 형태 로그 및 일반 텍스트 로그

### 🔐 Secrets 관리
- `/mnt/secrets-store/` 경로에서 모든 시크릿 파일 읽기
- JSON 파싱 시도 후 실패시 문자열로 저장
- 전체 시크릿 구조를 API로 노출

### 🌐 HTTP API 엔드포인트

| 엔드포인트 | 설명 | 응답 |
|----------|------|------|
| `GET /` | 기본 정보 | 서비스 상태 및 버전 |
| `GET /api/intgapp/ping/` | 헬스체크 | 200 OK |
| `GET /healthz` | Kubernetes 헬스체크 | healthy 상태 |
| `GET /api/secrets` | **전체 시크릿 조회** | 모든 시크릿의 JSON 구조 |
| `GET /api/secrets/<name>` | 특정 시크릿 조회 | 개별 시크릿 값 |
| `GET /api/stats` | 앱 통계 | 카운터, 환경변수 등 |

## 🏗️ 빌드 및 배포

### 1. Docker 이미지 빌드
```bash
cd app/
./build.sh v1.0
```

### 2. 이미지 푸시 (필요시)
```bash
docker push svvwac98/ezl-app-server-python:v1.0
docker push svvwac98/ezl-app-server-python:latest
```

### 3. Helm 배포
```bash
# 개발 환경
helm upgrade --install ezl-app-server . \
  -f values_dev.yaml \
  --set global.image.tag=v1.0 \
  -n dev

# 프로덕션 (블루-그린)
helm upgrade --install ezl-app-server . \
  -f values_prod.yaml \
  --set global.image.tag=v1.0 \
  -n production
```

## 🧪 로컬 테스트

### Docker로 실행
```bash
docker run -p 8000:8000 svvwac98/ezl-app-server-python:v1.0
```

### API 테스트
```bash
# 기본 정보
curl http://localhost:8000/

# 헬스체크
curl http://localhost:8000/api/intgapp/ping/

# 전체 시크릿 조회 (핵심 기능!)
curl http://localhost:8000/api/secrets

# 특정 시크릿 조회
curl http://localhost:8000/api/secrets/DB_PASSWORD

# 앱 통계
curl http://localhost:8000/api/stats
```

## 🔐 Secrets Store 통합

### 지원하는 시크릿 형태
1. **JSON 파일**: 자동으로 파싱하여 객체로 저장
2. **텍스트 파일**: 문자열로 저장
3. **바이너리 파일**: 읽기 오류시 에러 메시지 저장

### 시크릿 조회 API 응답 예시
```json
{
  "secrets_count": 3,
  "secrets_data": {
    "DB_PASSWORD": "super_secret_password",
    "API_KEY": "abcd1234",
    "config.json": {
      "database": {
        "host": "localhost",
        "port": 5432
      }
    }
  },
  "secrets_path": "/mnt/secrets-store",
  "timestamp": "2025-01-25T12:00:00"
}
```

## 📊 로그 출력 예시

### 백그라운드 로그 (기존 bash와 동일)
```
2025-01-25T12:00:00 | INFO | app.py:1 | Application starting... Checking secrets...
2025-01-25T12:00:03 | INFO | app.py:188 | EzlwalkDailyMission Check DailyUserStepCountLog updated: user_id=527972 device_id=603148 last_date=2025-01-25 step_count=2812
2025-01-25T12:00:06 | DEBUG | app.py:75 | hyphen.py:75 | {"sucsFalr": "success", "rsltCd": "HCO000", ...}
```

### HTTP 요청 로그
```
2025-01-25T12:00:09 | INFO | app.py:363 | 10.243.12.131 - - "GET /api/intgapp/ping/ HTTP/1.1" 200 4 | duration=0.001143
```

## 🎯 주요 개선사항

1. **실제 HTTP 서버**: Flask 기반으로 실제 요청 처리
2. **시크릿 전체 읽기**: `/mnt/secrets-store/` 전체 디렉토리 스캔
3. **JSON 지원**: 시크릿이 JSON이면 자동 파싱
4. **API 노출**: 시크릿 정보를 HTTP API로 조회 가능
5. **헬스체크**: Kubernetes 표준 헬스체크 지원
6. **백그라운드 로그**: 기존 로그 패턴 유지하면서 HTTP 서버 병행

이제 **실제 애플리케이션**처럼 동작하면서도 기존 로그 패턴을 유지합니다! 🚀
