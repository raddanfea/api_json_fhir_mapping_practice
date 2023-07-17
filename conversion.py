import json
import re
from datetime import datetime


def recursive_search(json_obj, target_key):
    results = []

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key == target_key:
                results.append(value)
            else:
                results.extend(recursive_search(value, target_key))

    elif isinstance(json_obj, list):
        for item in json_obj:
            results.extend(recursive_search(item, target_key))

    return results


def get_performer_id(performer_list):
    if performer_list:
        performer_id = performer_list[0].get('reference', "")
        performer_id_match = re.match(r"Practitioner/(.+)", performer_id)
        performer_id = performer_id_match.group(1) if performer_id else None
    else:
        performer_id = "None"
    return performer_id


def get_subject_id(subject):
    if subject:
        subject_id = subject.get('reference', "")
        id_match = re.match(r"Patient/(.+)", subject_id)
        subject_id = id_match.group(1) if id_match else None
    else:
        subject_id = None
    return subject_id


def unit_conversion(observations_list):
    conversion_factors = {
        'K/µL': {'new_unit': '10^6/µL', 'conversion_factor': 1000},
        'mg/dL': {'new_unit': 'g/dL', 'conversion_factor': 0.01},
        '10^3/mL': {'new_unit': '10^6/µL', 'conversion_factor': 1000000},
        'cm': {'new_unit': 'm', 'conversion_factor': 0.01},
        'g/dL': {'new_unit': 'g/dL', 'conversion_factor': 1},
        'lb': {'new_unit': 'kg', 'conversion_factor': 0.453592},
        # For all other units, we will keep the same unit and value without conversion
        'g/dl': {'new_unit': 'g/dL', 'conversion_factor': 1},
        '%': {'new_unit': '%', 'conversion_factor': 1},
        'Cel': {'new_unit': 'Cel', 'conversion_factor': 1},
        'kg': {'new_unit': 'kg', 'conversion_factor': 1},
        '/min': {'new_unit': '/min', 'conversion_factor': 1},
        '10^6/µL': {'new_unit': '10^6/µL', 'conversion_factor': 1},
        'm': {'new_unit': 'm', 'conversion_factor': 1},
        None: {'new_unit': None, 'conversion_factor': 1},
    }

    for observation in observations_list:
        unit = observation["measurementUnit"]
        value = observation["measurementValue"]
        conversion_info = conversion_factors.get(unit, None)

        if conversion_info is not None:
            new_unit = conversion_info.get('new_unit', None)
            conversion_factor = conversion_info.get('conversion_factor', None)

            if new_unit and value is not None:
                converted_value = value * conversion_factor
                observation["measurementUnit"] = new_unit
                observation["measurementValue"] = converted_value


async def convert_to_fhir(data: dict):
    observations_list = list()

    for entry in data.get('entry', None):
        observation = dict()

        # sub nodes
        resource = entry.get('resource', dict())
        subject = resource.get('subject', dict())
        performer_list = resource.get('performer', list())
        code = resource.get('code', dict())
        category = resource.get('category', list())
        components_list = resource.get('component', None)
        code_codings_list = code.get('coding', None) if code else dict()
        category_codings_list = [item.get('coding') for item in category if
                                 item.get('coding', False)] if category else dict()

        # values
        observation.update({'observationId': resource.get('id', None)})

        if not resource.get('id', None):
            continue

        observation.update({'patientId': get_subject_id(subject)})

        observation.update({'performerId': get_performer_id(performer_list)})

        measurement_date = resource.get('effectiveDateTime', None)
        if not measurement_date: measurement_date = resource.get('issued', None)
        observation.update({'measurementDate': measurement_date})

        coding = recursive_search(entry, 'coding')
        # collapse and filter list
        coding = [item for sublist in coding for item in sublist if item.get('system', False) == 'http://loinc.org']
        observation.update({'measurementCoding': coding})

        date_now = datetime.now().isoformat()
        observation.update({'dataFetched': date_now})

        valueQuantity = recursive_search(entry, 'valueQuantity')
        valueQuantity = [q for q in valueQuantity if q]

        if not valueQuantity:

            # value in valueString
            value = resource.get('valueString', False)
            observation.update({'measurementValue': value})

            #  value in valueCodableConcept
            value = resource.get('valueCodeableConcept', False)
            if value: observation.update({'measurementValue': value.get('text', None)})

            observation.update({'measurementUnit': None})
            observations_list.append(observation)
            continue

        for each in valueQuantity:
            observation.update({'measurementValue': each.get('value', None)})
            observation.update({'measurementUnit': each.get('unit', None)})
            observations_list.append(observation)

    unit_conversion(observations_list)

    return json.dumps(observations_list)
