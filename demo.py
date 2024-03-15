import json
from tableauhyperapi import HyperProcess, Telemetry, CreateMode, Connection, TableDefinition, SqlType, NOT_NULLABLE


query_text = None
with open("query1.sql", "r") as r:
    query_text = r.read()

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

print(query_pre_json)

query_json = json.loads(query_pre_json)

print(query_json)
