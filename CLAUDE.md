세션이 시작되거나 기존 섹션에서 새로운 세션으로 변경되면 항상 이 문서의 내용을 참고하고 나를 권부장님 이라고 불러주고 항상 한국어로 대답해야한다.

너는 Django 프레임워크의 프론트 엔드 및 백엔드 전문개발자이이며 아래에 설명하믄 


## 1. 시스템 아키텍처

### 1.1 기술 스택
- **Backend**: Django 5
- **Frontend**: HTML5, CSS3, JQuery, Ajax
- **Database**: MariaDB (UTF8MB4)
- **Web Server**: Nginx
- **Container**: Docker
- **Python**: 3.12

### 기술 스택 제한
본 프로젝트는 **전통적인 Django CRUD 방식**으로 MVT 형식으로 개발되어야 하며, 다음 기술만 사용 가능합니다:

#### ✅ 허용된 기술
- **Backend**: Django 5 (MVT 패턴)
- **Database**: MariaDB 10.11
- **Frontend**: 
  - Django Templates (서버사이드 렌더링)
  - Bootstrap 5 (CSS 프레임워크)
  - **jQuery 3.6+ (DOM 조작) - AJAX는 jQuery.ajax()만 사용**
  - AJAX (비동기 통신, jQuery.ajax() 사용)
- **인증**: Django 내장 인증 시스템 (django.contrib.auth)
- **Form**: Django Forms / ModelForm
- **환경**: Docker Compose (django, mariadb, nginx 컨테이너만)
- **진행률 표시**: Bootstrap Progress Bar (필수 사용)
- ~~**차트**: Chart.js~~ (사용 금지 - Bootstrap 컴포넌트로 충분)

#### ❌ 금지된 기술
- REST API Framework (DRF)
- React, Vue, Angular 등 SPA 프레임워크
- Redis, Celery, RabbitMQ 등 메시지 큐
- WebSocket, Server-Sent Events
- PWA, Service Worker
- GraphQL
- 외부 인증 서비스 (OAuth, JWT 등)
- NoSQL 데이터베이스
- 마이크로서비스 아키텍처
- **❌ HTMX 사용 절대 금지 (jQuery AJAX만 사용)**

### 1.2 공통 모달 및 알람 메세지 처리 방식
이 프로젝트에서는 해당 페이지네에서 수행되는 CRUD 작업과 관련된 이벤트를 처리할 때 사정에 정의된 공통 모달창을 사용하고 해당 창에서 표시 해야할 메세지 창은 화면 중앙에 공통 토스트 메세지 창을 구현하여 기본 브라우처 알람창을 대신하도록 한고,
파일 위치는 아래와 같이 위치 시키고 base.html 파일로 모든 창에 해당 모달창과 토스트 메세지 창을 사용 하도록 한다.
- **JavaScript 컴포넌트**: `/static/js/modal.js`
- **자동 로드**: `base.html`에 포함되어 모든 페이지에서 사용 가능
## 사용 가능한 함수
### 1. showDetailModal (상세 정보 표시)
### 2. showEditModal (수정 폼)
### 3. showCreateModal (생성 폼)
### 4. showDeleteModal (삭제 확인)
### 5. showCustomModal (커스텀 모달)


## 주요 특징
- 📋 **통일된 디자인**: Bootstrap 5 기반의 일관된 UI
- 🎨 **커스터마이징 가능**: 크기, 색상, 버튼 등 유연한 설정
- 📊 **테이블 형식 지원**: 구조화된 정보 표시
- 🔄 **재사용성**: 한 번 정의로 모든 템플릿에서 사용

### 1.3 프로젝트 구조

#### 전체 디렉토리 구조
```
racing/                              # 프로젝트 루트
├── docker/                          # Docker 설정 파일들
│   ├── django/
│   │   ├── Dockerfile               # Django 컨테이너 빌드 파일
│   │   └── scripts/
│   │       ├── entrypoint.sh        # Django 컨테이너 시작 스크립트
│   │       ├── settings.py          # Django 기본 설정
│   │       ├── urls.py              # Django 기본 URL 설정
│   │       └── create_secrets.py    # 시크릿 키 생성 스크립트
│   ├── mariadb/
│   │   ├── init.sql                 # DB 초기화 SQL
│   │   └── my.cnf                   # MariaDB 설정
│   └── nginx/
│       ├── nginx.conf               # Nginx 기본 설정
│       └── sites-enabled/
│           └── racing               # 사이트별 Nginx 설정
├── docker-compose.yml               # Docker Compose 설정
├── requirements.txt                 # Python 패키지 의존성
├── .env                            # 환경 변수 (비밀 정보 포함)
└── src/                            # Django 애플리케이션 소스
    ├── config/
    │   ├── __init__.py             # PyMySQL 설정
    │   ├── settings.py             # Django 설정
    │   ├── urls.py                 # 루트 URL 설정
    │   └── wsgi.py                 # WSGI 설정
    │
    ├── apps/                       # 커스텀 앱들
    │
    ├── main/                       # 메인 앱 (자동 생성)
    │   ├── static/main/
    │   │   ├── css/
    │   │   ├── js/
    │   │   └── img/
    │   ├── templates/main/
    │   ├── apps.py
    │   ├── models.py
    │   ├── views.py
    │   └── urls.py
    │
    ├── static/                     # 전역 정적 파일
    │   ├── css/
    │   │   └── common.css          # 추가 전역 스타일
    │   ├── js/
    │   │   ├── common.js           # 공통 함수
    │   │   └── modal.js            # 공통 모달창 및 토스트 메시지
    │   └── images/
    │
    ├── templates/                  # 전역 템플릿
    │   └── base.html              # 기본 템플릿
    │
    ├── staticfiles/               # 수집된 정적 파일 (자동 생성)
    ├── media/                     # 업로드 파일
    ├── logs/                      # 로그 파일
    ├── run/                       # Unix 소켓 파일
    ├── manage.py                  # Django 관리 명령
    ├── secrets.json              # 시크릿 키 (자동 생성)
    ├── CLAUDE.md                  # 이 파일
    └── 경마예측개발계획서.txt        # 개발 계획서
```

#### Docker 컨테이너 구조
```
┌─────────────────────────────────────────┐
│               Nginx Proxy                │
│         (Port: 8081 → 80)               │
│    - 정적 파일 서빙                        │
│    - 프록시 패싱                          │
│    - 로드 밸런싱                          │
└─────────────┬───────────────────────────┘
              │ Unix Socket
              │ /var/www/html/racing/run/racing.sock
┌─────────────▼───────────────────────────┐
│            Django Web                    │
│         (Gunicorn + Django 5)           │
│    - MVT 패턴 웹 애플리케이션                │
│    - API 엔드포인트                        │
│    - 비즈니스 로직 처리                     │
└─────────────┬───────────────────────────┘
              │ MySQL Protocol
              │ Host: db, Port: 3306
┌─────────────▼───────────────────────────┐
│           MariaDB 10.6                   │
│         (Port: 3301 → 3306)             │
│    - UTF8MB4 캐릭터셋                     │
│    - 타임존: Asia/Seoul                   │
│    - 쿼리 캐시 활성화                      │
└─────────────────────────────────────────┘
```

### 1.4 개발 환경 설정

#### 시스템 환경 (.env 파일 기준)
- **프로젝트명**: racing
- **웹 포트**: 8081 (http://localhost:8081/)
- **DB 포트**: 3301 (외부 접속용)
- **관리자 페이지**: http://localhost:8081/admin/
- **시스템**: WSL2 최적화 설정
- **타임존**: Asia/Seoul (한국 표준시)
- **언어**: 한국어 (ko_KR.UTF-8)

#### Docker 컨테이너 정보
- **Django Web**: racing_web (Python 3.12, Django 5.0)
- **MariaDB**: racing_db (MariaDB 10.6)
- **Nginx**: racing_nginx (mainline-alpine)
- **네트워크**: app_network (bridge)

#### 주요 기술 스택
- **Backend**: Django 5.0 + Gunicorn
- **Database**: MariaDB 10.6 (UTF8MB4)
- **Web Server**: Nginx (Unix Socket 연결)
- **Python**: 3.12 (가상환경 사용)
- **Container**: Docker + Docker Compose

### 1.5 개발 워크플로우

#### Docker 명령어
```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 재시작 (코드 변경 후)
docker-compose restart web

# 컨테이너 중지
docker-compose down

# 로그 확인
docker-compose logs -f web

# Django 관리 명령 실행
docker-compose exec web python manage.py [명령어]

# 데이터베이스 접속
docker-compose exec db mysql -u racing -p racing
```

#### 개발 절차
1. **코드 수정**: src/ 폴더 내 파일 수정
2. **변경사항 확인**: 자동으로 반영 (DEBUG=True 환경)
3. **모델 변경 시**: 
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```
4. **정적 파일 변경 시**: 
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```
5. **새 패키지 설치 시**: requirements.txt 수정 후 컨테이너 재빌드
   ```bash
   docker-compose up -d --build
   ```

#### 파일 권한 및 위치
- **소스 파일**: /home/kwonbee/racing/src/ (호스트)
- **컨테이너 내부**: /var/www/html/racing/ (컨테이너)
- **Unix 소켓**: /var/www/html/racing/run/racing.sock
- **로그 파일**: /var/www/html/racing/logs/
- **정적 파일**: /var/www/html/racing/staticfiles/


## 2. 개발 목적
### 2.1 목적 : 이 프로젝트는 한국마사회의 경마 결과를 API 키값으로 받아와서 향후 진행될 경주의 예측값을 측정하는 프로젝트이다.
### 2.2 API : 
* 마사회로 부터 제공 받는 데이타의 요청 조건 : 한국마사회 서울, 부산경남, 제주 경마장에서 시행된 경주에 대한 정보를 제공합니다. (제공정보는 경주조건에 해당하는 시행경마장명, 경주일자, 경주요일, 경주번호, 경주일수, 경주거리, 등급조건, 부담구분, 경주조건, 연령조건, 상별조건, 날씨, 주로, 경주명, 1착상금, 2착상금, 3착상금, 4착상금, 5착상금, 부가상금1, 부가상금2, 부가상금3 자료와 출전마의 정보와 경주결과에 해당하는 순위, 출주번호, 마명, 영문마명, 마번, 국적, 연령, 성별, 부담중량, 레이팅(등급), 기수명, 영문기수명, 기수번호, 조교사명, 영문조교사명, 조교사번호, 마주명, 영문마주명, 마주번호, 경주기록, 마체중, 착차 경주로 구간별 기록 자료를 제공합니다.) - 경주연도/경주년월/경주일자 중 요청변수로 아무것도 입력하지 않았을 경우에는 가장 최근 경주일자 기준 한달 간의 정보를 표출합니다.
* 한국마사회 서울, 부산경남, 제주 경마장에서 시행된 경주에 대한 성적정보를 제공합니다. (제공정보는 경마장, 경주일자, 경주요일, 경주번호, 경주일수, 경주거리, 등급조건, 부담구분, 경주조건, 연령조건, 날씨, 주로, 경주명, 1착상금, 2착상금, 3착상금, 4착상금, 5착상금, 부가상금1, 부가상금2, 부가상금3, 순위, 순위비고, 출주번호, 마명, 마번, 국적, 연령, 생년월일, 성별, 부담중량, 레이팅(등급), 기수명, 기수번호, 조교사명, 조교사번호, 마주명, 마주번호, 경주기록, 마체중, 도착차, S1F순위, 부경G8F_서울제주1C, 부경G6F_서울제주2C, 부경G4F_서울제주3C, 부경G3F_서울제주4C, 부경G2F, G1F순위, S1F기록, 1C기록, 2C기록, 3C기록, 4C기록, 부경400, G3F기록, 부경G2F, G1F기록, 단승식 배당율, 연승식 배당율, 승군순위, 기수감량, 장구내역, 부담중량신청표기 자료입니다.)

※ 요약어 추가설명

F (FURLONG) : 200미터 구간
C (CORNER) : 곡선주로 구간
S1F : 출발지 기준 200미터 구간
G1F : 도착지 기준 200미터 구간
G3F : 도착지 기준 600미터 구간
* 한국마사회 서울, 부산경남, 제주 경마장의 현역 경주마 정보를 제공합니다. (제공자료는 시행경마장명, 마명, 마번, 출생지, 성별, 생년월일, 등급, 조교사명, 조교사번호, 마주명, 마주번호, 마명, 마번, 모마명, 모마번, 통산총출주회수, 통산1착회수, 통산2착회수, 통산3착회수, 최근1년총출주회수, 최근1년1착회수, 최근1년2착회수, 최근1년3착회수, 통산착순상금, 레이팅, 최근거래가 자료입니다) - 요청메세지 경마장구분(meet)에 아무런 값도 입력하지 않았을 경우에는 1(서울)이 기본값으로 요청메시지에 설정됩니다.

* 서울, 부산경남, 제주 경마공원에서 시행예정인 경주계획표 (경주일자, 경주번호, 경주차수등) - 요청메시지 중 경주년, 경주월, 경주일 등의 날짜 변수를 모두 누락한 경우에는 경주일자 기준 최근 한달간의 정보가 표출됩니다. - 요청메시지중 meet(시행경마장)을 생략하면 해당 검색 경주일자 조건의 모든 경마계획정보가 표출됩니다.

### 2.2 현실작업의 흐름 : 마사회 사이트로 부터 한국마사회 경주계획표,한국마사회 경주마 상세정보,한국마사회_경주성적정보,한국마사회 경주기록 정보 정보를 가져와서 다음 경기 결과를 예측하는 프로그램을 만들것이다.

### 2.3 전략 : 딥서치, 딥추론 기능을 이용해서 승리 확율을 예측하는 로직을 만드는 일이다. 이 로직은 지속적인 실제 결과값을 업데이트로 제공함으로 해서 예측 로직의 결과와 실제 결과의 차이가 어디서 발생했는지 분석하는 분석한 내용을 다음 경기에 예측에 활용 할 수 있는 시스템으로 개발 해야한다.

## 3. 데이터베이스 및 성능 설정

### 3.1 MariaDB 설정 (my.cnf)
```ini
[mysqld]
# 문자셋 및 타임존
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
default-time-zone = '+9:00'

# 성능 설정
max_connections = 200
max_allowed_packet = 512M
innodb_buffer_pool_size = 512M
innodb_log_file_size = 128M
query_cache_size = 32M

# 느린 쿼리 로그
slow_query_log = 1
long_query_time = 2
```

### 3.2 Nginx 성능 설정
```nginx
# 워커 프로세스 최적화
worker_processes auto;
worker_connections 4096;

# 파일 크기 제한
client_max_body_size 500M;

# 정적 파일 캐싱
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Unix 소켓 연결
proxy_pass http://racing_backend;
```

### 3.3 Django 설정 정보
```python
# settings.py 주요 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'racing',
        'USER': 'racing',
        'HOST': 'db',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_TZ = True
```

## 4. 한국마사회 API 설정

### 4.1 API 인증 정보
```python
API_KEY = "95c3f0cdaf9f7b1d450b16dbda6480a9b7472e093d4fd0a63204fc006e4bd202"
BASE_URL = "https://apis.data.go.kr/B551015"
```

### 4.2 주요 API 엔드포인트

#### 한국마사회 경주계획표
- **End Point**: https://apis.data.go.kr/B551015/API72_2
- **데이터 포맷**: JSON+XML
- **용도**: 경주 일정 및 기본 정보

#### 한국마사회 경주마 상세정보  
- **End Point**: https://apis.data.go.kr/B551015/API8_2
- **데이터 포맷**: JSON+XML
- **용도**: 경주마별 상세 정보 및 성적

#### 한국마사회 경주성적정보
- **End Point**: https://apis.data.go.kr/B551015/API214_1
- **데이터 포맷**: JSON+XML  
- **용도**: 경주 결과 및 성적 데이터

#### 한국마사회 경주기록 정보
- **End Point**: https://apis.data.go.kr/B551015/API4_3
- **데이터 포맷**: JSON+XML
- **용도**: 세부 경주 기록 및 통계

## 5. 개발 가이드라인 및 절차

### 5.1 필수 개발 절차
1. **CLAUDE.md 파일 우선 참조**: 세션 시작 시 항상 확인
2. **권부장님 호칭**: 모든 대화에서 한국어 사용
3. **기술 스택 준수**: 허용된 기술만 사용 (Django MVT, Bootstrap 5, jQuery)
4. **금지 기술 엄수**: HTMX, DRF, React 등 사용 금지
5. **모달창 활용**: /static/js/modal.js 공통 컴포넌트 사용
6. **Docker 재시작**: 템플릿/백엔드 수정 후 필수

### 5.2 코드 작성 규칙
- UTF8MB4 캐릭터셋 준수
- 한국어 필드명/주석 사용
- Bootstrap 5 컴포넌트 활용
- jQuery 3.6+ AJAX 사용 (jQuery.ajax()만)
- Django Templates 서버사이드 렌더링

### 5.3 프로젝트 진행 순서
1. **Phase 1**: Django 기초 구축 (CRUD, UI)
2. **Phase 2**: ML 모델 개발 (데이터 수집, XGBoost)  
3. **Phase 3**: 실시간 시스템 (WebSocket, 모니터링)
4. **Phase 4**: 성능 최적화 (캐싱, 보안)

이 문서는 프로젝트의 모든 기술적 결정과 개발 절차의 기준이 됩니다.