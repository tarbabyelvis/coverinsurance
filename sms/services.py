from config.models import Sms
from integrations.superbase import send_sms_messages


def warn_of_policy_lapse(*phone_numbers):
    sms_config = Sms.objects.filter(template='Policy Lapse Warning').first()
    if sms_config is None:
        raise Exception("No Policy Lapse Warning SMS templates found")
    template_id = sms_config.template_id
    service_name = sms_config.service_name
    sms_from = sms_config.sms_from
    linked_organization = sms_config.linked_organization
    messages = []
    for phone_number in phone_numbers:
        data = {
            "template": template_id,
            "service_name": service_name,
            "external_ref": phone_number,
            "sms_from": sms_from,
            "sms_to": phone_number,
            "linked_organization": linked_organization
        }
        messages.append(data)
    return send_sms_messages(data=messages)
