import json
import tempfile
from tableauhyperapi import HyperProcess, Telemetry, CreateMode, Connection, TableDefinition, SqlType, NOT_NULLABLE
import duckdb
import os
import time

scaleFactor = "1"
queryNumber = "6"

def genHyperPlan(query_text:str, input_filename:str):
    # Hyper DB
    hyper_parameters = {
        # "log_config": "",
        "max_query_size": "10000000000",
        "hard_concurrent_query_thread_limit": str(1),
        "initial_compilation_mode": "o"
    }
    hyper_location = scaleFactor + "/tpch.hyper"

    explain_options = "EXPLAIN (VERBOSE)"
    query_pre_json = ""

    with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters=hyper_parameters) as hyper:
        with Connection(hyper.endpoint, hyper_location, CreateMode.CREATE_IF_NOT_EXISTS) as connection:
            query_pre_json = connection.execute_list_query(explain_options + query_text)[0][0]

    query_json =  json.loads(query_pre_json)
    with open("hyperPlans"+scaleFactor+"x/"+input_filename + "_hyperPlan.json", "w") as f:
        json.dump(query_json, f, indent=4)

def genDuckPlan(query_text:str, input_filename:str):
    # Duck DB
    duckdb_output_name = "duckPlans"+scaleFactor+"x/" + input_filename + "_duck_db_explain.json"

    if os.path.exists(duckdb_output_name):
        os.remove(duckdb_output_name)

    explain_commands = ["PRAGMA enable_profiling='json';",
                        "PRAGMA profile_output='" + str(duckdb_output_name) + "';",
                        "PRAGMA explain_output='ALL';",
                        "SET explain_output='all';",
                        "SET threads TO " + str(1) + ";"]

    duck_location = scaleFactor + "/TPCH.DUCKDB"
    connection = duckdb.connect(database=duck_location, read_only=False)

    for command in explain_commands:
        connection.execute(command).fetchall()

    connection.execute(query_text).fetchall()

    # with open(duckdb_output_name, "r") as f:
    #     query_json = json.load(f)

    # print(json.dumps(query_json, indent=4))

# if os.path.exists(duckdb_output_name):
#     os.remove(duckdb_output_name)

def getQueryText(source_prefix:str, input_filename:str):
    with open(source_prefix + input_filename, "r") as f:
        query_text = f.read()
    return query_text

if __name__ == "__main__":
    source_prefix = "query/"
    # input_filename = "query" + queryNumber + ".sql"
    for queryNum in range(1, 23):
        queryNumber = queryNum
        input_filename = "query" + str(queryNumber) + ".sql"
        print(queryNum)
        queryText = getQueryText(source_prefix, input_filename)
        genHyperPlan(queryText, input_filename)
        # genDuckPlan(queryText, input_filename)
