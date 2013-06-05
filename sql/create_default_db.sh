#!/bin/bash

python ../manage.py sqlall cygapp | sqlite3 default.db 
sqlite3 default.db < ./init_data.sql
rm ipsec.config.db
