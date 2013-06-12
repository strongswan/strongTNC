#!/usr/bin/python

"""
Used to dump all data in ipsec.config.db into sql statements
"""

import sqlite3

con = sqlite3.connect('ipsec.config.db')
for line in con.iterdump():
    if line[:11] == 'INSERT INTO':
            print line
