-- INSERTs to create a new, (nearly) empty default database for Cygnet

-- Default group
INSERT INTO groups(id, name) VALUES (1, 'Default group');

-- Known file hash algorithms
INSERT INTO algorithms(id, name) VALUES (65536, 'PTS_MEAS_ALGO_SHA1_IMA');
INSERT INTO algorithms(id, name) VALUES (32768, 'PTS_MEAS_ALGO_SHA1');
INSERT INTO algorithms(id, name) VALUES (16384, 'PTS_MEAS_ALGO_SHA256');
INSERT INTO algorithms(id, name) VALUES (8192, 'PTS_MEAS_ALGO_SHA384');
INSERT INTO algorithms(id, name) VALUES (0, 'PTS_MEAS_ALGO_NONE');

