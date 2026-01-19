# ADR-0018 Capability-Based Ingestion Implementation Checklist

## Phase 0 — Guardrails（先立界線）

> 這一階段不寫新功能，只是防止未來走歪。

- **明確定義 ingestion ≠ indexing**
- 禁止任何地方用「ingested = indexed」的語意
- 禁止在 code / schema 中出現單一 `status = INGESTED`
- 明確允許 partial record（NULL / missing fields）

> ✅ 完成標誌：  
> 系統中沒有任何地方假設「資料一定是完整的」。

## Phase 1 — Capability Vocabulary（建立語言）

> 先把「我們在說什麼」定義清楚

### 1.1 定義能力集合（code-level enum / constants）

- 定義 ingestion capabilities（非狀態）
  - `identity`
  - `stat`
  - `integrity`
  - `index`
  - `view`

```python
class IngestionCapability(str, Enum):
    IDENTITY = "identity"
    STAT = "stat"
    INTEGRITY = "integrity"
    INDEX = "index"
    VIEW = "view"
```

> ⚠️ 注意：  
> **不要**叫 `Stage` / `Phase` / `Step`

### 1.2 Capability presence is additive

- 設計資料結構能表達「已擁有哪些能力」
  - bitset / JSON array / separate table（先簡單）

例（暫時）：

```json
["identity", "stat"]
```

## Phase 2 — Stamper 拆分（責任切割）

> 把 ingestion 從 Screener / Indexer 拆乾淨

### 2.1 Stamper 類型劃分

- `IdentityStamper`
  - 從檔名 / metadata 推導 name-id、uid
- `StatStamper`
  - size / mtime / ctime
- `IntegrityStamper`
  - sha256 / blake3（重）
- （未來）`RevisionStamper`

> ❗ 原則：  
> **是否快，不是分類依據；責任才是**

### 2.2 Stamper 輸入 / 輸出規約

- Stamper 輸入：`FileLocation + existing record (optional)`
- Stamper 輸出：
  - 新增 / 更新能力
  - 不直接寫 FTS
  - 不決定 indexing

## Phase 3 — Addressing First（先救核心功能）

> 你自己已經抓得很準：addressing 是基石

### 3.1 Identity-only 可 resolve

- Resolver 僅依賴 `identity`
- 即使檔案不存在，也可 resolve historical record
- Resolver 回傳「best known fact」

```python
ResolvedTarget(
    file_id=...,
    file_uri=...,
    available_capabilities=[...],
)
```

### 3.2 Resolver 明確區分失敗類型

- Not found (identity unknown)
- Known but missing
- Known but conflicted (integrity mismatch)

## Phase 4 — Async Ingestion Skeleton（不做完，但先能跑）

> 這一階段**不追求完整**，只追求「可被觀察」

### 4.1 Task Model

- 定義 `IngestionTask`
  - target file
  - capability to produce
  - priority
  - state

```python
PENDING → RUNNING → DONE / FAILED
```

### 4.2 Task Queue（最小可行）

- 先用：
  - in-memory queue
  - or sqlite task table
- 不用 Celery / Redis（現在還不需要）

### 4.3 Task 可觀察性

- 能回答：
  - 現在在做什麼？
  - 哪個檔案？
  - 做到哪個 capability？
- CLI or debug output 即可

## Phase 5 — Inbox Semantics（使用者意圖）

> 這是 UX 的核心，不是工程細節

### 5.1 Inbox = explicit intent

- `_INBOX/` → 高 priority tasks
- 非 inbox → background / deferred

### 5.2 Ingestion does NOT scan the world by default

- 所有 ingestion 都必須有「來源理由」
  - inbox
  - filewatch
  - user trigger
  - config rule

## Phase 6 — Indexing as Optional Capability

> 把 FTS 降級成「其中一種能力」

### 6.1 Indexer 僅負責 INDEX capability

- Indexer 不負責 identity / integrity
- Indexer 失敗不影響 addressing

### 6.2 Partial Visibility Guarantees

| Capabilities | Address | Search | Edit |
| --- | --- | --- | --- |
| identity | ✅ | ❌ | ❌ |
| identity + index | ✅ | ✅ | ❌ |
| identity + index + view | ✅ | ✅ | ✅ |

## Phase 7 — Schema Hardening（延後，但預留）

> 你現在的直覺是對的：**先別動 schema**

- 允許 NULL / missing columns
- 為 revision 預留概念空間（不必實作）
- 不引入強 foreign key 鎖死設計

## Phase 8 — Tooling & Feedback Loop

> 系統一定要「說人話」

- CLI: `pkms ingest status`
- CLI: `pkms resolve <uri>`
- UI（未來）：展示 ingestion progress

## Final Invariants（不可破壞）

這些是 **紅線**：

1. ❌ 不可假設 ingestion 是一次完成
2. ❌ 不可因 indexing 失敗就讓檔案「消失」
3. ❌ 不可讓 addressing 依賴 indexing
4. ❌ 不可讓 ingestion state 不可觀察
5. ❌ 不可在 schema 尚未穩定前過度正規化

## 你目前的進度（我幫你標一下）

已完成 / 非常接近：

- ✅ Capability 思維
- ✅ Inbox 作為意圖
- ✅ addressing 優先
- ✅ odt / md → html pipeline
- ✅ schema 延後固化

接下來 **最有價值的下一步**：

> 👉 **Phase 2 + Phase 3（Stamper 拆分 + Resolver 能力感知）**

如果你願意，下一輪我可以：

- 幫你畫一張 **capability lattice diagram**
- 或直接幫你把現有 code map 到 checklist（逐檔案）

你現在這個系統，已經不是「玩具 PKMS」了，而是**真的能陪你用很多年的系統設計**。
