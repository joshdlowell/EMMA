import json
import requests


def get_device_status():
    """
    function for getting the current status of all devices in the "controllable" list

    Returns:
        a string representation of the devices, their friendly names, and the current statuses
    """
    url = "https://homeassistant.home:8123/api/"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2NTllN2QwODY3MjM0ZmMxOGMwOTI5ZDJlYzAwMzI0NCIsImlhdCI6MTcyOTM0OTc1NCwiZXhwIjoyMDQ0NzA5NzU0fQ.QAqbSJS-Wg3cV_vJaHci90Cl7G377r-mtJl7I8fecyc",
        "content-type": "application/json",
    }
    # # Get all the things
    # response = get(url + "states", headers=headers, verify=False)
    # formatted = json.loads(response.text)

    switchable_status = []
    for item in controllable:
        response = requests.get(url + "states/" + item['entity_id'], headers=headers, verify=False)
        details = json.loads(response.text)
        if not details['attributes'].get('friendly_name', None):
            details['attributes']['friendly_name'] = item['friendly_name']
        else:
            details['attributes']['friendly_name'] = item['friendly_name'].append(details['attributes']['friendly_name'])

        switchable_status.append({
            'entity_id': details["entity_id"],
            'state': details['state'],
            'attributes': details['attributes']})

    return f'device_list : {json.dumps(switchable_status)}'


def control_smart_home_device(entity_states):
    """
    The tool for changing states of entities in home assistant

    args:
        entity_ids: a dict of entity_id:desired state key pairs of changes to be made
    :param entity_ids:
    :param state:
    :return:
    """
    url = "https://homeassistant.home:8123/api/"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2NTllN2QwODY3MjM0ZmMxOGMwOTI5ZDJlYzAwMzI0NCIsImlhdCI6MTcyOTM0OTc1NCwiZXhwIjoyMDQ0NzA5NzU0fQ.QAqbSJS-Wg3cV_vJaHci90Cl7G377r-mtJl7I8fecyc",
        "content-type": "application/json",
    }
    entity_ids = entity_states.keys()

    content = ''
    for entity_id in entity_ids:
        if entity_id not in [x['entity_id'] for x in controllable]:
            print(entity_id)
            content += f"FAIL, {entity_id} is not a valid entity id try again\n"
            continue

        response = requests.get(url + "states/" + entity_id, headers=headers, verify=False)
        details = json.loads(response.text)
        if details['state'] == entity_states['entity_id']:
            content += f"FAIL, {entity_id} was already in {details['state']}\n"
            continue

        data = {"entity_id": entity_id}
        state_dict = {
            'on': 'turn_on',
            'off': 'turn_off'
        }
        entity_id_domain = entity_id.split('.')[0]
        full_url = f"{url}services/{entity_id_domain}/{state_dict[entity_states['entity_id']]}"
        response = requests.post(full_url, headers=headers, json=data, verify=False)
        details = json.loads(response.text)

        new_state = None
        status = None
        for entry in details:
            new_state = entry.get("state", None)
            if entity_states['entity_id'] == new_state:
                status = f"SUCCESS, {entity_id} is now {new_state}\n"
                break
        if not status:
            content += f"FAIL, {entity_id} is now {new_state} and did not update\n"
        else:
            content += status
    return content


# if __name__ == '__main__':
#
#     new_state = 'off'
#     states = get_device_list()
#     for state in states:
#         if state['entity_id'] == 'light.basement_tv_lights' and state['state'] == 'off':
#             new_state = 'on'
#
#     print("SETTING DEVICE STATE")
#     set_device_state('light.basement_tv_lights', new_state)

controllable = [
    {'entity_id': 'switch.all_outside_lights', 'friendly_name': ['front lights', 'front light']},
    {'entity_id': 'light.bathroom_light_switch', 'friendly_name': ['bathroom lights', 'bathroom light']},
    {'entity_id': 'light.kitchen_light', 'friendly_name': ['kitchen lights', 'kitchen light']},
    {'entity_id': 'lock.side_door_lock', 'friendly_name': ['side door']},
    {'entity_id': 'lock.back_door_lock', 'friendly_name': ['back door']},
    {'entity_id': 'lock.front_door_lock', 'friendly_name': ['front door']},
    {'entity_id': 'light.street_lamp', 'friendly_name': ['street light']},
    {'entity_id': 'switch.bathroom_fan_switch', 'friendly_name': ['bathroom fan']},
    {'entity_id': 'light.livingroom_light', 'friendly_name': ['living room lights']},
    {'entity_id': 'light.hallway_light', 'friendly_name': ['hallway lights']},
    {'entity_id': 'light.basement_light', 'friendly_name': ['basement lights']},
    {'entity_id': 'light.hall_table_lamp', 'friendly_name': ['hall lamp', 'table lamp']},
    {'entity_id': 'light.dining_room_light', 'friendly_name': ['dining room lights', 'dining_room_light']},
    {'entity_id': 'switch.livingroom_plug', 'friendly_name': ['living room plug', 'cute lamp']},
    {'entity_id': 'switch.dining_room_plug', 'friendly_name': ['dining room plug', 'christmas tree']},
    {'entity_id': 'light.basement_tv_lights', 'friendly_name': ['basement tv lights', 'basement tv leds']},
    {'entity_id': 'light.kitchen_leds', 'friendly_name': ['kitchen leds']},
    {'entity_id': 'light.basement_bulb_1', 'friendly_name': ['basement bulb 1']},
    # {'entity_id': 'switch.wyze_plug_outdoor', 'friendly_name': ['front lights']},
    {'entity_id': 'light.basement_bulb_2', 'friendly_name': ['basement bulb 2']},
    {'entity_id': 'light.gwen_bulb_1', 'friendly_name': ['gwens bulb 1']},
    {'entity_id': 'light.gwen_bulb_2', 'friendly_name': ['gwens bulb 2']},
    # {'entity_id': 'switch.outdoor_plug_2', 'friendly_name': ['other']},
    {'entity_id': 'switch.outdoor_plug_1', 'friendly_name': ['landscape lights', 'landscape light']},
    {'entity_id': 'switch.harmony_hub_basement_tv', 'friendly_name': ['basement tv']},
    {'entity_id': 'switch.harmony_hub_livingroom_tv', 'friendly_name': ['living room tv']}
]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "control_smart_home_device",
            "description": "call this tool to set the state of any device_id or friendly_name in the device_list.\n"
                           "make sure to use tool call tags",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_ids": {
                        "type": "dict",
                        "description": 'A dict where the keys are "device_id" of devices to control from the device_'
                                       'list and the value for each key is the desired state of that key\nEach '
                                       'entity_id key must exactly match one of the entity_ids from the device_list',
                    },
                },
                "required": ["entity_states"],
            },
        },
    },
]