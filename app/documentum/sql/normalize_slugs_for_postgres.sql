-- normalize_slugs_for_postgres.sql
-- SAFE slug normalization for documentum on Postgres (suitable for Supabase SQL editor)
-- What it does:
--  * creates extension unaccent (if available)
--  * normalizes `documentum_category.slug` from `name` and `documentum_document.slug` from `title`
--  * removes non-alphanumeric chars, replaces runs with '-', trims edges, lowercases
--  * ensures uniqueness by appending -1, -2 ... when needed
--  * logs changes with RAISE NOTICE (visible in query logs)

-- IMPORTANT: Run migrations on your production DB first so tables/columns exist.
-- Recommended: run inside a maintenance window and ensure no concurrent writes to these tables.

BEGIN;

-- ensure the extension is available for better transliteration
CREATE EXTENSION IF NOT EXISTS unaccent;

-- categories: generate ASCII slugs and guarantee uniqueness
LOCK TABLE documentum_category IN SHARE ROW EXCLUSIVE MODE;

DO $$
DECLARE
  rec RECORD;
  base TEXT;
  candidate TEXT;
  i INTEGER;
BEGIN
  FOR rec IN SELECT id, name, slug FROM documentum_category ORDER BY id LOOP
    base := lower(regexp_replace(unaccent(coalesce(rec.name, '')), '[^a-z0-9]+', '-', 'g'));
    base := regexp_replace(base, '(^-+|-+$)', '', 'g');
    IF base = '' THEN
      base := 'category-' || rec.id::text;
    END IF;

    candidate := base;
    i := 1;

    WHILE EXISTS(SELECT 1 FROM documentum_category WHERE slug = candidate AND id <> rec.id) LOOP
      candidate := base || '-' || i::text;
      i := i + 1;
    END LOOP;

    IF candidate IS DISTINCT FROM rec.slug THEN
      UPDATE documentum_category SET slug = candidate WHERE id = rec.id;
      RAISE NOTICE 'Category id=% slug: % -> %', rec.id, rec.slug, candidate;
    END IF;
  END LOOP;
END
$$;

-- documents: generate ASCII slugs from `title` and guarantee uniqueness across documents
LOCK TABLE documentum_document IN SHARE ROW EXCLUSIVE MODE;

DO $$
DECLARE
  rec RECORD;
  base TEXT;
  candidate TEXT;
  i INTEGER;
BEGIN
  FOR rec IN SELECT id, title, slug FROM documentum_document ORDER BY id LOOP
    base := lower(regexp_replace(unaccent(coalesce(rec.title, '')), '[^a-z0-9]+', '-', 'g'));
    base := regexp_replace(base, '(^-+|-+$)', '', 'g');
    IF base = '' THEN
      base := 'doc-' || rec.id::text;
    END IF;

    candidate := base;
    i := 1;

    WHILE EXISTS(SELECT 1 FROM documentum_document WHERE slug = candidate AND id <> rec.id) LOOP
      candidate := base || '-' || i::text;
      i := i + 1;
    END LOOP;

    IF candidate IS DISTINCT FROM rec.slug THEN
      UPDATE documentum_document SET slug = candidate WHERE id = rec.id;
      RAISE NOTICE 'Document id=% slug: % -> %', rec.id, rec.slug, candidate;
    END IF;
  END LOOP;
END
$$;

COMMIT;

-- Summary (check results)
SELECT 'categories' AS type, COUNT(*) AS total, COUNT(*) FILTER (WHERE slug ~ '[^a-z0-9\-]') AS non_ascii_slugs FROM documentum_category;
SELECT 'documents' AS type, COUNT(*) AS total, COUNT(*) FILTER (WHERE slug ~ '[^a-z0-9\-]') AS non_ascii_slugs FROM documentum_document;

-- End of script
