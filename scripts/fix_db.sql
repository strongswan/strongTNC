BEGIN;

-- Update schema for all relevant tables

ALTER TABLE "products" RENAME TO "products_tmp";
CREATE TABLE "products" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL COLLATE NOCASE
)
;
INSERT INTO "products" SELECT id, name FROM "products_tmp";
DROP TABLE "products_tmp";

ALTER TABLE "devices" RENAME TO "devices_tmp";
CREATE TABLE "devices" (
    "id" integer NOT NULL PRIMARY KEY,
    "value" varchar(255) NOT NULL COLLATE NOCASE,
    "description" text NULL COLLATE NOCASE,
    "product" integer NOT NULL REFERENCES "products" ("id"),
    "created" integer,
    "trusted" bool NOT NULL DEFAULT 0
)
;
INSERT INTO "devices" SELECT id, value, description, product, created, trusted FROM "devices_tmp";
DROP TABLE "devices_tmp";

ALTER TABLE "groups" RENAME TO "groups_tmp";
CREATE TABLE "groups" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(50) NOT NULL COLLATE NOCASE,
    "parent" integer REFERENCES "groups" ("id")
)
;
INSERT INTO "groups" SELECT id, name, parent FROM "groups_tmp";
DROP TABLE "groups_tmp";

ALTER TABLE "directories" RENAME TO "directories_tmp";
CREATE TABLE "directories" (
    "id" integer NOT NULL PRIMARY KEY,
    "path" varchar(255) NOT NULL UNIQUE
)
;
INSERT INTO "directories" SELECT id, path FROM "directories_tmp";
DROP TABLE "directories_tmp";

ALTER TABLE "files" RENAME TO "files_tmp";
CREATE TABLE "files" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL,
    "dir" integer NOT NULL REFERENCES "directories" ("id")
)
;
INSERT INTO "files" SELECT id, name, dir FROM "files_tmp";
DROP TABLE "files_tmp";

ALTER TABLE "packages" RENAME TO "packages_tmp";
CREATE TABLE "packages" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL COLLATE NOCASE
)
;
INSERT INTO "packages" SELECT id, name FROM "packages_tmp";
DROP TABLE "packages_tmp";

ALTER TABLE "versions" RENAME TO "versions_tmp";
CREATE TABLE "versions" (
    "id" integer NOT NULL PRIMARY KEY,
    "package" integer NOT NULL REFERENCES "packages" ("id"),
    "product" integer NOT NULL,
    "release" varchar(255) NOT NULL COLLATE NOCASE,
    "security" bool NOT NULL,
    "blacklist" integer,
    "time" integer NOT NULL
)
;
INSERT INTO "versions" SELECT id, package, product, release, security, blacklist, time FROM "versions_tmp";
DROP TABLE "versions_tmp";

ALTER TABLE "policies" RENAME TO "policies_tmp";
CREATE TABLE "policies" (
    "id" integer NOT NULL PRIMARY KEY,
    "type" integer NOT NULL,
    "name" varchar(100) NOT NULL UNIQUE COLLATE NOCASE,
    "argument" text,
    "rec_fail" integer NOT NULL,
    "rec_noresult" integer NOT NULL,
    "file" integer,
    "dir" integer
)
;
INSERT INTO "policies" SELECT id, type, name, argument, rec_fail, rec_noresult, file, dir FROM "policies_tmp";
DROP TABLE "policies_tmp";

ALTER TABLE "swid_tags" RENAME TO "swid_tags_tmp";
CREATE TABLE "swid_tags" (
    "id" integer NOT NULL PRIMARY KEY,
    "package_name" varchar(255) NOT NULL COLLATE NOCASE,
    "version" varchar(32) NOT NULL COLLATE NOCASE,
    "unique_id" varchar(255) NOT NULL COLLATE NOCASE,
    "swid_xml" text NOT NULL,
    "software_id" text NOT NULL
)
;
INSERT INTO "swid_tags" SELECT id, package_name, version, unique_id, swid_xml, software_id FROM "swid_tags_tmp";
DROP TABLE "swid_tags_tmp";

ALTER TABLE "swid_entities" RENAME TO "swid_entities_tmp";
CREATE TABLE "swid_entities" (
    "id" integer NOT NULL PRIMARY KEY,
    "name" varchar(255) NOT NULL COLLATE NOCASE,
    "regid" varchar(255) NOT NULL COLLATE NOCASE
)
;
INSERT INTO "swid_entities" SELECT id, name, regid FROM "swid_entities_tmp";
DROP TABLE "swid_entities_tmp";

ALTER TABLE "components" RENAME TO "components_tmp";
CREATE TABLE "components" (
    "id" integer NOT NULL PRIMARY KEY,
    "vendor_id" integer NOT NULL,
    "name" integer NOT NULL,
    "qualifier" integer NOT NULL,
    "label" varchar(255) NOT NULL COLLATE NOCASE
)
;
INSERT INTO "components" SELECT id, vendor_id, name, qualifier, label FROM "components_tmp";
DROP TABLE "components_tmp";

-- Re-create indexes on those tables

CREATE INDEX IF NOT EXISTS "products_4da47e07" ON "products" ("name");
CREATE INDEX IF NOT EXISTS "devices_f6915675" ON "devices" ("value");
CREATE INDEX IF NOT EXISTS "devices_7f1b40ad" ON "devices" ("product");
CREATE INDEX IF NOT EXISTS "groups_410d0aac" ON "groups" ("parent");
CREATE INDEX IF NOT EXISTS "files_4da47e07" ON "files" ("name");
CREATE INDEX IF NOT EXISTS "files_f85d3c8f" ON "files" ("dir");
CREATE INDEX IF NOT EXISTS "packages_4da47e07" ON "packages" ("name");
CREATE INDEX IF NOT EXISTS "versions_b6411b91" ON "versions" ("package");
CREATE INDEX IF NOT EXISTS "versions_7f1b40ad" ON "versions" ("product");
CREATE INDEX IF NOT EXISTS "versions_c12e4bec" ON "versions" ("release");
CREATE INDEX IF NOT EXISTS "versions_8cc08b5c" ON "versions" ("package", "product");
CREATE INDEX IF NOT EXISTS "policies_4e9667b7" ON "policies" ("file");
CREATE INDEX IF NOT EXISTS "policies_6e6a6202" ON "policies" ("dir");
CREATE INDEX IF NOT EXISTS "swid_tags_71da787b" ON "swid_tags" ("package_name");
CREATE INDEX IF NOT EXISTS "swid_tags_684d52f3" ON "swid_tags" ("unique_id");
CREATE INDEX IF NOT EXISTS "swid_tags_be2eff2c" ON "swid_tags" ("software_id");
CREATE INDEX IF NOT EXISTS "swid_entities_4da47e07" ON "swid_entities" ("name");
CREATE INDEX IF NOT EXISTS "swid_entities_b1ef5f73" ON "swid_entities" ("regid");

COMMIT;
