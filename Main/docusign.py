# Python3 Quick start example: embedded signing ceremony.
# Copyright (c) 2018 by DocuSign, Inc.
# License: The MIT License -- https://opensource.org/licenses/MIT

import base64, os
from flask import Flask, request, render_template, redirect
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Signer, SignHere, Tabs, Recipients, Document, \
    RecipientViewRequest
import get_documents
import re

access_token = 'eyJ0eXAiOiJNVCIsImFsZyI6IlJTMjU2Iiwia2lkIjoiNjgxODVmZjEtNGU1MS00Y2U5LWFmMWMtNjg5ODEyMjAzMzE3In0.AQkAAAABAAUABwCALlNrjTnXSAgAgG52edA510gCAF2HtnaajrlMjQ0RXfHzPDgVAAEAAAAYAAkAAAAFAAAAKwAAAC0AAAAvAAAAMQAAADIAAAA4AAAAMwAAADUAAAANACQAAABmMGYyN2YwZS04NTdkLTRhNzEtYTRkYS0zMmNlY2FlM2E5NzgwAICd2d-MOddINwD3KgqJBxtrQqmUr5Q_z5s7.5t-8Yq2IZLq_ZgRWCDy7PGX-G2RVFLXIeHs2RUIIh6uZVDhtmU08dw-iNkzAUNcxupq-OP_tomP_18W_-8LXhflqgPtLJ5EUMTfJwI8-dBapQwwdUyxhdo2Ivt3pAfSNFqAss8u8bZkHGGtv0IQqd_1Wgou5_dd8lBvYUXPvBeLfMpXTnWtSWPMO4vXI5mjg1D2CpteBcPq3IRy2DtD3pBI059--4Vaz9Tujw89x4TXYFB_VAj8fBVt189ay9WEVleW0M1HpqaI0mqP2y_Beu4AwupNPLqN3HGa-q_dGdge8u72TY47Qo6DM-KSN_0s2xn997zBMXIghX_IGlLi5QA'
account_id = '8998993'
# Recipient Information:
signer_name = 'Rafael'
signer_email = 'patrick.d.kao@gmail.com'
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

all_good_page = '''
        <html lang="en"><body><p>You're good. For now...</p></body>
        '''

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
    raw_text = get_documents.get_doc_text()
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
        return all_good_page
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
