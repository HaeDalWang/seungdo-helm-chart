#!/bin/bash

# EZL App Server Python 앱 멀티 아키텍처 빌드 스크립트
# AMD64 (x86_64) + ARM64 (Apple Silicon, ARM servers) 지원

set -e

# 변수 설정
IMAGE_NAME="svvwac98/ezl-app-server-python"
VERSION=${1:-"v1.0"}  # 첫 번째 인자로 버전 지정, 기본값은 v1.0
PLATFORM="linux/amd64,linux/arm64"

echo "🐍 Building EZL App Server Python image (Multi-Architecture)..."
echo "📦 Image: ${IMAGE_NAME}:${VERSION}"
echo "🏗️  Platforms: ${PLATFORM}"

# Docker Buildx 활성화 확인
if ! docker buildx version >/dev/null 2>&1; then
    echo "❌ Docker Buildx not available. Please enable Docker Buildx."
    exit 1
fi

# 빌더 인스턴스 생성 또는 사용
BUILDER_NAME="multiarch-builder"
if ! docker buildx inspect ${BUILDER_NAME} >/dev/null 2>&1; then
    echo "🔧 Creating multiarch builder..."
    docker buildx create --name ${BUILDER_NAME} --driver docker-container --bootstrap
fi

echo "🚀 Using builder: ${BUILDER_NAME}"
docker buildx use ${BUILDER_NAME}

# 멀티 아키텍처 빌드 및 푸시
echo "🏗️  Building and pushing multi-architecture image..."
docker buildx build \
    --platform ${PLATFORM} \
    --tag ${IMAGE_NAME}:${VERSION} \
    --tag ${IMAGE_NAME}:latest \
    --push \
    .

echo "✅ Multi-architecture build completed!"
echo "📋 Built for platforms: ${PLATFORM}"

echo ""
echo "🔍 To inspect the image:"
echo "   docker buildx imagetools inspect ${IMAGE_NAME}:${VERSION}"

echo ""
echo "🧪 To test locally:"
echo "   # AMD64:"
echo "   docker run --platform linux/amd64 -p 8000:8000 ${IMAGE_NAME}:${VERSION}"
echo "   # ARM64:"
echo "   docker run --platform linux/arm64 -p 8000:8000 ${IMAGE_NAME}:${VERSION}"

echo ""
echo "📡 Images pushed to registry:"
echo "   ${IMAGE_NAME}:${VERSION}"
echo "   ${IMAGE_NAME}:latest"
