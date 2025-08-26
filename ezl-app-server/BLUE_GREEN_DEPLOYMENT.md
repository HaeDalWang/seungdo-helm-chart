# 🚀 Argo Rollouts 블루-그린 배포 가이드

## 📋 개요

이 Helm 차트는 Argo Rollouts을 사용한 블루-그린 배포를 지원합니다.

## 🛠️ 사전 준비

### 1. Argo Rollouts Controller 설치
```bash
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
```

### 2. Argo Rollouts CLI 설치 (선택사항)
```bash
# macOS
brew install argoproj/tap/kubectl-argo-rollouts

# Linux
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x ./kubectl-argo-rollouts-linux-amd64
sudo mv ./kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts
```

## 🎯 배포 방법

### 1️⃣ 기본 블루-그린 배포

```bash
# 블루-그린 모드로 배포
helm upgrade --install ezl-app-server . \
  --set rollout.enabled=true \
  --set global.image.tag=v1.0.0 \
  --namespace default
```

### 2️⃣ 설정 파일을 사용한 배포

```bash
# values_bluegreen.yaml 사용
helm upgrade --install ezl-app-server . \
  -f values_bluegreen.yaml \
  --set global.image.tag=v1.1.0 \
  --namespace default
```

### 3️⃣ 자동 분석과 함께 배포

```bash
helm upgrade --install ezl-app-server . \
  --set rollout.enabled=true \
  --set rollout.analysisTemplate.enabled=true \
  --set rollout.strategy.blueGreen.prePromotionAnalysis.enabled=true \
  --set global.image.tag=v1.2.0 \
  --namespace default
```

## 🔍 배포 상태 모니터링

### Rollout 상태 확인
```bash
# 기본 상태 확인
kubectl get rollouts

# 상세 상태 확인
kubectl describe rollout ezl-app-server

# Argo Rollouts CLI 사용 (더 보기 좋음)
kubectl argo rollouts get rollout ezl-app-server
```

### 실시간 모니터링
```bash
# 실시간 상태 확인
kubectl argo rollouts get rollout ezl-app-server --watch

# 대시보드 실행
kubectl argo rollouts dashboard
```

## 🎮 수동 프로모션

### 프리뷰 확인 후 프로모션
```bash
# 1. 프리뷰 서비스로 테스트
kubectl port-forward svc/ezl-app-server-preview 8080:8000

# 2. 테스트 완료 후 프로모션
kubectl argo rollouts promote ezl-app-server

# 3. 또는 kubectl로
kubectl patch rollout ezl-app-server --type merge --patch='{"spec":{"paused":false}}'
```

### 롤백
```bash
# 이전 버전으로 롤백
kubectl argo rollouts undo ezl-app-server

# 특정 리비전으로 롤백
kubectl argo rollouts undo ezl-app-server --to-revision=3
```

## ⚙️ 주요 설정 변수

### 필수 설정
```yaml
rollout:
  enabled: true  # Rollout 활성화

global:
  image:
    tag: "v1.0.0"  # 배포할 이미지 태그
```

### 블루-그린 전략 설정
```yaml
rollout:
  strategy:
    blueGreen:
      autoPromotionEnabled: false    # 자동/수동 프로모션
      scaleDownDelaySeconds: 30      # 이전 버전 제거 지연 시간
      previewReplicaCount: 1         # 프리뷰 환경 파드 수
```

### 자동 분석 설정
```yaml
rollout:
  analysisTemplate:
    enabled: true
    metrics:
      successRate:
        threshold: 0.95    # 95% 성공률
        count: 3           # 3번 체크
        failureLimit: 2    # 2번 실패까지 허용
```

## 🔧 배포 시나리오별 설정

### 1. 개발 환경 (빠른 피드백)
```yaml
rollout:
  enabled: true
  strategy:
    blueGreen:
      autoPromotionEnabled: true     # 자동 프로모션
      scaleDownDelaySeconds: 10      # 빠른 정리
      prePromotionAnalysis:
        enabled: false               # 분석 비활성화
```

### 2. 스테이징 환경 (자동 분석)
```yaml
rollout:
  enabled: true
  strategy:
    blueGreen:
      autoPromotionEnabled: false    # 수동 승인
      prePromotionAnalysis:
        enabled: true                # 분석 활성화
      postPromotionAnalysis:
        enabled: true                # 배포 후 분석
```

### 3. 프로덕션 환경 (최대 안전성)
```yaml
rollout:
  enabled: true
  strategy:
    blueGreen:
      autoPromotionEnabled: false    # 반드시 수동 승인
      scaleDownDelaySeconds: 300     # 5분간 이전 버전 유지
      prePromotionAnalysis:
        enabled: true
      postPromotionAnalysis:
        enabled: true
```

## 🚨 트러블슈팅

### 자주 발생하는 문제

1. **Rollout이 생성되지 않음**
   ```bash
   # Argo Rollouts Controller 확인
   kubectl get pods -n argo-rollouts
   ```

2. **분석이 실패함**
   ```bash
   # 분석 로그 확인
   kubectl logs -l app.kubernetes.io/component=analysis-controller -n argo-rollouts
   
   # Prometheus 연결 확인
   kubectl get analysisrun
   ```

3. **프로모션이 안됨**
   ```bash
   # Rollout 상태 확인
   kubectl argo rollouts get rollout ezl-app-server
   
   # 수동으로 프로모션
   kubectl argo rollouts promote ezl-app-server
   ```

## 📚 참고 자료

- [Argo Rollouts 공식 문서](https://argo-rollouts.readthedocs.io/)
- [블루-그린 배포 가이드](https://argo-rollouts.readthedocs.io/en/stable/features/bluegreen/)
- [Analysis Template 설정](https://argo-rollouts.readthedocs.io/en/stable/features/analysis/)

