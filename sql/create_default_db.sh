#!/bin/bash

python ../manage.py sqlall tncapp | sqlite3 default.db
sqlite3 default.db < ./init_data.sql
rm ipsec.config.db
