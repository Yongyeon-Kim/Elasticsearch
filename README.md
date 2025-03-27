# 🔍 Elasticsearch 문서 검색 시스템 구성 가이드

---

## 📁 디렉터리 구조

```
.
├── docker-compose.yml               # Elasticsearch + Python 컨테이너 구성
├── Dockerfile                       # Python 환경 빌드 (elasticsearch-py 설치 포함)
├── requirements.txt                 # Python 의존 패키지 (elasticsearch, pandas 등)
├── data/                            # 문서 데이터
├── load_to_es.py                    # CSV → Elasticsearch 색인 스크립트
├── search_from_es.py                # 검색어 입력 후 결과 출력 스크립트
└── README.md                        # 사용 설명서
```

---

## ▶️ 실행 방법

```bash
# 1. 컨테이너 빌드 및 실행
docker compose up -d

# 2. 컨테이너 접속
docker exec -it es_only_search bash

# 3. Elasticsearch 색인 실행
python load_to_es.py

# 4. 검색 테스트 실행
python search_from_es.py
```

---

## 🧱 컨테이너 구성 설명

| 컨테이너 이름    | 역할                          | 주요 기능                                              |
| ---------------- | ----------------------------- | ------------------------------------------------------ |
| `elasticsearch`  | Elasticsearch 서버            | 문서 색인 및 검색 기능 제공 (REST API: 9200 포트 사용) |
| `es_only_search` | Python 실행 환경 (클라이언트) | CSV 데이터 색인, 검색어 입력 후 검색 결과 출력         |

---

## 🧠 Elasticsearch 개요

Elasticsearch는 대규모 문서 기반 데이터를 빠르게 색인하고 검색할 수 있는 **오픈소스 검색 엔진**입니다.  
`RESTful API` 기반으로 동작하며, Python에서는 `elasticsearch-py` 라이브러리를 통해 접근할 수 있습니다.

| 용어           | 의미                                           |
| -------------- | ---------------------------------------------- |
| 색인(Index)    | 문서들이 저장되는 공간 (DB의 테이블 개념)      |
| 문서(Document) | 색인된 단위 데이터 (JSON 형식)                 |
| 필드(Field)    | 문서 내의 개별 속성 (예: code, name, contents) |
| 질의(Query)    | 문서를 검색하기 위한 조건 (검색어, 필터 등)    |

---

## 📌 Elasticsearch 색인 흐름

`load_to_es.py` 스크립트를 실행하면 다음과 같은 과정으로 문서가 색인됩니다:

```
CSV 파일 → Pandas DataFrame → Python dict → Elasticsearch.index() → standard_docs 인덱스에 저장
```

---

## 📄 색인 코드 분석 (`load_to_es.py`)

```python
es = Elasticsearch("http://elasticsearch:9200")

def index_csv(file_path, code_type):
    df = pd.read_csv("data/" + file_path)
    for _, row in tqdm(df.iterrows(), total=len(df)):
        doc = {
            "code_type": code_type,
            "code": row.get("code", ""),
            "name": row.get("name", ""),
            "contents": row.get("contents", "")
        }
        es.index(index="standard_docs", document=doc)
```

| 항목                    | 설명                                        |
| ----------------------- | ------------------------------------------- |
| `Elasticsearch(...)`    | Elasticsearch 서버와 연결 (기본 포트: 9200) |
| `pd.read_csv(...)`      | CSV 파일을 DataFrame으로 읽어들임           |
| `es.index(...)`         | 문서 한 건씩 Elasticsearch에 색인           |
| `index="standard_docs"` | Elasticsearch 인덱스 이름 (자동 생성됨)     |
| `document=doc`          | 저장할 JSON 형식의 문서 데이터 (dict)       |

---

## 🔍 Elasticsearch 검색 흐름

`search_from_es.py`는 사용자가 검색어를 입력하면 Elasticsearch에 쿼리를 보내고 결과를 출력합니다.

```python
es = Elasticsearch("http://elasticsearch:9200")

def search(query, mode="fulltext"):
    if mode == "like":
        es_query = {
            "query": {
                "wildcard": {
                    "contents": f"*{query}*"
                }
            }
        }
    else:
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name", "contents"]
                }
            },
            "highlight": {
                "fields": {
                    "contents": {}
                }
            }
        }

    res = es.search(index="standard_docs", body=es_query)
    ...
```

---

## 🔍 검색 모드 비교

| 모드       | 설명                              | 쿼리 방식     | 특징                         |
| ---------- | --------------------------------- | ------------- | ---------------------------- |
| `fulltext` | 형태소 분석 기반 자연어 검색      | `multi_match` | 의미 기반 검색, 정렬 정확도  |
| `like`     | 단순 문자열 포함 여부 (부분 일치) | `wildcard`    | SQL의 `LIKE '%word%'`와 유사 |

- **`fulltext` 모드**는 기본적으로 Elasticsearch가 제공하는 형태소 분석을 활용해 `"지반계측"` → `"지반", "계측"`으로 분석해 검색
- **`like` 모드**는 형태소 분석 없이 해당 문자열이 포함된 문서만 찾음

## ✅ 1. Full-text 검색 쿼리 (`multi_match`)

| 키                         | 의미                                                     |
| -------------------------- | -------------------------------------------------------- |
| `"query"`                  | 검색 조건의 최상위 키                                    |
| `"multi_match"`            | 여러 필드를 대상으로 full-text 검색                      |
| `"query"` (내부)           | 사용자가 입력한 검색어                                   |
| `"fields"`                 | 검색 대상 필드 목록 (예: `"name"`, `"contents"`)         |
| `"highlight"`              | 검색어가 포함된 부분을 하이라이팅                        |
| `"fields"` (하이라이트 내) | 하이라이트 적용 대상 필드 (`"contents"`에서 강조 처리됨) |

## ✅ 2. Like 검색 쿼리 (`wildcard`)

| 키           | 의미                                                                  |
| ------------ | --------------------------------------------------------------------- |
| `"query"`    | 검색 조건                                                             |
| `"wildcard"` | `SQL LIKE` 검색처럼 부분 문자열 검색 수행                             |
| `"contents"` | 검색 대상 필드                                                        |
| `*{query}*`  | 와일드카드 패턴: 앞뒤 어느 위치든 포함되면 매칭 (`*` = 0개 이상 문자) |

---

## 🧪 색인 및 검색 확인

### ✅ 색인된 문서 개수 확인

```bash
curl -X GET "http://localhost:9200/standard_docs/_count?pretty"
```

### ✅ 전체 검색 테스트 (예: "지반계측")

```bash
curl -X GET "http://localhost:9200/standard_docs/_search?q=지반계측&pretty"
```

---
