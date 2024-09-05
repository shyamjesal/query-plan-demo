sf = 1

import duckdb
import pathlib

for x in range(0, sf):
    con = duckdb.connect()
    con.sql('PRAGMA disable_progress_bar;SET preserve_insertion_order=false')
    con.sql(f"CALL dbgen(sf={sf} , children ={sf}, step = {x})")
    for tbl in ['nation', 'region', 'customer', 'supplier', 'lineitem', 'orders', 'partsupp', 'part']:
        pathlib.Path(f'{sf}/{tbl}').mkdir(parents=True, exist_ok=True)
        con.sql(f"COPY (SELECT * FROM {tbl}) TO '{sf}/{tbl}/{x:02d}.parquet' ")
    con.close()

con = duckdb.connect(f"{sf}/TPCH.DUCKDB")
con.execute(f'''
PRAGMA disable_progress_bar;
CREATE TABLE IF NOT EXISTS  lineitem AS SELECT * FROM '{sf}/lineitem/*.parquet';
CREATE TABLE IF NOT EXISTS  orders AS SELECT * FROM '{sf}/orders/*.parquet';
CREATE TABLE IF NOT EXISTS  partsupp AS SELECT * FROM '{sf}/partsupp/*.parquet';
CREATE TABLE IF NOT EXISTS  part AS SELECT * FROM '{sf}/part/*.parquet';
CREATE TABLE IF NOT EXISTS  supplier AS SELECT * FROM '{sf}/supplier/*.parquet';
CREATE TABLE IF NOT EXISTS  nation AS SELECT * FROM '{sf}/nation/*.parquet';
CREATE TABLE IF NOT EXISTS  region AS SELECT * FROM '{sf}/region/*.parquet';
CREATE TABLE IF NOT EXISTS  customer AS SELECT * FROM '{sf}/customer/*.parquet';
''')
con.close()

# GENERATE EMPTY HYPER FILE, probabaly there is a better way
from tableauhyperapi import HyperProcess, Telemetry, Connection, CreateMode, NOT_NULLABLE, NULLABLE, \
    SqlType, TableDefinition, Inserter, escape_name, escape_string_literal, HyperException, TableName

with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
    with Connection(endpoint=hyper.endpoint, database=f"{sf}/tpch.hyper",
                    create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
        connection.execute_query('SELECT 42')

from tableauhyperapi import HyperProcess, Telemetry, Connection, CreateMode, NOT_NULLABLE, NULLABLE, \
    SqlType, TableDefinition, Inserter, escape_name, escape_string_literal, HyperException, TableName


def hypersql(sql):
    with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(endpoint=hyper.endpoint, database=f"{sf}/tpch.hyper",
                        create_mode=CreateMode.NONE) as connection:
            data = connection.execute_list_query(sql)
            df = pd.DataFrame.from_records(data)
            print(df)


#load data into hyper
import pandas as pd

# import shutil
for tbl in ['nation', 'region', 'customer', 'supplier', 'lineitem', 'orders', 'partsupp', 'part']:
    array_list_ls = [f" '{sf}/{tbl}/{x:02d}.parquet' " for x in range(0, sf)]
    array_list = ", ".join(array_list_ls)
    hypersql(f""" create table "{tbl}" as (select * from external(array[{array_list}])) """)
