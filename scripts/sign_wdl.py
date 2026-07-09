"""WDL signature tool — compute SHA-256 canonical JSON for plan.json and verdict.yaml."""
import json, hashlib, yaml, sys, os

plan_path = sys.argv[1]  # artifacts/wdl/<plan-id>/plan.json
verdict_path = sys.argv[2]  # artifacts/wdl/<plan-id>/verdict.yaml

# --- Sign plan.json ---
with open(plan_path, 'r', encoding='utf-8') as f:
    plan = json.load(f)

plan.pop('signature', None)
canonical = json.dumps(plan, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
plan_sha = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
print(f'plan_sha={plan_sha}')

with open(plan_path, 'w', encoding='utf-8') as f:
    plan['signature'] = {'algorithm': 'sha256-canonical-json', 'value': plan_sha}
    json.dump(plan, f, indent=2, ensure_ascii=False)

# --- Sign verdict.yaml ---
with open(verdict_path, 'r', encoding='utf-8') as f:
    verdict_raw = f.read()

verdict = yaml.safe_load(verdict_raw)
verdict.pop('signature', None)
canonical_v = json.dumps(verdict, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
verdict_sha = hashlib.sha256(canonical_v.encode('utf-8')).hexdigest()
print(f'verdict_sha={verdict_sha}')

# Rebuild YAML preserving original content then appending signature
with open(verdict_path, 'w', encoding='utf-8') as f:
    f.write(verdict_raw.rstrip() + '\n')
    f.write('\n')
    f.write('signature:\n')
    f.write('  algorithm: sha256-canonical-json\n')
    f.write(f'  value: "{verdict_sha}"\n')
