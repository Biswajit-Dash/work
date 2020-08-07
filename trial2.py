#!/Users/bdash/Documents/Ubereats/googledrive/bin/python

from __future__ import print_function
import time
from time import sleep
from googleapiclient.discovery import build
from apiclient.http import MediaFileUpload
from google.oauth2 import service_account
from googleapiclient import errors
import json
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

def upload_n_times(n, google_drive_service):
    print("upload {} times".format(str(n)))
    uploaded_file_ids = []
    for i in range(n):
        print("upload #{}".format(str(i + 1)))
        name = "sample_{}.csv".format(str(i + 1))
        file_metadata = {'name': name, 'parents': ['1h-9FG-6m3kXH54cIFor6ul78hzvxlfyW']}
        media = MediaFileUpload('sample.csv', mimetype='text/csv', resumable=True)
        t1 = time.time()
        retry, sleep_sec = 1, 2
        file = None
        while file is None and retry <= 5:
            try:
                file = google_drive_service.files().create(body=file_metadata,
                                                           media_body=media,
                                                           fields='id').execute()
            except errors.Error as e:
                j = json.loads(e.content)
                print("Unexpected error: {}".format(j))
            if file is None:
                print("will retry after {} sec".format(str(sleep_sec)))
                sleep(sleep_sec)
                sleep_sec *= 2
                retry += 1
            else:
                break
        t2 = time.time()
        print("done {} in {}".format(file, str(t2 - t1)))
        uploaded_file_ids.append(file['id'])
    return uploaded_file_ids


SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
    creds = tools.run_flow(flow, store)
DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))

files = DRIVE.files().list().execute().get('files', [])
for f in files:
    print(f['name'], f['mimeType'])

uploaded = upload_n_times(20, DRIVE)
print(uploaded)
