#!/bin/bash
# Create the schema for a SQLite database.
# Run this script from the main directory.

echo "Dumping schema..."

python manage.py sqlall \
    $(ls apps/ | grep -vE "(py|api|front)") \
    > schema.sql

echo "Adding default field to devices.trusted"

lines_found=$(grep '"trusted" bool NOT NULL' schema.sql | wc -l)
if [ $lines_found -ne 1 ]; then
    echo "> Could not fix devices.trusted field." 1>&2
    echo "> The line '\"trusted\" bool NOT NULL' should occur exactly once in schema.sql." 1>&2
    exit 1
fi

sed -i 's/"trusted" bool NOT NULL/"trusted" bool NOT NULL DEFAULT 0/' schema.sql

echo "Adding COLLATE NOCASE to all varchar fields"

sed -i -r 's/varchar([^,]*)(,?)/varchar\1 COLLATE NOCASE\2/' schema.sql

echo "Done, see schema.sql"
echo "Please remove 'COLLATE NOCASE' manually from the file and directory tables."
echo "Otherwise they'll consider upper- and lowercase filenames the same file."
