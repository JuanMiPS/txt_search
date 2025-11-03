import os
import time
import json
from elasticsearch import Elasticsearch, helpers

ES_INDEX = "txtdocs"

def get_client():
    return Elasticsearch("http://localhost:9200")

MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "name_analyzer": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": ["lowercase", "asciifolding"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "path":    {"type": "keyword"},
            "name":    {"type": "text", "analyzer": "name_analyzer"},
            "content": {"type": "text", "analyzer": "italian"}
        }
    }
}

def recreate_index(es: Elasticsearch):
    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
    es.indices.create(index=ES_INDEX, body=MAPPING)

def gen_docs(input_dir: str):
    for entry in os.scandir(input_dir):
        if entry.is_file() and entry.name.lower().endswith(".txt"):
            try:
                with open(entry.path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                print(f"[WARN] Could not read {entry.path}: {e}")
                continue
            yield {
                "_index": ES_INDEX,
                "_id": os.path.abspath(entry.path),
                "_source": {
                    "path": os.path.abspath(entry.path),
                    "name": entry.name,
                    "content": content
                }
            }

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Index .txt files into Elasticsearch (Italian analyzer)")
    ap.add_argument("input_dir", help="Folder containing .txt files")
    args = ap.parse_args()

    es = get_client()
    recreate_index(es)

    t0 = time.time()
    helpers.bulk(es, gen_docs(args.input_dir))
    es.indices.refresh(index=ES_INDEX)
    secs = time.time() - t0

    count = es.count(index=ES_INDEX)["count"]
    print(f"Indexing complete: {count} files in {secs:.3f}s")
    print(json.dumps({"num_docs": count, "build_seconds": round(secs, 3)}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
