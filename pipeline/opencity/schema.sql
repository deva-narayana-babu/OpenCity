-- OpenCity database schema (SQLite).
-- Every number keeps a trail back to the fetch that produced it and the raw
-- snapshot archived for that fetch. Missing data is stored as status
-- 'not_reported', never as 0.

CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

-- One row per data source (one adapter module in opencity/sources/).
CREATE TABLE IF NOT EXISTS source (
  source_id      TEXT PRIMARY KEY,
  name           TEXT NOT NULL,
  publisher      TEXT NOT NULL,
  url            TEXT NOT NULL,
  module         TEXT NOT NULL,
  cadence        TEXT NOT NULL,
  interval_hours REAL NOT NULL,
  parser_version TEXT NOT NULL,
  geo_note       TEXT,
  licence_note   TEXT,
  notes          TEXT,
  enabled        INTEGER NOT NULL DEFAULT 1,
  updated_at     TEXT NOT NULL
);

-- One row per invocation of the refresher.
CREATE TABLE IF NOT EXISTS run (
  run_id      INTEGER PRIMARY KEY,
  started_at  TEXT NOT NULL,
  finished_at TEXT,
  command     TEXT,
  status      TEXT            -- ok | partial | failed
);

-- One row per HTTP request made by an adapter (or per archived file re-parsed).
CREATE TABLE IF NOT EXISTS fetch (
  fetch_id       INTEGER PRIMARY KEY,
  run_id         INTEGER REFERENCES run(run_id),
  source_id      TEXT NOT NULL REFERENCES source(source_id),
  url            TEXT NOT NULL,
  request_key    TEXT NOT NULL,   -- method + url + body hash: "the same request" across runs
  fetched_at     TEXT NOT NULL,
  http_status    INTEGER,
  content_type   TEXT,
  bytes          INTEGER,
  sha256         TEXT,
  raw_path       TEXT,            -- relative to the data directory
  etag           TEXT,
  last_modified  TEXT,
  changed        INTEGER,         -- 1 = content differs from the previous fetch of this request
  status         TEXT NOT NULL,   -- pending | ok | unchanged | not_modified | skipped | http_error | network_error | blocked | parse_error | validation_error
  parser         TEXT,            -- source_id@parser_version that parsed it
  error          TEXT,
  n_observations INTEGER,
  n_records      INTEGER,
  meta           TEXT             -- adapter context (JSON)
);
CREATE INDEX IF NOT EXISTS fetch_by_source  ON fetch(source_id, fetched_at);
CREATE INDEX IF NOT EXISTS fetch_by_request ON fetch(request_key, fetched_at);

CREATE TABLE IF NOT EXISTS metric (
  metric_id   TEXT PRIMARY KEY,
  label       TEXT NOT NULL,
  unit        TEXT,
  module      TEXT NOT NULL,
  description TEXT,
  source_id   TEXT NOT NULL REFERENCES source(source_id)
);

-- Geographies: smc_city, smc_zone, smc_ward, surat_district, tapi_district,
-- apmc_market, reporting_centre, dam, raingauge, ...
CREATE TABLE IF NOT EXISTS geo (
  geo_level    TEXT NOT NULL,
  geo_code     TEXT NOT NULL,
  name         TEXT NOT NULL,
  parent_level TEXT,
  parent_code  TEXT,
  note         TEXT,
  PRIMARY KEY (geo_level, geo_code)
);

-- Tidy, long-format numbers. One row per metric x place x period x extra dimensions.
CREATE TABLE IF NOT EXISTS observation (
  metric_id       TEXT NOT NULL REFERENCES metric(metric_id),
  geo_level       TEXT NOT NULL,
  geo_code        TEXT NOT NULL,
  period_start    TEXT NOT NULL,  -- ISO date or datetime, Asia/Kolkata
  period_end      TEXT NOT NULL,
  dims            TEXT NOT NULL DEFAULT '{}',  -- canonical JSON, e.g. {"commodity":"Onion"}
  value           REAL,
  value_text      TEXT,
  status          TEXT NOT NULL CHECK (status IN ('reported', 'not_reported', 'withheld')),
  publisher_as_of TEXT,           -- "last updated" date printed by the publisher, if any
  source_id       TEXT NOT NULL REFERENCES source(source_id),
  fetch_id        INTEGER NOT NULL REFERENCES fetch(fetch_id),  -- fetch that set the current value
  parser          TEXT NOT NULL,  -- latest parser version that produced this value
  first_seen      TEXT NOT NULL,
  last_seen       TEXT NOT NULL,
  PRIMARY KEY (metric_id, geo_level, geo_code, period_start, period_end, dims)
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS observation_by_source ON observation(source_id);
CREATE INDEX IF NOT EXISTS observation_by_period ON observation(metric_id, period_start);

-- Every time a publisher changes a number we already had, the old value is kept here.
CREATE TABLE IF NOT EXISTS observation_revision (
  revision_id    INTEGER PRIMARY KEY,
  metric_id      TEXT NOT NULL,
  geo_level      TEXT NOT NULL,
  geo_code       TEXT NOT NULL,
  period_start   TEXT NOT NULL,
  period_end     TEXT NOT NULL,
  dims           TEXT NOT NULL,
  old_value      REAL,
  old_value_text TEXT,
  old_status     TEXT,
  old_fetch_id   INTEGER,
  new_value      REAL,
  new_value_text TEXT,
  new_status     TEXT,
  new_fetch_id   INTEGER,
  revised_at     TEXT NOT NULL
);

-- Non-numeric entities (corporators, PIOs, documents) with validity history:
-- valid_to IS NULL means "current".
CREATE TABLE IF NOT EXISTS record (
  record_type TEXT NOT NULL,
  record_key  TEXT NOT NULL,
  attrs       TEXT NOT NULL,      -- canonical JSON
  valid_from  TEXT NOT NULL,
  valid_to    TEXT,
  source_id   TEXT NOT NULL REFERENCES source(source_id),
  fetch_id    INTEGER NOT NULL REFERENCES fetch(fetch_id),
  PRIMARY KEY (record_type, record_key, valid_from)
);
CREATE INDEX IF NOT EXISTS record_current ON record(record_type, valid_to);

-- ---------- convenience views (recreated on every migration) ----------

DROP VIEW IF EXISTS v_observation;
CREATE VIEW v_observation AS
SELECT o.metric_id, m.label AS metric_label, m.unit, m.module,
       o.geo_level, o.geo_code, g.name AS geo_name,
       o.period_start, o.period_end, o.dims, o.value, o.value_text, o.status,
       o.publisher_as_of, o.source_id, s.publisher, f.url AS source_url,
       f.fetched_at AS retrieved_at, f.sha256 AS raw_sha256, o.parser,
       o.first_seen, o.last_seen
FROM observation o
JOIN metric m ON m.metric_id = o.metric_id
JOIN source s ON s.source_id = o.source_id
JOIN fetch f  ON f.fetch_id = o.fetch_id
LEFT JOIN geo g ON g.geo_level = o.geo_level AND g.geo_code = o.geo_code;

DROP VIEW IF EXISTS v_current_record;
CREATE VIEW v_current_record AS
SELECT record_type, record_key, attrs, valid_from, source_id, fetch_id
FROM record WHERE valid_to IS NULL;

-- Freshness per source: last attempt, last success, and what is stored.
DROP VIEW IF EXISTS v_source_health;
CREATE VIEW v_source_health AS
SELECT s.source_id, s.name, s.module, s.cadence, s.interval_hours, s.enabled,
       (SELECT max(fetched_at) FROM fetch f WHERE f.source_id = s.source_id) AS last_attempt,
       (SELECT max(fetched_at) FROM fetch f WHERE f.source_id = s.source_id
          AND f.status IN ('ok', 'unchanged', 'not_modified', 'skipped')) AS last_success,
       (SELECT status FROM fetch f WHERE f.source_id = s.source_id
          ORDER BY fetch_id DESC LIMIT 1) AS last_status,
       (SELECT count(*) FROM fetch f WHERE f.source_id = s.source_id
          AND f.status IN ('http_error', 'network_error', 'blocked', 'parse_error', 'validation_error')
          AND f.run_id = (SELECT max(run_id) FROM fetch g WHERE g.source_id = s.source_id)) AS errors_last_run,
       (SELECT error FROM fetch f WHERE f.source_id = s.source_id AND f.error IS NOT NULL
          AND f.run_id = (SELECT max(run_id) FROM fetch g WHERE g.source_id = s.source_id)
          ORDER BY fetch_id DESC LIMIT 1) AS last_error,
       (SELECT count(*) FROM observation o WHERE o.source_id = s.source_id) AS n_observations,
       (SELECT count(*) FROM record r WHERE r.source_id = s.source_id AND r.valid_to IS NULL) AS n_current_records,
       (SELECT max(period_end) FROM observation o WHERE o.source_id = s.source_id
          AND o.status = 'reported') AS latest_period
FROM source s;
