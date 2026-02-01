#!/usr/bin/env python3
import re
from pathlib import Path
infile = Path('documentum_seed.sql')
outfile = Path('documentum_seed_postgres.sql')
if not infile.exists():
    print('ERROR: input not found')
    raise SystemExit(1)
text = infile.read_text(encoding='utf-8')
text = text.replace('PRAGMA foreign_keys=OFF;\nBEGIN TRANSACTION;', 'BEGIN;')
text = text.replace('CURRENT_TIMESTAMP', 'now()')
text = re.sub(r"INSERT OR IGNORE INTO documentum_category \(([^)]+)\) VALUES \(([^)]+)\);",
              lambda m: f"INSERT INTO documentum_category ({m.group(1)}) VALUES ({m.group(2)}) ON CONFLICT (slug) DO NOTHING;",
              text, flags=re.S)
text = re.sub(r"INSERT OR IGNORE INTO documentum_document \(([^)]+)\) VALUES \((.+?)\);",
              lambda m: f"INSERT INTO documentum_document ({m.group(1)}) VALUES ({m.group(2)}) ON CONFLICT (slug) DO NOTHING;",
              text, flags=re.S)
text = re.sub(r"INSERT OR IGNORE INTO documentum_documentversion \(([^)]+)\) VALUES \((.+?)\);",
              lambda m: f"INSERT INTO documentum_documentversion ({m.group(1)}) VALUES ({m.group(2)});",
              text, flags=re.S)
outfile.write_text(text, encoding='utf-8')
print('Wrote', outfile)
