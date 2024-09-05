## open and parse json file
import json


# if main then run
if __name__ == "__main__":
    with open("query1.sql", "r") as f:
        # get string from file
        query_pre_json = f.read()
        print(query_pre_json[532: 583])
        print(query_pre_json[76: 91])

