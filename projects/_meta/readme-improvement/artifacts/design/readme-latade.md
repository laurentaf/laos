<!--
  LATADE — Data engineering capability for LAOS (DuckDB medallion pipeline)
  README.md  |  github.com/laurentaf/latade
  Brand: Data is the spine of every decision.
  Tone: Technical, polished, capability reference.
  Adapted from the LAOS README (20/20) inline-HTML pattern.
-->

<div align="center" style="margin-top:48px;margin-bottom:24px;">

<!-- Emblem: medallion layers (bronze → silver → gold) -->
<svg width="72" height="72" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#6c5ce7" stroke-width="1.5" fill="none" opacity="0.3"/>
  <!-- Three stacked layers -->
  <rect x="12" y="10" width="40" height="12" rx="3" fill="#CD7F32" fill-opacity="0.15" stroke="#CD7F32" stroke-width="1.5"/>
  <text x="32" y="19" text-anchor="middle" font-size="7" fill="#CD7F32" font-weight="600" font-family="monospace">BRONZE</text>
  <rect x="12" y="26" width="40" height="12" rx="3" fill="#C0C0C0" fill-opacity="0.15" stroke="#C0C0C0" stroke-width="1.5"/>
  <text x="32" y="35" text-anchor="middle" font-size="7" fill="#C0C0C0" font-weight="600" font-family="monospace">SILVER</text>
  <rect x="12" y="42" width="40" height="12" rx="3" fill="#FFD700" fill-opacity="0.15" stroke="#FFD700" stroke-width="1.5"/>
  <text x="32" y="51" text-anchor="middle" font-size="7" fill="#FFD700" font-weight="600" font-family="monospace">GOLD</text>
  <!-- Down arrows -->
  <line x1="32" y1="22" x2="32" y2="26" stroke="#6c5ce7" stroke-width="1" opacity="0.4"/>
  <line x1="32" y1="38" x2="32" y2="42" stroke="#6c5ce7" stroke-width="1" opacity="0.4"/>
</svg>

<br/>

# LATADE

### Data Engineering &bull; DuckDB Medallion Pipeline &bull; MCP-Native

<p style="margin:12px 0;">
  <img src="https://img.shields.io/badge/Python-%E2%89%A53.11-3776AB?style=flat&logo=python&logoColor=fff" alt="Python 3.11+"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Status-STABLE-00b894?style=flat" alt="Status: STABLE"/>
  &nbsp;
  <img src="https://img.shields.io/badge/License-MIT-31c754?style=flat" alt="License: MIT"/>
  &nbsp;
  <img src="https://img.shields.io/badge/DuckDB-Enabled-6c5ce7?style=flat&logo=duckdb&logoColor=fff" alt="DuckDB Enabled"/>
  &nbsp;
  <img src="https://img.shields.io/badge/MCP-7%20tools-a29bfe?style=flat" alt="7 MCP tools"/>
  &nbsp;
  <a href="https://github.com/laurentaf/laos"><img src="https://img.shields.io/badge/Ecosystem-LAOS-6c5ce7?style=flat" alt="LAOS Ecosystem"/></a>
</p>

<hr style="width:48px;margin:24px auto;border:none;border-top:2px solid #6c5ce7;opacity:0.3;"/>

</div>

> **Data is the spine of every decision.**  
> LATADE is the LAOS ecosystem's data engineering capability — a DuckDB-backed medallion pipeline (bronze → silver → gold) exposed through 7 MCP-native tools. From CSV ingestion to gold-layer aggregation, every operation is deterministic, versioned, and gated.

---

## What LATADE Is

LATADE is the data engineering capability for LAOS, providing a complete medallion pipeline (bronze → silver → gold) backed by **DuckDB** and exposed through deterministic **MCP tools**. It replaces ad-hoc ETL scripts with a spec-first, gated data pipeline that any orchestrated agent can call.

**Why LATADE exists:** LAOS agents need a shared, trusted data layer — not a collection of one-off SQL scripts. LATADE standardizes the pipeline: load CSV to bronze, deduplicate to silver, aggregate to gold. Every step is a tool, every operation is auditable, and every table is inspectable.

**Key architecture:** DuckDB-powered (embeddable, zero-config OLAP). No separate database server needed. The medallion model ensures data quality gates at each layer.

---

## Architecture

```mermaid
flowchart LR
    CSV[CSV / Data Sources] --> BRONZE[bronze_*]
    BRONZE --> SILVER[silver_*]
    SILVER --> GOLD[gold_*]

    subgraph BRONZE[Bronze — Raw Ingestion]
        BRONZE
    end
    subgraph SILVER[Silver — Cleaned / Deduped]
        SILVER
    end
    subgraph GOLD[Gold — Aggregated]
        GOLD
    end
```

<div align="center" style="margin:24px 0;">

<table style="border-collapse:separate;border-spacing:0;min-width:560px;">
  <tr>
    <td colspan="3" align="center" style="padding:0 0 8px 0;">
      <div style="display:inline-block;border:1.5px solid #6c5ce7;border-radius:8px;padding:12px 24px;text-align:center;">
        <div style="font-weight:700;font-size:1em;letter-spacing:0.04em;color:#6c5ce7;">LATADE MCP Server</div>
        <div style="font-size:0.8em;opacity:0.5;">Python · DuckDB · Medallion Pipeline</div>
      </div>
    </td>
  </tr>
  <tr><td colspan="3" align="center" style="padding:0;"><div style="width:1.5px;height:14px;background:#6c5ce7;opacity:0.2;margin:0 auto;"></div></td></tr>
  <tr>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1.5px solid #CD7F32;border-radius:6px;padding:10px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;color:#CD7F32;">Bronze</div>
        <div style="font-size:0.7em;opacity:0.5;">Raw CSV ingestion<br/><code>load_csv_to_bronze</code></div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1.5px solid #C0C0C0;border-radius:6px;padding:10px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;color:#C0C0C0;">Silver</div>
        <div style="font-size:0.7em;opacity:0.5;">Dedup + clean<br/><code>run_silver_dedup</code></div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1.5px solid #FFD700;border-radius:6px;padding:10px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;color:#B8860B;">Gold</div>
        <div style="font-size:0.7em;opacity:0.5;">Grouped aggregation<br/><code>run_gold_aggregation</code></div>
      </div>
    </td>
  </tr>
</table>

</div>

---

## MCP Tools

<table style="width:100%;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid #6c5ce7;opacity:0.4;">
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;width:25%;">Tool</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Description</th>
  </tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>load_csv_to_bronze</code></td><td style="padding:8px 14px;opacity:0.7;">Ingest CSV → bronze layer with auto schema detection + <code>_ingested_at</code></td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>run_silver_dedup</code></td><td style="padding:8px 14px;opacity:0.7;">Deduplicate bronze table by key columns → silver layer</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>run_gold_aggregation</code></td><td style="padding:8px 14px;opacity:0.7;">Aggregate silver table by group columns → gold layer (SUM, COUNT, AVG, MIN, MAX)</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>execute_sql</code></td><td style="padding:8px 14px;opacity:0.7;">Safe read-only SELECT queries against DuckDB with safety validation</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>validate_data_safety</code></td><td style="padding:8px 14px;opacity:0.7;">Check if a SQL query is safe (read-only) before execution</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>generate_schema_preview</code></td><td style="padding:8px 14px;opacity:0.7;">Infer schema from CSV/JSON — columns, types, sample values</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>inspect_table</code></td><td style="padding:8px 14px;opacity:0.7;">Describe table: columns, types, row count</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>health</code></td><td style="padding:8px 14px;opacity:0.7;">Server liveness probe</td></tr>
  <tr><td style="padding:8px 14px;font-weight:500;"><code>list_supported_operations</code></td><td style="padding:8px 14px;opacity:0.7;">Full capability catalog</td></tr>
</table>

---

## Quick Start

```bash
# Install dependencies
uv sync

# Configure your DuckDB database
# LATADE_DB_PATH defaults to :memory: — set for persistence:
# export LATADE_DB_PATH=/path/to/latade.duckdb

# Start the MCP server
uv run latade-server

# Health check
uv run latade health
```

### Requirements

<table style="font-size:0.85em;border-collapse:separate;border-spacing:0;">
  <tr><td style="padding:6px 12px;font-weight:500;">Python</td><td style="padding:6px 12px;opacity:0.6;">≥ 3.11</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Storage</td><td style="padding:6px 12px;opacity:0.6;">DuckDB (:memory: or persistent .duckdb file)</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Dependencies</td><td style="padding:6px 12px;opacity:0.6;">duckdb, pandas, pyyaml</td></tr>
</table>

---

## Example: Full Medallion Pipeline

```python
# 1. Load CSV to Bronze
result = latade.load_csv_to_bronze(
    source_path="/data/orders.csv",
    table_name="bronze_orders"
)
# → "Loaded 10,000 rows into bronze_orders"

# 2. Deduplicate to Silver
result = latade.run_silver_dedup(
    source_table="bronze_orders",
    target_table="silver_orders",
    dedup_columns=["order_id"]
)
# → "9,850 rows (150 duplicates removed)"

# 3. Aggregate to Gold
result = latade.run_gold_aggregation(
    source_table="silver_orders",
    target_table="gold_orders_by_category",
    group_by_columns=["category"],
    measures={"total": "SUM", "count": "COUNT", "avg_value": "AVG"}
)
# → "25 rows in gold_orders_by_category"

# 4. Inspect & Query
latade.inspect_table("gold_orders_by_category")
# → {"columns": [...], "row_count": 25}

latade.execute_sql("SELECT * FROM gold_orders_by_category ORDER BY total DESC")
# → [{"category": "Electronics", "total": 450000, ...}, ...]
```

---

## Medallion Pipeline Details

| Layer | Stage | What Happens | Output Table |
|-------|-------|-------------|--------------|
| 🟤 **Bronze** | Raw Ingestion | CSV → DuckDB with auto schema, `_ingested_at` metadata | `bronze_{source}` |
| ⚪ **Silver** | Dedup & Clean | Remove duplicates by key columns, keep first occurrence | `silver_{entity}` |
| 🟡 **Gold** | Aggregation | Grouped aggregations (SUM, COUNT, AVG, MIN, MAX) | `gold_{domain}` |

All layers are inspectable via `inspect_table` and queryable via `execute_sql`.

---

## Safety & Governance

- **Read-only enforcement:** `execute_sql` only permits SELECT/WITH/EXPLAIN queries. Mutations (DROP, DELETE, INSERT, UPDATE, ALTER) are rejected.
- **Pre-flight validation:** `validate_data_safety` checks queries without executing them.
- **Dedup audit trail:** Silver layer preserves the first occurrence per key, ensuring reproducibility.
- **Immutable bronze:** Raw data is never modified — only read during silver transformation.

---

## Contributing

LATADE is a LAOS capability. Changes follow the governance model:

| Scope | Path |
|-------|------|
| **New pipeline stage** | LACOUNCIL proposal → Conselho majority → implement |
| **Bug fix** | Open an [issue](https://github.com/laurentaf/latade/issues) or submit a PR |
| **Documentation** | PR with description — no gate required |

See the [LAOS governance model](https://github.com/laurentaf/laos) for full details.

---

## License

<div style="margin:16px 0;">

**MIT** — see [`LICENSE`](https://github.com/laurentaf/latade/blob/main/LICENSE) for the full text.

Data is the spine of every decision. The pipeline is yours.

</div>

---

<div align="center" style="margin:36px 0;opacity:0.25;font-size:0.8em;">
<svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#6c5ce7" stroke-width="1.5" fill="none" opacity="0.15"/>
  <rect x="14" y="12" width="36" height="10" rx="2" stroke="#CD7F32" stroke-width="1.5" fill="none" opacity="0.4"/>
  <rect x="14" y="27" width="36" height="10" rx="2" stroke="#C0C0C0" stroke-width="1.5" fill="none" opacity="0.4"/>
  <rect x="14" y="42" width="36" height="10" rx="2" stroke="#FFD700" stroke-width="1.5" fill="none" opacity="0.4"/>
</svg>
<br/>
LATADE — part of the <a href="https://github.com/laurentaf/laos" style="text-decoration:none;">LAOS</a> ecosystem
</div>
