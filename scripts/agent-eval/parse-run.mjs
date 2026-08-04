#!/usr/bin/env node
// scripts/agent-eval/parse-run.mjs
// Parse os JSONs de run e imprime comparison agregado
// Adaptado de: colbymchenry/codegraph/scripts/agent-eval/parse-run.mjs
//
// Usage: node scripts/agent-eval/parse-run.mjs <out-dir> <timestamp> <runs-per-arm>
//
// Output: tabela comparativa com medianas por arm
//
// Parseia cada run JSON (formato: {run_id, arm, duration, result}) e
// agrega por arm. Result esperado tem a forma:
//   { tool_calls: [{type, count}], read_count, grep_count, tokens_total }

import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';

const [outDir, timestamp, runs] = process.argv.slice(2);
const RUNS = parseInt(runs, 10);

const files = readdirSync(outDir).filter(f =>
  f.startsWith(`run_${timestamp}_`) && f.endsWith('.json')
);

const arms = { A: [], B: [] };

for (const file of files) {
  try {
    const raw = JSON.parse(readFileSync(join(outDir, file), 'utf8'));
    const parsed = parseRun(raw);
    if (parsed.arm === 'A' || parsed.arm === 'B') {
      arms[parsed.arm].push(parsed);
    }
  } catch (e) {
    console.warn(`  ⚠ Could not parse ${file}: ${e.message}`);
  }
}

function median(arr) {
  if (arr.length === 0) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0
    ? sorted[mid]
    : (sorted[mid - 1] + sorted[mid]) / 2;
}

function sum(arr, key) {
  return arr.reduce((acc, r) => acc + (r[key] || 0), 0);
}

// ── Aggregate per arm ────────────────────────────────────────────────────────
const agg = {};
for (const arm of ['A', 'B']) {
  const runs = arms[arm];
  if (runs.length === 0) {
    agg[arm] = { n: 0 };
    continue;
  }

  agg[arm] = {
    n: runs.length,
    duration_med: median(runs.map(r => r.duration)),
    tool_calls_sum: sum(runs, 'tool_calls_total'),
    tool_calls_med: median(runs.map(r => r.tool_calls_total)),
    read_sum: sum(runs, 'read_count'),
    read_med: median(runs.map(r => r.read_count)),
    grep_sum: sum(runs, 'grep_count'),
    grep_med: median(runs.map(r => r.grep_count)),
    tokens_sum: sum(runs, 'tokens_total'),
    tokens_med: median(runs.map(r => r.tokens_total)),
    mcp_by_type: aggregateMcp(runs),
  };
}

// ── Print comparison table ────────────────────────────────────────────────────
console.log('');
console.log('  arm     n   duration(s)   tool_calls   Read   Grep   tokens');
console.log('  ───   ──   ───────────   ──────────   ────   ────   ──────');
for (const arm of ['A', 'B']) {
  const r = agg[arm];
  if (r.n === 0) { console.log(`  ${arm}     —     —             —         —     —     —`); continue; }
  console.log(
    `  ${arm}    ${r.n}   ` +
    `${r.duration_med.toFixed(1).padStart(10)}   ` +
    `${String(r.tool_calls_med).padStart(9)}   ` +
    `${String(r.read_med).padStart(4)}   ` +
    `${String(r.grep_med).padStart(4)}   ` +
    `${String(r.tokens_med).padStart(6)}`
  );
}

console.log('');

// ── Delta B vs A ──────────────────────────────────────────────────────────────
const a = agg['A'];
const b = agg['B'];
if (a.n > 0 && b.n > 0) {
  const tool_delta = b.tool_calls_med - a.tool_calls_med;
  const read_delta = b.read_med - a.read_med;
  const grep_delta = b.grep_med - a.read_med;
  const dur_delta = b.duration_med - a.duration_med;

  console.log('  Delta B vs A (median):');
  console.log(`    tool calls: ${sign(tool_delta)}${Math.abs(tool_delta)}`);
  console.log(`    Read:       ${sign(read_delta)}${Math.abs(read_delta)}`);
  console.log(`    Grep:       ${sign(grep_delta)}${Math.abs(grep_delta)}`);
  console.log(`    duration:   ${sign(dur_delta)}${Math.abs(dur_delta).toFixed(1)}s`);

  console.log('');
  console.log('  Verdict:');
  const wins = [];
  if (tool_delta < 0) wins.push('✅ fewer tool calls');
  if (tool_delta > 0) wins.push('⚠️  MORE tool calls (regression)');
  if (read_delta <= 0) wins.push('✅ Read <= baseline');
  if (read_delta > 0) wins.push('⚠️  MORE reads (regression)');
  if (dur_delta < 0) wins.push('✅ faster');
  if (dur_delta > 0) wins.push('⚠️  slower');
  for (const w of wins) console.log(`    ${w}`);
}

// ── MCP tools breakdown ───────────────────────────────────────────────────────
if (a.n > 0 && b.n > 0) {
  const allTypes = new Set([...Object.keys(a.mcp_by_type || {}), ...Object.keys(b.mcp_by_type || {})]);
  if (allTypes.size > 0) {
    console.log('');
    console.log('  MCP tools used (total across all runs):');
    for (const type of [...allTypes].sort()) {
      const a_val = (a.mcp_by_type || {})[type] || 0;
      const b_val = (b.mcp_by_type || {})[type] || 0;
      if (a_val === 0 && b_val === 0) continue;
      console.log(`    ${type}: A=${a_val}  B=${b_val}  ${b_val > a_val ? '↑' : b_val < a_val ? '↓' : '='}`);
    }
  }
}

console.log('');

// ── Helpers ───────────────────────────────────────────────────────────────────
function sign(n) {
  return n > 0 ? '+' : '';
}

function parseRun(raw) {
  // Expected shape: { run_id, arm, duration, result: { tool_calls, read_count, ... } }
  const run_id = raw.run_id || '';
  const arm = run_id.includes('_A_') ? 'A' : run_id.includes('_B_') ? 'B' : null;
  const result = raw.result || {};

  // Tool calls total — sum all types
  const tool_calls_total = Array.isArray(result.tool_calls)
    ? result.tool_calls.reduce((acc, t) => acc + (t.count || 0), 0)
    : (result.tool_calls_total || 0);

  // MCP calls by type
  const mcp_by_type = {};
  if (Array.isArray(result.tool_calls)) {
    for (const t of result.tool_calls) {
      if (t.type && t.type.startsWith('mcp__')) {
        // normalize: mcp__namespace__tool
        mcp_by_type[t.type] = (mcp_by_type[t.type] || 0) + (t.count || 0);
      }
    }
  }

  return {
    run_id,
    arm,
    duration: raw.duration || 0,
    tool_calls_total,
    read_count: result.read_count || 0,
    grep_count: result.grep_count || 0,
    tokens_total: result.tokens_total || 0,
    mcp_by_type,
  };
}

function aggregateMcp(runs) {
  const totals = {};
  for (const r of runs) {
    for (const [type, count] of Object.entries(r.mcp_by_type || {})) {
      totals[type] = (totals[type] || 0) + count;
    }
  }
  return totals;
}