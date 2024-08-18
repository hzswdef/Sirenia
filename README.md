### Setup
```bash
mkdir .data
mkdir .data/docker-entrypoint-initdb.d

cp ext/base.sql .data/docker-entrypoint-initdb.d

make up
```