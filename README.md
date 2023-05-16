# facturas-rs-lp

1. Importamos todas las liberías necesarias
``` python
import requests
import json
from datetime import datetime, timedelta
import hashlib
import os.path
from pathlib import Path
import pysftp
```
2. Importamos las variables secretas de autenticación
``` python
CLIENT_ID = "**************************"
CLIENT_SECRET = "*****************************"
TENANT_ID = "************************************"
```
3. Ponemos la lista de emails para obtener las facturas
``` python
EMAIL_ADDRESSES = ["correo@realst.mx", "correo2@realst.mx"]
```
4. Declaramos los links y permisos adecuados
``` python
authority = f"https://login.microsoftonline.com/{TENANT_ID}"
token_url = f"{authority}/oauth2/v2.0/token"
scopes = ["https://graph.microsoft.com/.default"]
```
5. Ajustamos los parametros para solicitar el token de acceso
``` python
params = {
  "client_id": CLIENT_ID,
  "client_secret": CLIENT_SECRET,
  "grant_type": "client_credentials",
  "scope": " ".join(scopes)
}
```
6. Obtenemos el token de acceso para solicitar información de las cuentas
``` python
response = requests.post(token_url, data=params)
token_json = json.loads(response.content)
access_token = token_json["access_token"]
print(access_token)
```
7. Filtramos los correos electrónicos al día de hoy
 ``` python
date = datetime.utcnow().date()
today_filter = f"receivedDateTime ge {date.isoformat()}"
```
8. Creamos una lista con los nombres de cada mes
``` python
months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
```
9. Realizamos una petición get para obtener los correos electrónicos
``` python
graph_url = "https://graph.microsoft.com/v1.0/"

for email in EMAIL_ADDRESSES:
  messages_url = f"{graph_url}users/{email}/messages?$filter={today_filter}"
  headers = {"Authorization": f"Bearer {access_token}"}
  response = requests.get(messages_url, headers=headers)
```
10. Si hubo exito, guardamos los correos electrónicos en una variable
``` python
  if response.status_code == 200:
      messages = json.loads(response.content)["value"]
      print(f"Found {len(messages)} emails for {email}")
  else:
      print(f"Failed to retrieve emails for {email}: {response.content}")
```
11. Iteramos en la lista de correos electrónicos obtenidos para analizar los archivos adjuntos
``` python
  # ITERACION DE LISTA
  for message in messages:
      subject = message.Subject
      body = message.Body
      attachments = message.Attachments

      # ENCRIPTACION DE ID MAIL
      mail_id = hashlib.md5(message.EntryID.encode())

      # CREAR UN DIRECTIORIO PARA CADA ARCHIVO VALIDANDO SU EXISTENCIA
      target_folder = str(date.strftime('%Y')) + '/' + months[int(date.strftime("%m"))-1] + '/' + 'Semana ' + date.isocalendar().week + '/' + 'nombre_operador'
      target_folder.mkdir(parents=True, exist_ok=True)

      # CONECTAR CON SFTP Y SUBIR ARCHIVO
      cnopts = pysftp.CnOpts()
      cnopts.hostkeys = None

      # ITERAR EN LOS ARCHIVOS ADJUNTOS DEL MAIL
      for attachment in attachments:
          # SE VALIDA QUE SOLO ENTREN ARCHIVOS DE TIPO PDF Y XML
          if ".pdf" in str(attachment) or ".xml" in str(attachment):
          
            # CON OS, VERIFICAMOS QUE EL ARCHIVO NO EXISTA PARA PODER CREARLO
            if not os.path.isfile(str(target_folder) + '/' + str(attachment)):

              # SI EL NOMBRE DEL ARCHIVO CONTIENE RS50000 SUBIRLO A UN HOST POR SFTP
              if "RS50000" in str(attachment):

                # SE GUARDA EL ARCHIVO CON DIRECTORIO PERSONALIZADO
                attachment.SaveAsFile(target_folder + '/' + str(attachment))

                # SE ESTABLECE UNA CONEXIÓN SFTP 
                with pysftp.Connection(host='host.com', username='mail/username', password='pass', cnopts = cnopts, port=22) as sftp:
                        print("Conexión establecida ... ")
                        sftp.makedirs(target_folder)
                        sftp.chdir(target_folder)
                        sftp.put(target_folder+'/archivo.pdf', 'archivo.pdf', preserve_mtime=True)
                        print("Archivo cargado ")

                        # CERRAR CONEXIÓN SFTP
                        sftp.close()

                # BORRAR ARCHIVO DEL DISCO LOCAL
                os.rmdir(str(target_folder)+'/'+str(attachment))

              # SI EL NOMBRE DEL ARCHIVO CONTIENE LP500 SUBIRLO A UN HOST DISTINTO POR SFTP
              if "LP500" in str(attachment):

                # SE GUARDA EL ARCHIVO CON DIRECTORIO PERSONALIZADO
                attachment.SaveAsFile(target_folder + '/' + str(attachment))

                # SE ESTABLECE UNA CONEXIÓN SFTP 
                with pysftp.Connection(host='other-host.com', username='mail/username', password='pass', cnopts = cnopts, port=22) as sftp:
                        print("Conexión establecida ... ")
                        sftp.makedirs(target_folder)
                        sftp.chdir(target_folder)
                        sftp.put(target_folder+'/archivo.pdf', 'archivo.pdf', preserve_mtime=True)
                        print("Upload file ")

                        # CERRAR CONEXIÓN SFTP
                        sftp.close()

                # BORRAR ARCHIVO DEL DISCO LOCAL
                os.rmdir(str(target_folder)+'/'+str(attachment))
```
