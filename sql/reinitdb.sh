#!/bin/bash

loc="`dirname \"$0\"`"

if [ ${#} == 1 ]
then
	psql -U postgres -c "REVOKE CONNECT ON DATABASE ${1} FROM public;"
	psql -U postgres -c "select pg_terminate_backend(pid) from pg_stat_activity where datname='${1}' and pid != pg_backend_pid();"
	psql -U postgres -d postgres -c "drop database ${1}"
	psql -U postgres -c "create database ${1}"
	psql -U postgres -d "${1}" -f "${loc}/tables.sql"
	psql -U postgres -d "${1}" -f "${loc}/views.sql"
	psql -U postgres -d "${1}" -f "${loc}/functions.sql"
	psql -U postgres -d "${1}" -f "${loc}/installmtimecols.sql"
	psql -U postgres -d "${1}" -f "${loc}/installnotifications.sql"
else
	echo Please specify a database name
fi
