# Wording for Resolution and Screening Status

## Resolution Status of File

| Name             | DB Record | FS File | Trash Can |
| ---              | :---:     | :---:   | :---:     |
| NORMAL           | O         | O       | X         |
| TRASHED          | O         | X       | O         |
| DELETED          | O         | X       | X         |
| ERASED           | X         | X       | X         |
| ABSENT           | X         | X       | X         |
| MOVED            | O         | O/X     | X         |
| UAVAILABLE       | X         | O?      | X         |
| REJECTED         | X         | O       | X         |
| ~~PENDING~~      | X         | O       | X         |
| CHANGE_REQUESTED | X         | O       | X         |
| INBOXED          | X         | O       | X         |

- Normal: record exist in db, file exists in fs
- TRASHED: record exist in db, file exists in trash/
- INBOXED: record not exists in db, file exists in inbox/
- PENDING: record not exists in db, file exists in pending/
  - wait for human intervention, the name needs revise
    - as may confuse with pending ingestion
    - maybe blocked or review ?
    - CHANGE_REQUESTED , use the word from ITSM (IT Service Management)
      - not quite
    - ESCALATED: sounds good for one word? 
      - escalated for human processing and intervention
    - REQUIRES_REVIEW: 
    - REQUIRES_INTERVENTION: 
- IGNORED: the filename is ignored in the collection?
- BACKUP: USING
- HEAD: the current status 
- SNAPSHOT: this is from the history of snapshot not HEAD