import json

with open("result.json", "r") as write_file:
    print(json.dump(data, write_file))