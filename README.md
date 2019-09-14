# DocuSign Quick Start examples for Python

Repository: [qs-python](https://github.com/docusign/qs-python)

These quick start examples provide straight-forward
code examples for quickly
trying the DocuSign eSignature API with the Python SDK.

The repo includes:

1. qs-01-python-embed-signing-ceremony

   Embedding a signing ceremony in your web application.
2. qs-02-python-send-envelope

   Sending a signing request via an email to the signer.
3. qs-03-python-list-envelopes

   Listing the envelopes in the user's account, including their status.

These examples do not include authentication. Instead,
use the DocuSign DevCenter's
[OAuth token generator](https://developers.docusign.com/oauth-token-generator)
to create an access token.

For a Python JWT authentication example, see the
[eg-01-python-jwt](https://github.com/docusign/eg-01-python-jwt)
repository. An OAuth Authorization Code Grant example is
also being developed.

For more information, see the
[DocuSign DevCenter Examples section](https://developers.docusign.com/esign-rest-api/code-examples).

## Installation

The examples were tested with Python v3.6.
The SDK itself works with Python v2.7 or later.

Download or clone this repository. Then:

````
cd qs-python
pip3 install docusign_esign pendulum flask
````

### Configure the example's settings
Each quick start example is a standalone file. You will configure
each of the example files:

 * **Access token:** Use the [OAuth Token Generator](https://developers.docusign.com/oauth-token-generator).
   To use the token generator, you'll need a
   [free DocuSign Developer's account.](https://go.docusign.com/o/sandbox/)

   Each access token lasts 8 hours, you will need to repeat this process
   when the token expires. You can use the same access token for
   multiple examples.

 * **Account Id:** After logging into the [DocuSign Sandbox system](https://demo.docusign.net),
   you can copy your Account Id from the dropdown menu by your name. See the figure:

   ![Figure](https://raw.githubusercontent.com/docusign/qs-python/master/documentation/account_id.png)
 * **Signer name and email:** Remember to try the DocuSign signing ceremony using both a mobile phone and a regular
   email client.

## Run the examples

The embedded signing example provides a small web app's server.
First, start the web app:
````
python3 qs-01-python-embed-signing-ceremony.py
````
Then open your browser to http://localhost:5000

Two of the examples are command line scripts:
````
python3 qs-02-python-send-envelope.py
python3 qs-03-python-list-envelopes.py
````

## Support, Contributions, License

Submit support questions to [StackOverflow](https://stackoverflow.com). Use tag `docusignapi`.

Contributions via Pull Requests are appreciated.
All contributions must use the MIT License.

This repository uses the MIT license, see the
[LICENSE](https://github.com/docusign/eg-01-Python-jwt/blob/master/LICENSE) file.
