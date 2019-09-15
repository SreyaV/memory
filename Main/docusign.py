# Python3 Quick start example: embedded signing ceremony.
# Copyright (c) 2018 by DocuSign, Inc.
# License: The MIT License -- https://opensource.org/licenses/MIT

import base64, os
from flask import Flask, request, render_template, redirect
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Signer, SignHere, Tabs, Recipients, Document, \
    RecipientViewRequest
import re
import pendulum
import tika
tika.initVM()
from tika import parser

access_token = 'eyJ0eXAiOiJNVCIsImFsZyI6IlJTMjU2Iiwia2lkIjoiNjgxODVmZjEtNGU1MS00Y2U5LWFmMWMtNjg5ODEyMjAzMzE3In0.AQoAAAABAAUABwCA1c9ejznXSAgAgBXzbNI510gCAMvVYBwvyIxFgkVCFpMeHV8VAAEAAAAYAAkAAAAFAAAAKwAAAC0AAAAvAAAAMQAAADIAAAA4AAAAMwAAADUAAAANACQAAABmMGYyN2YwZS04NTdkLTRhNzEtYTRkYS0zMmNlY2FlM2E5NzgSAAEAAAALAAAAaW50ZXJhY3RpdmUwAAA_N16POddINwBNPPof2qbfTIKfNu5-qKQO.l_uW40yQUzVmw-rSKGTTEkgwUM7pHlSyvfKEFaXnxAeiY-QDuovS2KsGxfwmtzBzlvcEtuD36Btw9XvhX0L7tI1CO0VxHTk_yipuuLSlXkel6wVNvuNV9zZljP7Xgmq9oumDEDgoyh55Nlyz96cYH8PHbNan8oNwTfP9KAe8MDUVbADjVWiqJlX_scg7w7_oEnJsb7TiXGy8X4xyq2jYlveKRSkO30tYDTj66UgdcQ-aQT2hlcfDDQpcabo2UB6B1-7iKH3MBYTIxsLnKg3Cmbn2nEoIY-iNtMOU5f-FnWS5p4rw-P7hDVmEcIVrh51TOTJM-hu9cLKcp-JvDef-yA'
account_id = '8999292'

# Recipient Information:
signer_name = 'Rafael Reif'
signer_email = 'jamsabot@gmail.com'
# The document you wish to send. Path is relative to the root directory of this repo.
file_name_path = 'documents/resignation.pdf'
# The url of this web application
base_url = 'http://localhost:5000'
client_user_id = '123'  # Used to indicate that the signer will use an embedded
# Signing Ceremony. Represents the signer's userId within
# your application.
authentication_method = 'None'  # How is this application authenticating
# the signer? See the `authenticationMethod' definition
# https://developers.docusign.com/esign-rest-api/reference/Envelopes/EnvelopeViews/createRecipient

# The API base_path
base_path = 'https://demo.docusign.net/restapi'

master_dict = {"sex_offender": ["Jeff Epstein"], "racists": ["Alfred Sloan"],
               "fossil_fuels": ["David Koch", "Charles Koch"], "rich_assholes": ["Jeff Bezos"],
               "war_criminals": ["Henry Kisinger"]}

import os

# Set FLASK_ENV to development if it is not already set
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'development'

# Constants
APP_PATH = os.path.dirname(os.path.abspath(__file__))


def embedded_signing_ceremony():
    """
    The document <file_name> will be signed by <signer_name> via an
    embedded signing ceremony.
    """

    #
    # Step 1. The envelope definition is created.
    #         One signHere tab is added.
    #         The document path supplied is relative to the working directory
    #
    with open(os.path.join(APP_PATH, file_name_path), "rb") as file:
        content_bytes = file.read()
    base64_file_content = base64.b64encode(content_bytes).decode('ascii')

    # Create the document model
    document = Document(  # create the DocuSign document object
        document_base64=base64_file_content,
        name='Example document',  # can be different from actual file name
        file_extension='pdf',  # many different document types are accepted
        document_id=1  # a label used to reference the doc
    )

    # Create the signer recipient model 
    signer = Signer(  # The signer
        email=signer_email, name=signer_name, recipient_id="1", routing_order="1",
        client_user_id=client_user_id,  # Setting the client_user_id marks the signer as embedded
    )

    # Create a sign_here tab (field on the document)
    sign_here = SignHere(  # DocuSign SignHere field/tab
        document_id='1', page_number='1', recipient_id='1', tab_label='SignHereTab',
        x_position='195', y_position='147')

    # Add the tabs model (including the sign_here tab) to the signer
    signer.tabs = Tabs(sign_here_tabs=[sign_here])  # The Tabs object wants arrays of the different field/tab types

    # Next, create the top level envelope definition and populate it.
    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign this document sent from the Python SDK",
        documents=[document],  # The order in the docs array determines the order in the envelope
        recipients=Recipients(signers=[signer]),  # The Recipients object wants arrays for each recipient type
        status="sent"  # requests that the envelope be created and sent.
    )

    #
    #  Step 2. Create/send the envelope.
    #
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", "Bearer " + access_token)

    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.create_envelope(account_id, envelope_definition=envelope_definition)

    #
    # Step 3. The envelope has been created.
    #         Request a Recipient View URL (the Signing Ceremony URL)
    #
    envelope_id = results.envelope_id
    recipient_view_request = RecipientViewRequest(
        authentication_method=authentication_method, client_user_id=client_user_id,
        recipient_id='1', return_url=base_url + '/dsreturn',
        user_name=signer_name, email=signer_email
    )

    results = envelope_api.create_recipient_view(account_id, envelope_id,
                                                 recipient_view_request=recipient_view_request)

    #
    # Step 4. The Recipient View URL (the Signing Ceremony URL) has been received.
    #         Redirect the user's browser to it.
    #
    return results.url


def search(keyword):
    matched_documents = []
    raw_text = get_doc_text()
    to_find = master_dict[keyword]
    for text in raw_text:
        for word in to_find:
            matches = [m.start() for m in re.finditer(word, text[1])]
            if matches is not None:
                matched_documents.append((word, matches))

    return matched_documents

def search_all():
    all_keys = []
    for key in master_dict:
        result = search(key)
        if result is not None:
            all_keys.append(result)

    return all_keys

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

# Mainline
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        return redirect(embedded_signing_ceremony(), code=302)
    else:
        return render_template("home.html", url=request.url)


@app.route('/dsreturn', methods=['GET'])
def dsreturn():
    return '''
        <html lang="en"><body><p>The signing ceremony was completed with
          status {event}</p>
          <p>This page can also implement post-signing processing.</p></body>
    '''.format(event=request.args.get('event'))


@app.route('/keyword', methods=['GET'])
def keyword():
    print("searching for {}".format((request.args.get('keyword'))))
    found_keys = search(request.args.get('keyword'))
    if len(found_keys) == 0:
        return render_template("allgood.html")
    else:
        return render_template("keyword.html", found_keys=str(found_keys))

# @app.route('/checkall', methods=['GET', 'POST'])
# def checkall():
#     all_keys = search_all()
#     if len(all_keys) == 0:
#         return all_good_page
#     else:
#         return render_template("keyword.html", found_keys=str(all_keys))


app.run()
