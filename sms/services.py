from config.models import Sms
from integrations.superbase import send_sms_messages


def warn_of_policy_lapse(client_details):
    sms_config = Sms.objects.filter(template='Policy Lapse Warning').first()
    if sms_config is None:
        raise Exception("No Policy Lapse Warning SMS templates found")
    template_id = sms_config.template_id
    service_name = sms_config.service_name
    sms_from = sms_config.sms_from
    linked_organization = sms_config.linked_organization
    messages = []
    for client_detail in client_details:
        phone_number = client_detail['phone_number']
        entity = client_detail['entity']
        content = {
            "values": {
                "subject": "Policy Lapse Warning",
                "variables": [
                    entity
                ]
            }
        }
        data = {
            "template": template_id,
            "service_name": service_name,
            "external_ref": phone_number,
            "sms_from": sms_from,
            "sms_to": phone_number,
            "linked_organisation": linked_organization,
            "msg_content": content
        }
        messages.append(data)

    response = None
    try:
        print('sending sms messages')
        response = send_sms_messages(messages=messages)
    except Exception as e:
        print(f'Exception: {e}')
    return response
