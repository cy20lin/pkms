# Future Notes（Snapshot / Version / Replica）

> **只寫概念，不寫實作** 

## Why v2 Exists

> **PKMS v1 is about knowing what a file is.**\
> **PKMS v2+ will be about knowing how it changes. how to access it acroess devices.**

v1 解決的是：

- indexing
- search
- identity stability
    
v2+ 開始才處理：

- 多版本
- 多裝置
- 副本關係

    

## Planned Concepts (Not Implemented)

### 1\. Version / Revision Identity

```text
revision_uid
```

-   表示某一資源在某一時間點的內容狀態
-   可形成 DAG（類 Git）
    

### 2\. Replica Identity

```text
replica_id
```

-   某一檔案在某一裝置上的實體存在
-   關聯：
    -   device\_id
    -   local path
    -   last\_seen

### 3\. Device Identity

```text
device_id
```

-   每一裝置的穩定識別
-   不與使用者帳號綁定
    

## Key Design Principle for v2+

> Identity 與 Version 是不同問題  
> Version 永遠建立在 Identity 之上
