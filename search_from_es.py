from elasticsearch import Elasticsearch

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
    else:  # full-text
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
    hits = res["hits"]["hits"]
    print(f"\n총 {len(hits)}개 결과:")
    for hit in hits:
        source = hit["_source"]
        print(f"\n[{source.get('code_type')}] {source.get('code')} - {source.get('name')}")
        if "highlight" in hit and "contents" in hit["highlight"]:
            print("→ 하이라이트:", hit["highlight"]["contents"][0])
        else:
            print("→ 요약:", source.get("contents", "")[:100])

if __name__ == "__main__":
    query = input("검색어를 입력하세요: ")
    mode = input("검색 모드 선택 (fulltext 또는 like): ").strip().lower()
    search(query, mode)
