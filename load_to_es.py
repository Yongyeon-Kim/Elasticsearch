from elasticsearch import Elasticsearch
import pandas as pd
from tqdm import tqdm

# Elasticsearch 서버에 연결
es = Elasticsearch("http://elasticsearch:9200")  # 도커 컨테이너 이름 사용

def index_csv(file_path, code_type):
    df = pd.read_csv("data/"+file_path)
    for _, row in tqdm(df.iterrows(), total=len(df)):
        doc = {
            "code_type": code_type,
            "code": row.get("code", ""),
            "name": row.get("name", ""),
            "contents": row.get("contents", "")
        }
        es.index(index="standard_docs", document=doc)

if __name__ == "__main__":
    index_csv("csv_KCS.csv", "KCS")
    index_csv("csv_KDS.csv", "KDS")
    print("색인 완료")
