#!/bin/bash

echo "=== SSL 인증서 설정 (Let's Encrypt) ==="

# Docker Compose 명령어 자동 감지
COMPOSE_CMD=""
if command -v "docker compose" &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v "docker-compose" &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "❌ Docker Compose가 설치되어 있지 않습니다."
    exit 1
fi

# 필요한 디렉토리 생성
mkdir -p ./ssl
mkdir -p ./certbot

# 1. DNS 확인
echo "🔍 DNS 설정 확인 중..."
if ! nslookup racing.inno.ceo | grep -q "107.173.223.234"; then
    echo "⚠️ DNS가 아직 전파되지 않았습니다."
    echo "잠시 기다린 후 다시 시도해주세요."
    read -p "계속 진행하시겠습니까? (y/n): " continue_ssl
    if [ "$continue_ssl" != "y" ]; then
        exit 1
    fi
fi

# 2. Certbot으로 SSL 인증서 발급
echo "🔐 SSL 인증서 발급 중..."
docker run --rm \
  -v $(pwd)/ssl:/etc/letsencrypt \
  -v $(pwd)/certbot:/var/www/certbot \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  --email kwonbe@naver.com \
  --agree-tos \
  --no-eff-email \
  --force-renewal \
  -d racing.inno.ceo

# 3. 인증서 파일 복사
echo "📋 인증서 파일 복사..."
if [ -d "./ssl/live/racing.inno.ceo" ]; then
    cp ./ssl/live/racing.inno.ceo/fullchain.pem ./ssl/fullchain.pem
    cp ./ssl/live/racing.inno.ceo/privkey.pem ./ssl/privkey.pem
    chmod 644 ./ssl/fullchain.pem
    chmod 644 ./ssl/privkey.pem
    echo "✅ SSL 인증서 설정 완료!"
else
    echo "❌ SSL 인증서 발급 실패!"
    echo "DNS 설정을 확인하고 racing.inno.ceo가 서버 IP를 가리키는지 확인해주세요."
    exit 1
fi

# 4. Nginx 재시작
echo "🔄 Nginx 재시작..."
$COMPOSE_CMD restart nginx

echo ""
echo "🌐 HTTPS 테스트: https://racing.inno.ceo"
echo "🔐 SSL 인증서 확인: openssl s_client -connect racing.inno.ceo:443 -servername racing.inno.ceo"