import json
import pprint

import requests

from ge_interview.model import InputModel

input_file = 'files/input_observations.json'
output_file = 'files/output_observations.json'


def read_json_file(path):
    with open(path, "r") as json_file:
        return json.load(json_file)


def send_test_request():
    input_data = read_json_file(input_file)


def show_json_structure():
    def remove_values(obj):
        if isinstance(obj, dict):
            return {key: remove_values(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [remove_values(element) for element in obj]
        else:
            return type(obj).__name__

    file = read_json_file(input_file)
    print([(key, type(value)) for key, value in file.items()])
    input_data = remove_values(file)
    pprint.pprint(input_data)


if __name__ == '__main__':
    # check out structure of the json file
    # show_json_structure()

    # test the pydantic model
    # input_pydantic = InputModel(**read_json_file(input_file))

    # send request
    headers = {"Content-Type": "application/json"}
    payload = read_json_file(input_file)
    response = requests.post("http://127.0.0.1:3000/convert", json=payload, headers=headers)
    pprint.pprint(json.loads(response.json()))
