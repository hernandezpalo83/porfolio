#!/usr/bin/env python3
"""Convert documentum_seed.sql (SQLite) to a PostgreSQL-compatible SQL file.
Usage: python convert_to_postgres.py [--in documentum_seed.sql] [--out documentum_seed_postgres.sql]
"""
from pathlib import Path
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--in', dest='infile', default='documentum_seed.sql')
parser.add_argument('--out', dest='outfile', default='documentum_seed_postgres.sql')
args = parser.parse_args()

infile = Path(args.infile)
outfile = Path(args.outfile)
if not infile.exists():
    print('ERROR: source file not found:', infile)
    raise SystemExit(1)

s = infile.read_text(encoding='utf-8')
# Remove PRAGMA and convert BEGIN TRANSACTION to BEGIN;
s = s.replace('PRAGMA foreign_keys=OFF;\nBEGIN TRANSACTION;', 'BEGIN;')
# Replace CURRENT_TIMESTAMP -> now()
s = s.replace('CURRENT_TIMESTAMP', 'now()')
# Convert category inserts to ON CONFLICT
s = re.sub(r"INSERT OR IGNORE INTO documentum_category \(([^)]+)\) VALUES \(([^)]+)\);",
           lambda m: f"INSERT INTO documentum_category ({m.group(1)}) VALUES ({m.group(2)}) ON CONFLICT (slug) DO NOTHING;",
           s, flags=re.S)
# Ensure booleans are correct: 1 -> true where appropriate (category is_visible)
s = s.replace(', 0, 1, now(), now()', ', 0, true, now(), now()')
# Documents: replace INSERT OR IGNORE ... with ON CONFLICT (slug) DO NOTHING
s = re.sub(r"INSERT OR IGNORE INTO documentum_document \(([^)]+)\) VALUES \((.+?)\);",
           lambda m: f"INSERT INTO documentum_document ({m.group(1)}) VALUES ({m.group(2)}) ON CONFLICT (slug) DO NOTHING;",
           s, flags=re.S)
# Document versions: remove OR IGNORE
s = re.sub(r"INSERT OR IGNORE INTO documentum_documentversion \(([^)]+)\) VALUES \((.+?)\);",
           lambda m: f"INSERT INTO documentum_documentversion ({m.group(1)}) VALUES ({m.group(2)});",
           s, flags=re.S)

# Final check
if 'PRAGMA' in s:
    print('Warning: PRAGMA still present')
if 'INSERT OR IGNORE' in s:
    print('Warning: INSERT OR IGNORE still present')

outfile.write_text(s, encoding='utf-8')
print('Wrote', outfile)
print('\nPreview (first 40 lines):')
print('\n'.join(s.splitlines()[:40]))
