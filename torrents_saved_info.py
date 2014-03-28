#!/usr/bin/python
import sqlite3

def create_table(conn, name):
    sor = conn.cursor()
    create_sql = "CREATE TABLE " + name
    create_sql += " (addr text, fname text, down_count int, fsha1 text)"
    sor.execute(create_sql)

#unit test
conn = sqlite3.connect("temp.db")

create_table(conn,"ttg")

conn.close()
