import re
import time
from elasticsearch import Elasticsearch

ES_INDEX = "txtdocs"

def get_client():
    return Elasticsearch("http://localhost:9200")

TOKENIZER = re.compile(
    r'(?P<field>name|content)?:?"(?P<phrase>[^"]+)"|(?P<field2>name|content)?:?(?P<term>[^\s"]+)'
)

def parse_query(q: str):
    clauses = []
    for m in TOKENIZER.finditer(q):
        field = m.group("field") or m.group("field2") or "both"
        if m.group("phrase") is not None:
            clauses.append({"type": "phrase", "field": field, "text": m.group("phrase")})
        elif m.group("term"):
            clauses.append({"type": "term", "field": field, "text": m.group("term")})
    return clauses

def clause_to_es(cl):
    field = cl["field"]
    fields = ["name", "content"] if field == "both" else [field]
    if cl["type"] == "phrase":
        return {
            "bool": {
                "should": [{"match_phrase": {f: {"query": cl["text"]}}} for f in fields],
                "minimum_should_match": 1,
            }
        }
    else:
        return {
            "multi_match": {
                "query": cl["text"],
                "fields": fields,
                "type": "best_fields",
                "operator": "and" if field == "both" else "or",
            }
        }

def build_query(user_q: str):
    clauses = parse_query(user_q)
    if not clauses:
        return {"match_none": {}}
    return {"bool": {"must": [clause_to_es(c) for c in clauses]}}

def print_hits(hits):
    for i, h in enumerate(hits, 1):
        s = h["_source"]
        print(f"{i:2d}. {s['name']}  —  {s['path']}  (score={h['_score']:.3f})")

def repl():
    es = get_client()
    print("Index ready. Type a query (ENTER to exit).")
    print('Examples: name:guida  content:"rete neurale"  tfidf inversa')
    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q:
            break
        body = {
            "query": build_query(q),
            "size": 20,
        }
        t0 = time.time()
        res = es.search(index=ES_INDEX, body=body)
        ms = (time.time() - t0) * 1000
        hits = res["hits"]["hits"]
        print(f"{len(hits)} results ({ms:.1f} ms):")
        print_hits(hits)
    print("Bye.")

if __name__ == "__main__":
    repl()
