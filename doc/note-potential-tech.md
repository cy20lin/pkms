# Note for potential tech

- html to text
  - inscrptis: good for plain text
  - to markdown: noisy for complex html, not ideal

- odt to html pre-render
  - Write my own converter: take like 12 days
  - Why not use Other solution:
    - license issue and cannot render drawing shapes o
  - solutions
    - odt2html: 
    - pandoc:

- markdown to html pre-render
  - python/markitdown
  - python/markdown2
  - python/markdown

- frontend markdown view:
  - milkdown: 
    - 支援 CRDT Y.js
  - lexical: 
    - CRDT Y.js
  - code mirror 6: 
    - obsidian, logseq 使用的工具
  - vditor: all in one, feature rich editor
    - 視覺模式
      - 所見及所得 WYSIWYG : like milkdown
      - 及時預覽IR: like obsidian
      - 分屏預覽: like stackedit

- Database
  - Sqlite3
  - Datasette: for database viewing, and automatic APIs generation, use sqlite
  - sqlite3-vec: 
    - A vector search SQLite extension that runs anywhere!
    - https://github.com/asg017/sqlite-vec
    - also support datasette
  - sqliteai/sqlite-vector
    - 提供一系列的生態應用軟體程式碼
    - 星星數較少
    - https://github.com/sqliteai/sqlite-vector
    - Elastic License 2.0 (modified for open-source use)
    - 商用需要商用license

- frontend file tree view:
  - headless tree
    - https://github.com/lukasbach/headless-tree
    - https://github.com/lukasbach/react-complex-tree
  - inspire-tree:
    - https://github.com/helion3/inspire-tree
    - 看起來更輕量?
    - 效果看起來不錯

- filesystem monitor
  - python: watchfiles, backend

- frontend terminal:
  - xterm.js

- backend api serving lib
  - fastapi: use this
  - flask: skip

- for profiling
  - pyinstrument

- for source code investigation
  - https://deepwiki.com/

- for container base image
  - Alpine Linux: a lightweight base image os choice
