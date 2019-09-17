# Python3 Quick start example: embedded signing ceremony.
# Copyright (c) 2018 by DocuSign, Inc.
# License: The MIT License -- https://opensource.org/licenses/MIT

import base64, os
import requests
import uuid
import ds_config
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_oauthlib.client import OAuth
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Signer, SignHere, Tabs, Recipients, Document, \
    RecipientViewRequest
import re
from datetime import datetime, timedelta
import tika
tika.initVM()
from tika import parser

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

master_dict = {"sex_offender": ["Jeff Epstein", "Donald Trump"], "racists": ["Alfred Sloan", "Ted Cruz"],
               "fossil_fuels": ["David Koch", "Charles Koch"], "rich_assholes": ["Jeff Bezos", "Warren Buffet", "Giorgio Armani"],
               "war_criminals": ["Henry Kissinger", "Stephen A. Schwarzman"]}


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
   
    if ds_token_ok(3):
        account_id = session['ds_account_id']
        base_path = session['ds_base_path']
        access_token = session['ds_access_token']

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
            document_id='1', page_number='2', recipient_id='1', tab_label='SignHereTab',
            x_position='100', y_position='250')

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
        return redirect(results.url, code=302)
    else:
        session['eg'] = url_for('resign')
        return redirect(url_for('ds_login'))

def search(keywords):
    matched_documents = []
    raw_text = get_doc_text()
    for text in raw_text:
        for word in keywords:
            matches = [m.start() for m in re.finditer(word, text[1])]
            if matches is not None:
                matched_documents.append((word, matches))

    return matched_documents, raw_text[1]

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
    from_date = datetime.min.isoformat()
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
    from_date = datetime.min.isoformat()
    status_changes = env_api.list_status_changes(account_id, from_date=from_date)
    for env in status_changes.envelopes:
        combined = env_api.get_document(account_id, 'combined', env.envelope_id)
        parsed = parser.from_file(combined)
        to_ret.append((env.envelope_id ,parsed['content']))
        print(parsed['content'])

    return to_ret

# Mainline
app = Flask(__name__)

app.secret_key = ds_config.DS_CONFIG['session_secret']
@app.route('/', methods=['GET'])
def homepage():
    return render_template("home.html", search="", found_docs="")

@app.route('/resign', methods=['GET'])
def resign():
    return embedded_signing_ceremony() 


@app.route('/dsreturn', methods=['GET'])
def dsreturn():
    return '''
        <html lang="en"><body><p>The signing ceremony was completed with
          status {event}</p>
          <p>This page can also implement post-signing processing.</p></body>
    '''.format(event=request.args.get('event'))


@app.route('/search', methods=['GET'])
def keyword():
    keywords = request.args.get('keyword')
    print("searching for {}".format(keywords))
    found_keys = search(keywords.split(' '))

    if len(found_keys) == 0 or len(keywords)==0:
        return render_template("home.html", search=keywords, found_docs="")
    else:
        return render_template("home.html", search=keywords, found_docs="{}".format(found_keys[1][1]))

#######
#OAUTH#
######



base_uri_suffix = '/restapi'
oauth = OAuth(app)
request_token_params = {'scope': 'signature',
                        'state': lambda: uuid.uuid4().hex.upper()}
docusign = oauth.remote_app(
    'docusign',
    consumer_key=ds_config.DS_CONFIG['ds_client_id'],
    consumer_secret=ds_config.DS_CONFIG['ds_client_secret'],
    access_token_url=ds_config.DS_CONFIG['authorization_server'] + '/oauth/token',
    authorize_url=ds_config.DS_CONFIG['authorization_server'] + '/oauth/auth',
    request_token_params=request_token_params,
    base_url=None,
    request_token_url=None,
    access_token_method='POST'
)

def ds_token_ok(buffer_min=60):
    """
    :param buffer_min: buffer time needed in minutes
    :return: true iff the user has an access token that will be good for another buffer min
    """

    ok = 'ds_access_token' in session and 'ds_expiration' in session
    ok = ok and (session['ds_expiration'] - timedelta(minutes=buffer_min)) > datetime.utcnow()
    return ok


@app.route('/ds/login')
def ds_login():
    return docusign.authorize(callback=url_for('ds_callback', _external=True))


@app.route('/ds/logout')
def ds_logout():
    ds_logout_internal()
    flash('You have logged out from DocuSign.')
    return redirect(url_for('index'))


def ds_logout_internal():
    # remove the keys and their values from the session
    session.pop('ds_access_token', None)
    session.pop('ds_refresh_token', None)
    session.pop('ds_user_email', None)
    session.pop('ds_user_name', None)
    session.pop('ds_expiration', None)
    session.pop('ds_account_id', None)
    session.pop('ds_account_name', None)
    session.pop('ds_base_path', None)
    session.pop('envelope_id', None)
    session.pop('eg', None)
    session.pop('envelope_documents', None)
    session.pop('template_id', None)

@app.route('/ds/callback')
def ds_callback():
    """Called via a redirect from DocuSign authentication service """
    # Save the redirect eg if present
    redirect_url = session.pop('eg', None)
    # reset the session
    ds_logout_internal()

    resp = docusign.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    # app.logger.info('Authenticated with DocuSign.')
    flash('You have authenticated with DocuSign.')
    session['ds_access_token'] = resp['access_token']
    session['ds_refresh_token'] = resp['refresh_token']
    session['ds_expiration'] = datetime.utcnow() + timedelta(seconds=resp['expires_in'])

    # Determine user, account_id, base_url by calling OAuth::getUserInfo
    # See https://developers.docusign.com/esign-rest-api/guides/authentication/user-info-endpoints
    url = ds_config.DS_CONFIG['authorization_server'] + '/oauth/userinfo'
    auth = {"Authorization": "Bearer " + session['ds_access_token']}
    response = requests.get(url, headers=auth).json()
    session['ds_user_name'] = response["name"]
    session['ds_user_email'] = response["email"]
    accounts = response["accounts"]
    account = None # the account we want to use
    # Find the account...
    account = next((a for a in accounts if a["is_default"]), None)
    if not account:
        # Panic! Every user should always have a default account
        raise Exception("No default account")

    # Save the account information
    session['ds_account_id'] = account["account_id"]
    session['ds_account_name'] = account["account_name"]
    session['ds_base_path'] = account["base_uri"] + base_uri_suffix

    if not redirect_url:
        redirect_url = url_for('resign')
    return redirect(redirect_url)


#####
# @app.route('/checkall', methods=['GET', 'POST'])
# def checkall():
#     all_keys = search_all()
#     if len(all_keys) == 0:
#         return all_good_page
#     else:
#         return render_template("keyword.html", found_keys=str(all_keys))


app.run()
