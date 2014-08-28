BEGIN;
CREATE TABLE "swid_tagstats" (
    "id" integer NOT NULL PRIMARY KEY,
    "tag_id" integer NOT NULL REFERENCES "swid_tags" ("id"),
    "device_id" integer NOT NULL REFERENCES "devices" ("id"),
    "first_seen_id" integer NOT NULL REFERENCES "sessions" ("id"),
    "last_seen_id" integer NOT NULL REFERENCES "sessions" ("id"),
    UNIQUE ("tag_id", "device_id")
)
;
CREATE INDEX "swid_tagstats_5659cca2" ON "swid_tagstats" ("tag_id");
CREATE INDEX "swid_tagstats_b6860804" ON "swid_tagstats" ("device_id");
CREATE INDEX "swid_tagstats_b38d6251" ON "swid_tagstats" ("first_seen_id");
CREATE INDEX "swid_tagstats_be0e8b5c" ON "swid_tagstats" ("last_seen_id");
COMMIT;
