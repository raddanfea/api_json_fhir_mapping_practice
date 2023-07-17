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

        observation.update({'patientId': get_subject_id(subject)})

        observation.update({'performerId': get_performer_id(performer_list)})

        measurement_date = resource.get('effectiveDateTime', None)
        observation.update({'measurementDate': measurement_date})

        valueQuantity = recursive_search(entry, 'valueQuantity')
        valueQuantity = [q for q in valueQuantity if q]
        observation.update({'valueQuantity': valueQuantity})

        coding = recursive_search(entry, 'coding')
        # collapse and filter list
        coding = [item for sublist in coding for item in sublist if item.get('system', False) == 'http://loinc.org']
        observation.update({'measurementCoding': coding})

        date_now = datetime.now().isoformat()
        observation.update({'dataFetched': date_now})

        value = resource.get('valueString', False)
        if value: observation.update({'measurementValue': value})

        if resource.get('id', None): observations_list.append(observation)

        if components_list and False:
            for component in components_list:
                codings_list = component.get('code', dict()).get('coding', list())
                codings_list_filtered = [c for c in codings_list if c.get('system', False) == 'http://loinc.org']
                values = component.get('valueQuantity', None)
                if values is None: values = dict()
                value = values.get('value', None)
                unit = values.get('unit', None)

                observation.update({'measurementCoding': codings_list_filtered})
                observation.update({'measurementValue': value})
                observation.update({'measurementUnit': unit})

                if observation: observations_list.append(observation)

    return json.dumps(observations_list)
