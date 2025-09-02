import json
import os
import uuid

from json_handler.models import JSONData
from laboratory_django import settings


def get_search_results(queryset, search_term):
    queryset |= JSONData.objects.all()
    if search_term:
        try:
            key_value_pairs = search_term.split('&&')
            json_results = []
            for obj in queryset:
                if isinstance(obj.data, dict):
                    json_data = obj.data
                else:
                    json_data = json.loads(obj.data)  # Convert the JSON string to a Python object
                try:
                    if check_key_value_pairs(json_data, key_value_pairs):
                        json_results.append(obj)
                except json.JSONDecodeError:
                    # Handle the JSON decoding error
                    pass
                queryset = JSONData.objects.filter(
                    pk__in=[item.pk for item in json_results])  # Convert the list to a queryset
        except:
            return queryset

    return queryset


def check_key_value_pairs(data, key_value_pairs):
    for key_value_pair in key_value_pairs:
        search_key, search_value = key_value_pair.split(':', 1)
        if not search_json(data, search_key, search_value):
            return False
    return True


def search_json(data, search_key, search_value):
    # Search in json key value
    if isinstance(data, dict):
        for key, value in data.items():
            if search_key.lower() == key.lower() and search_value in str(value):
                return True
            if isinstance(value, (dict, list)):
                if search_json(value, search_key, search_value):
                    return True
    elif isinstance(data, list):
        for item in data:
            if search_json(item, search_key, search_value):
                return True
    return False


def handle_merge(ids_list):
    data_to_write = ""
    for _id in ids_list:
        try:
            obj = JSONData.objects.get(id=_id)
            data_to_write += str(obj.data)[1:-1] + ", "
        except JSONData.DoesNotExist:
            print(f"Object with id {_id} does not exist.")

    file_name = str(uuid.uuid4())
    final_data = "{" + data_to_write[0:-2].replace("'", '"') + "}"

    # Write Final Data To Json File
    directory = os.path.join(settings.MEDIA_ROOT, 'files')
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(os.path.join(directory, f"{file_name}.json"), 'a') as file:
        file.write(final_data)

    return file_name
