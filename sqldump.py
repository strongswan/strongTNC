#!/usr/bin/python

import sqlite3

con = sqlite3.connect('ipsec.config.db')
for line in con.iterdump():
    if line[:11] == 'INSERT INTO':
            print line
