CREATE TABLE directories (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL
);
CREATE INDEX directories_path ON directories (
  path
);
CREATE TABLE files (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  dir INTEGER DEFAULT 0 REFERENCES directories(id),
  name TEXT NOT NULL
);
CREATE INDEX files_name ON files (
  name
);
CREATE TABLE products (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);
CREATE INDEX products_name ON products (
  name
);
CREATE TABLE algorithms (
  id INTEGER PRIMARY KEY,
  name VARCHAR(20) not NULL
);
CREATE TABLE file_hashes (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  file INTEGER NOT NULL REFERENCES files(id),
  product INTEGER NOT NULL REFERENCES products(id),
  device INTEGER DEFAULT 0,
  key INTEGER DEFAULT 0 REFERENCES keys(id),
  algo INTEGER NOT NULL REFERENCES algorithms(id),
  hash BLOB NOT NULL
);
CREATE TABLE keys (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  keyid BLOB NOT NULL,
  owner TEXT NOT NULL
);
CREATE INDEX keys_keyid ON keys (
  keyid
);
CREATE INDEX keys_owner ON keys (
  owner
);
CREATE TABLE groups (
  id INTEGER NOT NULL PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  parent INTEGER
);
CREATE TABLE groups_members (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  group_id INTEGER NOT NULL REFERENCES groups(id),
  device_id INTEGER NOT NULL REFERENCES devices(id),
  UNIQUE (group_id, device_id)
);
CREATE TABLE groups_product_defaults (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  group_id INTEGER NOT NULL REFERENCES groups(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  UNIQUE (group_id, product_id)
);
CREATE TABLE policies (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  type INTEGER NOT NULL,
  name VARCHAR(100) NOT NULL UNIQUE,
  argument TEXT DEFAULT '' NOT NULL,
  rec_fail INTEGER NOT NULL,
  rec_noresult INTEGER NOT NULL,
  file INTEGER DEFAULT 0 REFERENCES files(id),
  dir INTEGER DEFAULT 0 REFERENCES directories(id)
);
CREATE TABLE enforcements (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  policy INTEGER NOT NULL REFERENCES policies(id),
  group_id INTEGER NOT NULL REFERENCES groups(id),
  rec_fail INTEGER,
  rec_noresult INTEGER,
  max_age INTEGER NOT NULL,
  UNIQUE (policy, group_id)
);
CREATE TABLE sessions (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  time INTEGER NOT NULL,
  connection INTEGER NOT NULL,
  identity INTEGER DEFAULT 0 REFERENCES identities(id),
  device INTEGER DEFAULT 0 REFERENCES devices(id),
  product INTEGER DEFAULT 0 REFERENCES products(id),
  rec INTEGER DEFAULT 3
);
CREATE TABLE workitems (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  session INTEGER NOT NULL REFERENCES sessions(id),
  enforcement INTEGER NOT NULL REFERENCES enforcements(id),
  type INTEGER NOT NULL,
  arg_str TEXT,
  arg_int INTEGER DEFAULT 0,
  rec_fail INTEGER NOT NULL,
  rec_noresult INTEGER NOT NULL,
  rec_final INTEGER,
  result TEXT
);
CREATE INDEX workitems_sessions ON workitems (
  session
);
CREATE TABLE results (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  session INTEGER NOT NULL REFERENCES measurements(id),
  policy INTEGER NOT NULL REFERENCES policies(id),
  rec INTEGER NOT NULL,
  result TEXT NOT NULL
);
CREATE INDEX results_session ON results (
  session
);
CREATE TABLE components (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  vendor_id INTEGER NOT NULL,
  name INTEGER NOT NULL,
  qualifier INTEGER DEFAULT 0
);
CREATE TABLE key_component (
  key INTEGER NOT NULL,
  component INTEGER NOT NULL,
  depth INTEGER DEFAULT 0,
  seq_no INTEGER DEFAULT 0,
  PRIMARY KEY (key, component)
);
CREATE TABLE component_hashes (
  component INTEGER NOT NULL,
  key INTEGER NOT NULL,
  seq_no INTEGER NOT NULL,
  pcr INTEGER NOT NULL,
  algo INTEGER NOT NULL,
  hash BLOB NOT NULL,
  PRIMARY KEY(component, key, seq_no, algo)
);
CREATE TABLE packages (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);
CREATE INDEX packages_name ON packages (
  name
);
CREATE TABLE versions (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  package INTEGER NOT NULL REFERENCES packages(id),
  product INTEGER NOT NULL REFERENCES products(id),
  release TEXT NOT NULL,
  security INTEGER DEFAULT 0,
  blacklist INTEGER DEFAULT 0,
  time INTEGER DEFAULT 0
);
CREATE INDEX versions_release ON versions (
  release
);
CREATE INDEX versions_package_product ON versions (
  package, product
);
CREATE TABLE identities (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  type INTEGER NOT NULL,
  value BLOB NOT NULL,
  UNIQUE (type, value)
);
CREATE TABLE devices (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  description TEXT DEFAULT '',
  value TEXT NOT NULL,
  product INTEGER REFERENCES products(id),
  created INTEGER
);
CREATE INDEX devices_value ON devices (
  value
);
CREATE INDEX dir_files_name on files (dir, name);
CREATE TABLE regids (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);
CREATE INDEX regids_name ON regids (
  name
);
CREATE TABLE tags (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  regid INTEGER NOT NULL REFERENCES regids(id),
  unique_sw_id TEXT NOT NULL,
  value TEXT
);
CREATE INDEX tags_unique_sw_id ON tags (
  unique_sw_id
);
