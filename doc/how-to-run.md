# How to run pkms

Make a config file

```jsonc
{
    "db_path": "pkms.db",
    "collection_path": "/path/to/<collection-name>"
}
```

Before running the commands, please activate the environment.

```powershell
./activate.ps1
```

Ingest the files from filesystem, refer to the config you made.

```bash
python spike/ingest.py ingest.jsonc
```

Run Webapp, specify the db to proceed

```bash
python -m pkms.web --db-path pkms.db
```
