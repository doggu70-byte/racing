#!/bin/bash

echo "=== Racing.inno.ceo 배포 스크립트 ==="

# Docker Compose 명령어 자동 감지
COMPOSE_CMD=""
if command -v "docker compose" &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "✅ Docker Compose V2 감지"
elif command -v "docker-compose" &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "✅ Docker Compose V1 감지"
else
    echo "❌ Docker Compose가 설치되어 있지 않습니다."
    exit 1
fi

# 1. 환경 변수 확인
if [ ! -f .env ]; then
    echo "⚠️ .env 파일이 없습니다. .env.example을 복사합니다."
    cp .env.example .env
    echo "🔧 .env 파일을 수정해주세요."
    exit 1
fi

# 2. 기존 컨테이너 중지
echo "🛑 기존 컨테이너 중지 중..."
$COMPOSE_CMD down 2>/dev/null || true

# 3. Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
$COMPOSE_CMD build --no-cache

# 4. 데이터베이스 시작
echo "🗄️ 데이터베이스 시작 중..."
$COMPOSE_CMD up -d db

# 잠시 대기
echo "⏳ 데이터베이스 초기화 대기 (30초)..."
sleep 30

# 5. 데이터베이스 마이그레이션
echo "📊 데이터베이스 마이그레이션 실행..."
$COMPOSE_CMD run --rm web python manage.py migrate

# 6. 정적 파일 수집
echo "📁 정적 파일 수집 중..."
$COMPOSE_CMD run --rm web python manage.py collectstatic --noinput

# 7. 관리자 계정 생성 (선택사항)
echo "👤 관리자 계정을 생성하시겠습니까? (y/n)"
read -r create_admin
if [ "$create_admin" = "y" ]; then
    $COMPOSE_CMD run --rm web python manage.py createsuperuser
fi

# 8. 모든 서비스 시작
echo "🚀 모든 서비스 시작 중..."
$COMPOSE_CMD up -d

# 9. 서비스 상태 확인
echo "📊 서비스 상태 확인..."
$COMPOSE_CMD ps

echo ""
echo "✅ 배포 완료!"
echo "🌐 서비스 주소: http://racing.inno.ceo"
echo "🔧 관리자 페이지: http://racing.inno.ceo/admin/"
echo ""
echo "📊 로그 확인: $COMPOSE_CMD logs -f"
echo "🛑 서비스 중지: $COMPOSE_CMD down"
echo "🔄 서비스 재시작: $COMPOSE_CMD restart"