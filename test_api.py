import json
import pprint

import requests

from ge_interview.model import InputModel

input_file = 'files/input_observations.json'
output_file = 'files/output_observations.json'


def read_json_file(path):
    with open(path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def send_test_request():
    headers = {"Content-Type": "application/json"}
    payload = read_json_file(input_file)
    response = requests.post("http://127.0.0.1:3000/convert", json=payload, headers=headers)
    if not response.status_code == 200:
        pprint.pprint(response.text)
    else:
        pprint.pprint(json.loads(response.json()))
    return response


def show_json_structure():
    def remove_values(obj):
        if isinstance(obj, dict):
            return {key: remove_values(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [remove_values(element) for element in obj]
        else:
            return type(obj).__name__

    file = read_json_file(input_file)
    input_data = remove_values(file)
    pprint.pprint(input_data)


def check_units(resp):
    units = set()
    for each in json.loads(resp.json()):
        units.add(each.get('measurementUnit', 'MISSING'))

    print("Units:", *units)


if __name__ == '__main__':
    # check out structure of the json file
    show_json_structure()

    # test the pydantic model
    InputModel(**read_json_file(input_file))

    # test
    response = send_test_request()

    # check output units
    check_units(response)
