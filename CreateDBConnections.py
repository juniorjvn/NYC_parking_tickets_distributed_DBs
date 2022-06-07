import sqlite3
import mariadb
import psycopg2
import firebirdsql
from psycopg2 import OperationalError


def create_sqlite_connection(path, messages=True):
    connection = None
    try:
        connection = sqlite3.connect(path)
        if messages:
            print("Connection to SQLite3 DB successful")
    except sqlite3.OperationalError:
        print("Error opening SQLITE3 database:\n", path)
        exit()
    return connection


def create_mariadb_connection(user, database='', password='', host='localhost', unix_socket=None, messages=True):
    connection = None
    try:
        connection = mariadb.connect(user=user, password=password, host=host, database=database,
                                     unix_socket=unix_socket)
        if messages:
            print("Connection to MariaDB successful")
    except mariadb.Error:
        print("Error opening MariaDB database:", database)
        exit()
    return connection


def create_postgres_connection(user='postgres', password='', database='', host=None, port=5432, messages=True):
    connection = None
    try:
        connection = psycopg2.connect(dbname=database, user=user, password=password, host=host, port=port)
        if messages:
            print("Connection to Postgres DB successful")
    except psycopg2.Error as e:
        print("Error opening Postgresql database:", e)
        exit()
    return connection


def create_firebird_connection(user, password, database, role=None, host=None, messages=True):
    connection = None
    try:
        connection = firebirdsql.connect(user=user, password=password, database=database, role=role, host=host)
        if messages:
            print("Connection to Firebird DB successful")
    except firebirdsql.OperationalError:
        print("Error opening Firebird database:" )
        exit()
    return connection


