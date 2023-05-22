import requests
import json
from datetime import datetime, timedelta


# GET TOKEN =============================================================================
# CREDENCIALES
CLIENT_ID = "084bf31e-5442-4a95-85a1-6b14be89d542"
CLIENT_SECRET = "XjL8Q~B7zVSeXPPY2RXBIhuoIhZP6NcfE4EDnaik"
TENANT_ID = "6ed69bdf-507b-4b02-bb08-3458b8f71b02"

# EMAIL O MAILS QUE SOLICITA SCOPES
#EMAIL_ADDRESSES = ["jonathan@uxlabsmx.onmicrosoft.com"]
EMAIL_ADDRESSES = ["jona_ram200@hotmail.com"]

# PREPARAR FUNCIÓN PARA OBTENCIÓN DE TOKEN
authority = f"https://login.microsoftonline.com/{TENANT_ID}"
token_url = f"{authority}/oauth2/v2.0/token"
scopes = [".default"]

# Nota* Conceder privilegios de scopes

params = {
  "client_id": CLIENT_ID,
  "client_secret": CLIENT_SECRET,
  "grant_type": "client_credentials",
  "scope": " ".join(scopes)
}

response = requests.post(token_url, data=params)
token_json = json.loads(response.content)
access_token = token_json["access_token"]
expires_in = token_json["expires_in"]
expiration_time = datetime.now() + timedelta(seconds=expires_in - 60)

print(access_token)
# END GET TOKEN =========================================================================


# ENVIROMENT FOR GET REQUEST =============================================================================

# FILTRAR FECHA DE CONSULTA
date = datetime.utcnow().date()
today_filter = f"receivedDateTime ge {date.isoformat()}"

# END POINT GRAPH API
graph_url = "https://graph.microsoft.com/v1.0/"

# LISTA DE MESES
months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


# ITERACIÓN DE MAILS QUE DESEAN LA INFORMACIÓN
for email in EMAIL_ADDRESSES:
    # Make the API call
    messages_url = f"{graph_url}users/{email}/messages?$filter={today_filter}"
    #messages_url = f"{graph_url}users/{email}/contacts"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(messages_url, headers=headers)
    print(response)

    # FRESPUESTA
    if response.status_code == 200:
        messages = json.loads(response.content)["value"]
        print(f"Found {len(messages)} emails for {email}")
    else:
        print(f"Failed to retrieve emails for {email}: {response.content}")

# END ENVIROMENT FOR GET REQUEST =========================================================================
  
