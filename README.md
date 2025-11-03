# Simple .txt Search with Elasticsearch (Italian-friendly)

This project delivers the assignment with:
1) **Indexing**: a script that indexes `.txt` files from a folder into Elasticsearch with two fields: `name` and `content`.
2) **Searching**: a CLI that accepts simple queries (field prefixes and quoted phrases) and prints ranked results.
3) **Report**: section below describing analyzers, number of files, timing, and example queries.

---

## Features
- Two-field schema: `name` (filename) and `content` (file body).
- **Italian-friendly analysis** (stopwords + light stemming via Elasticsearch’s `italian` analyzer).
- Query syntax:
  - `name:term`, `content:term`
  - Phrases in quotes: `content:"rete neurale"`
  - No prefix → search in **both** fields.
  - Multiple clauses combined with **AND**.
- Fast local setup with Docker.

---

## Repository layout
