## Identity Layers

PKMS 定義三層 identity，**各司其職，不可混用**。

### 1. `id` — Database Row Identity

- SQLite `INTEGER PRIMARY KEY`
- 僅存在於單一 DB instance
- 不具任何跨系統語意
    
**Contract**

- 不可對外暴露
- 不可作為引用
- 不可假設穩定性
    

### 2. `file_id` — Human-facing Resource Identity

- 人類可讀、可書寫
- 格式慣例，如：`yyyy-mm-dd-nnnn[suffix]`
- 大小寫不敏感（Windows 相容） 

**Contract**

- 為 PKMS 的主要引用錨點
- 用於 URI、Markdown、Obsidian
- 不承載 metadata
- 一旦建立，不應因 rename 而改變

> `file_id` 回答的是「這是什麼資源」，不是「它目前長什麼樣」。

### 3. `file_uid` — Strong Unique File Identity

- 系統生成
- 不要求人類可讀
- 來源可為：
  - UUID / ULID / CUID（可編輯檔案）
  - Hash（snapshot / readonly）

**Contract**

- 用於去重、驗證、跨裝置比對
- 不作為語意版本判斷
- 不保證內容等價

## Snapshot 定義（v1）

在 v1 中：

> **每一個 snapshot 被視為一個獨立 file resource**

-   同一 URL 不同時間 → 不同 `file_id`
-   Snapshot 之間不假設版本關係

## 非 Identity 欄位（輔助訊號）

-   `file_hash_sha256`
-   `modified_datetime`
-   `origin_url`
-   `snapshot_datetime`
    

這些欄位**不具身份語意**，僅用於輔助分析。


## Evolution Guarantee

- `file_id` 與 `file_uid` 在未來版本中只會被擴充，不會被否定
- v1 不處理 version graph / diff / merge

## future questions

