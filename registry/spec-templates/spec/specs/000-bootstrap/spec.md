# SPEC-001: Example Feature

**Status:** ACEITO
**Version:** 1.0
**Authors:** Laurent (data engineer)
**Owner:** Laurent

---

## 1. Executive Summary
Example feature demonstrating the SDD workflow.

## 2. User Stories
### US-1
As a data engineer, I need to ingest data because...

## 3. Acceptance Criteria
- [ ] Data ingested successfully
- [ ] Schema validated

## 4. Sources
| Table | Schema |
|-------|--------|
| source | columns |

## 5. Destination
### DDL
```sql
CREATE TABLE target (id INT, name TEXT);
```

## 6. Refresh Strategy
Mode: delete-insert
