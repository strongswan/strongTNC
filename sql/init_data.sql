-- INSERTs to create a new, (nearly) empty default database

-- Default group
INSERT INTO groups(id, name) VALUES (1, 'Default group');

-- Known file hash algorithms
INSERT INTO algorithms(id, name) VALUES (65536, 'SHA1_IMA');
INSERT INTO algorithms(id, name) VALUES (32768, 'SHA1');
INSERT INTO algorithms(id, name) VALUES (16384, 'SHA256');
INSERT INTO algorithms(id, name) VALUES (8192, 'SHA384');
INSERT INTO algorithms(id, name) VALUES (0, 'NONE');

