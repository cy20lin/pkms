import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# if len(sys.argv) < 2:
#     print("Usage: python app.py /path/to/file.md")
#     sys.exit(1)


# md_path = Path(sys.argv[1]).expanduser().resolve()
md_path = Path("C:/Users/cylin/Repo/pkms/spike/milkdown_spike/note.md")

if not md_path.exists():
    raise FileNotFoundError(md_path)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    return Path("templates/index.html").read_text(encoding="utf-8")


@app.get("/api/file")
def read_file():
    return {
        "content": md_path.read_text(encoding="utf-8")
    }


@app.put("/api/file")
def save_file(content: str = Body(..., embed=True)):
    md_path.write_text(content, encoding="utf-8")
    return {"status": "ok"}
