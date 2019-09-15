import base64, os
from docusign_esign import ApiClient, EnvelopesApi
import pendulum  # pip install pendulum
import pprint
import tika
tika.initVM()
from tika import parser

access_token = 'eyJ0eXAiOiJNVCIsImFsZyI6IlJTMjU2Iiwia2lkIjoiNjgxODVmZjEtNGU1MS00Y2U5LWFmMWMtNjg5ODEyMjAzMzE3In0.AQoAAAABAAUABwAAQ5L0RDnXSAgAAIO1Aog510gCAF2HtnaajrlMjQ0RXfHzPDgVAAEAAAAYAAkAAAAFAAAAKwAAAC0AAAAvAAAAMQAAADIAAAA4AAAAMwAAADUAAAANACQAAABmMGYyN2YwZS04NTdkLTRhNzEtYTRkYS0zMmNlY2FlM2E5NzgSAAEAAAALAAAAaW50ZXJhY3RpdmUwAAC8_vBEOddINwD3KgqJBxtrQqmUr5Q_z5s7.wzFlaQ0oMUqPxz2XTQ0wX9-tHkJuyPdCeG5BDznU4rf0cEOkPomHBXtYqujsPBlQ-cS2zDAmZrL_Ebf77Rwu4An79WN4UHyDPoBKJFz47Renw4HeI9_fqOdu1P-6i3jv8MIAHwAmiWfTD9Vc_duOVo458s6dB3hG6Zf6qK64p6O078X7puZra2H2tZXSwMLh0hETUY3OiW9moxQSl9o6BWog094UPEgoF1KF9jOTmAuttRy_7ybppQoZj3-6Hpx3yTAIpJy6_pyVdN5Fp5Csw982bgEuI74TwhAAniimfu6Z-ZjZo1fcd5UfxIhRpKQSGtj-7uBke_t7KHzm-Zmlig'
account_id = '8998993'
base_path = 'https://demo.docusign.net/restapi'


def list_envelopes():
    """
    Lists the user's envelopes created in the last 10 days
    """

    #
    # Step 1. Prepare the options object
    #
    from_date = pendulum.now().subtract(days=10).to_iso8601_string()
    #
    # Step 2. Get and display the results
    #
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", "Bearer " + access_token)

    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.list_status_changes(account_id, from_date=from_date)
    return results

def get_envelopes_api():
    """
       Lists the user's envelopes created in the last 10 days
       """


    #
    # Step 2. Get and display the results
    #
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", "Bearer " + access_token)

    envelope_api = EnvelopesApi(api_client)
    return envelope_api

def get_doc_text():
    to_ret = []
    env_api = get_envelopes_api()
    #
    # Step 1. Prepare the options object
    #
    from_date = pendulum.now().subtract(days=10).to_iso8601_string()
    status_changes = env_api.list_status_changes(account_id, from_date=from_date)
    for env in status_changes.envelopes:
        combined = env_api.get_document(account_id, 'combined', env.envelope_id)
        parsed = parser.from_file(combined)
        to_ret.append((env.envelope_id ,parsed['content']))
        print(parsed['content'])

    return to_ret

if __name__ == '__main__':
    # Mainline
    results = list_envelopes()
    print("\nEnvelopes:\n")
    pprint.pprint(results, indent=4, width=80)
    get_doc_text()
