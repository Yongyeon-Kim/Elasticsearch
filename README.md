# 🔍 Django + Elasticsearch 문서 검색 시스템 구성 가이드

## 📁 디렉터리 구조

```
.
├── Dockerfile                    # Django 앱 빌드용 Docker 설정
├── README.md                     # 프로젝트 설명서
├── csv_KCS.csv                   # KCS 문서 데이터 (CSV)
├── csv_KDS.csv                   # KDS 문서 데이터 (CSV)
├── db.sqlite3                    # SQLite DB (PostgreSQL 대신 테스트용 가능)
├── docker-compose.yaml           # 전체 서비스 도커 컴포지션 정의
├── manage.py                     # Django 명령줄 관리 도구
├── requirements.txt              # 프로젝트 의존 패키지 목록
├── search_app/                   # 문서 검색 기능 관련 앱
│   ├── __init__.py
│   ├── apps.py                   # 앱 등록 정보
│   ├── documents.py              # Elasticsearch용 문서 정의
│   ├── management/commands/      # 커맨드: load_csv
│   │   └── load_csv.py           # CSV 데이터를 모델로 삽입하는 스크립트
│   ├── migrations/               # DB 마이그레이션 기록
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py                 # StandardDoc 모델 정의
│   ├── templates/search_app/     # 검색 결과 HTML 템플릿 (search.html)
│   ├── urls.py                   # 이 앱의 URL 라우팅
│   └── views.py                  # 검색 뷰 로직 정의
├── search_project/               # Django 프로젝트 설정
│   ├── __init__.py
│   ├── settings.py               # 전체 프로젝트 설정
│   ├── urls.py                   # 전체 URL 라우팅
│   └── wsgi.py                   # WSGI 서버 진입점
├── static/                       # 정적 파일 (이미지, CSS 등)
│   └── 한맥기술_좌우_국문.png     # 삽입한 회사 로고 이미지
└── wait-for-it.sh                # DB 컨테이너 대기 스크립트
```

---

## 🛠️ 데이터 처리 명령어

```bash
# 1. 마이그레이션 파일 생성
docker exec -it django_elasticsearch-web-1 python manage.py makemigrations search_app

# 2. 데이터베이스에 테이블 생성
docker exec -it django_elasticsearch-web-1 python manage.py migrate

# 3. CSV 데이터를 DB에 삽입
docker exec -it django_elasticsearch-web-1 python manage.py load_csv

# 4. Elasticsearch 인덱스를 재생성하고 색인화
docker exec -it django_elasticsearch-web-1 python manage.py search_index --rebuild

# 참고. 데이터베이스 초기화
docker exec -it django_elasticsearch-web-1 python manage.py flush -> 'yes'
docker compose down -v
docker compose up -d
```

| 명령어                          | 설명                                              |
|-------------------------------|---------------------------------------------------|
| `makemigrations`              | 모델 변경사항 추적, 마이그레이션 파일 생성       |
| `migrate`                     | 마이그레이션 파일을 기반으로 DB에 테이블 생성     |
| `load_csv`                    | CSV(KCS/KDS) 파일 데이터를 DB에 삽입              |
| `search_index --rebuild`      | 기존 색인 제거 후 인덱스 생성 및 데이터 색인      |

---

## ✅ Elasticsearch 색인 상태 확인

```bash
curl -X GET http://localhost:9200/_cat/indices?v
```

예시 출력:
```
health status index         uuid      pri rep docs.count docs.deleted store.size
yellow open   standard_docs abc123... 1   1     1890          0        43.5mb
```

---

## ✅ 슈퍼유저 생성 (관리자 페이지 접속용)

```bash
docker exec -it django_elasticsearch-web-1 python manage.py createsuperuser
```

접속: [http://localhost:9100/admin](http://localhost:9100/admin)

---

## 🔍 검색 페이지 접속

- 일반 사용자 검색 UI: [http://localhost:9100](http://localhost:9100)

---

## 📦 Elasticsearch 직접 쿼리 테스트

```bash
curl -X POST "http://localhost:9200/standard_docs/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "multi_match": {
        "query": "건축",
        "fields": ["name", "contents"]
      }
    }
  }'
```

| 필드 이름            | 설명                                      |
|----------------------|-------------------------------------------|
| `_index`             | 인덱스 이름 (`standard_docs`)             |
| `_score`             | 검색 관련도 점수 (높을수록 상위 노출됨)   |
| `_source.code_type`  | 문서 분류 (KCS, KDS 등)                   |
| `_source.code`       | 문서 고유 코드 번호                       |
| `_source.name`       | 문서 제목                                 |
| `_source.contents`   | 문서 내용 전문                            |

---

## 🎨 UI 기능 요약 (`search.html`)

| 기능                  | 설명                                                       |
|-----------------------|------------------------------------------------------------|
| ✅ 검색어 하이라이팅  | 검색어가 노란색으로 강조됨 (`highlight` 사용)              |
| ✅ 실시간 검색        | 입력 시 자동으로 결과 반영 (JavaScript `fetch`)            |
| ✅ 페이지네이션       | 검색 결과가 많을 경우 페이지 이동 지원                      |
| ✅ 회사 로고 삽입     | `/static/` 경로의 이미지 출력 (`한맥기술_좌우_국문.png`)    |