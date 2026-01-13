# Milkdown + FastAPI Markdown Editor Spike

This is an **exploratory spike project** intended to validate the following idea:

> Using **Milkdown (a structured Markdown editor based on ProseMirror)**  
> together with **FastAPI (a local backend)**  
> can serve as a solid foundation for a **local-first PKMS (Personal Knowledge Management System)** editor.

This project is deliberately kept **minimal, single-purpose, and single-file-oriented** to avoid premature system design.

---

## 🎯 Project Goals

- Edit a **local Markdown file** through a web interface
- Use **Milkdown** as the frontend editor
- Use **FastAPI** as the backend server
- **No dependency on external CDN or cloud services**
- The web app edits **exactly one Markdown file**, whose path is provided via CLI

---

## ❌ Explicitly Out of Scope (for this Spike)

- Multiple files / vault management
- File tree or file explorer
- Authentication / user system
- Autosave / diff / patch
- Sync / versioning
- PKMS features (wikilinks, block refs, etc.)

> These are intentionally deferred until the editor experience itself is validated.

---

## 🧱 Project Structure

```text
milkdown_spike/
├── app.py                    # FastAPI backend
├── requirements.txt
├── static/
│   ├── milkdown/
│   │   └── bundle.js         # Frontend bundle built by esbuild
│   └── style.css
├── templates/
│   └── index.html
└── frontend/
    ├── editor.ts             # Milkdown frontend source
    └── package.json
```

---

## 🧠 Architecture Overview (Important)

### Core Concept

- **Markdown is not the primary editing format**

- Milkdown edits a **Document Tree (ProseMirror state)**

- Markdown only exists at the boundaries:

  - Load (parse)

  - Save (serialize)

```text
Markdown string
      ↓ parse
Document Tree (Editor State)
      ↓ editing
Document Tree
      ↓ serialize
Markdown string
```

This model is critical for advanced PKMS features later on.

---

## 🚀 Usage

### 1️⃣ Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Start the Backend (specify the Markdown file)

```bash
python app.py /path/to/your/note.md
```

Or with reload support:

```bash
uvicorn app:app --reload
```

Then open your browser at:

```cpp
http://127.0.0.1:8000
```

---

## 🖥 Frontend Build (Milkdown)

The frontend uses **esbuild** to bundle Milkdown into a single browser-executable JavaScript file.

### 1️⃣ Install Frontend Dependencies

```bash
cd frontend
npm install
```

Key dependencies include:

- `@milkdown/core`

- `@milkdown/preset-commonmark`

- `@milkdown/theme-nord`

- `esbuild`

### 2️⃣ Build the Frontend Bundle

```bash
npx esbuild editor.ts --bundle --format=iife --target=es2017 --outfile=../static/milkdown/bundle.js
```

### 3️⃣ The bundle is served by FastAPI

```html
<script src="/static/milkdown/bundle.js"></script>
```

---

## 🔌 Backend API (Minimal)

### `GET /api/file`

Returns the entire Markdown file content.

```json
{
  "content": "# My Note\n\nHello world"
}
```

### `PUT /api/file`

Overwrites the entire Markdown file.

```json
{
  "content": "# Updated\n\nNew content"
}
```

---

## 🧪 What This Spike Is Meant to Validate

Focus on answering these questions:

1. Is Milkdown comfortable for long-term Markdown writing?

2. Is the Markdown round-trip (load → save) acceptable?

3. Does a structured editing model fit future PKMS needs?

4. Is a local web-based editor responsive enough?

---

## 🔮 Possible Future Extensions (Not Part of This Spike)

- Wikilinks (`[[note]]`) via custom schema

- Block references / block IDs

- Metadata / frontmatter

- Search and indexing

- Multi-file PKMS UI

- Desktop packaging via Tauri or Electron

---

## 📌 Project Positioning

> This is not a finished application.  
> It is a **decision-making experiment**.

If this spike proves successful,  
it will become the foundation of the **editor core** for a future PKMS system.
