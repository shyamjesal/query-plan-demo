import json
from tableauhyperapi import HyperProcess, Telemetry, CreateMode, Connection, TableDefinition, SqlType, NOT_NULLABLE
import duckdb
import os
import time

query_text = None
with open("query1.sql", "r") as f:
    query_text = f.read()

# Hyper DB
hyper_parameters =  {
    #"log_config": "",
    "max_query_size": "10000000000",
    "hard_concurrent_query_thread_limit": str(1), 
    "initial_compilation_mode": "o"
}
hyper_location = "hyperdb_tpch.hyper"

explain_options = "EXPLAIN (VERBOSE)"
query_pre_json = ""

with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters=hyper_parameters) as hyper:
        with Connection(hyper.endpoint, hyper_location, CreateMode.CREATE_IF_NOT_EXISTS) as connection:
            query_pre_json = connection.execute_list_query(explain_options + query_text)[0][0]

query_json = json.loads(query_pre_json)
print(query_json)

# Duck DB
duckdb_output_name = "query1_duck_db_explain.json"

if os.path.exists(duckdb_output_name):
    os.remove(duckdb_output_name)

explain_commands = ["PRAGMA enable_profiling='json';",
    "PRAGMA profile_output='" + str(duckdb_output_name) + "';",
    "PRAGMA explain_output='ALL';",
    "SET explain_output='all';",
    "SET threads TO " + str(1) + ";"]
    
duck_location = "duckdb_tpch.duckdb"
connection = duckdb.connect(database=duck_location, read_only=False)

for command in explain_commands:
    connection.execute(command).fetchall()
    
connection.execute(query_text).fetchall()

with open(duckdb_output_name, "r") as f:
    query_json = json.load(f)
    
print(query_json)

if os.path.exists(duckdb_output_name):
    os.remove(duckdb_output_name)
