# lambda_function_index_file =signalwire.py
print("=== lambda_function_signalwire.py loaded ===")

import os, json, datetime
from signalwire.rest import Client                       # ← switched SDK
from googleapiclient.discovery import build
from google.oauth2 import service_account
TMP_DIR = "/tmp"  

def log_to_google_sheets(sheet_id, values, creds_json):
    creds = service_account.Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build('sheets', 'v4', credentials=creds)
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="landscape_calls!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [values]}
    ).execute()


def lambda_handler(event=None, context=None):
    print("Script started")
    try:
        # ----- env -----
        project_id  = os.environ['SIGNALWIRE_PROJECT_ID']
        api_token   = os.environ['SIGNALWIRE_API_TOKEN']
        space_url   = os.environ['SIGNALWIRE_SPACE_URL']
        from_number = os.environ['SIGNALWIRE_NUMBER']
        to_number   = os.environ['TO_NUMBER']
        sheet_id    = os.environ['SHEET_ID']

        # Google creds (local file for dev, env var for Lambda)
        if os.path.exists("creds.json"):
            with open("creds.json") as f:
                creds_json = json.load(f)
        else:
            creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])

        # ----- rotate message index -----
        index_file = f"{TMP_DIR}/message_index.txt"
        if os.path.exists(index_file):
            with open(index_file) as f:
                index = (int(f.read().strip()) + 1) % 4
        else:
            index = 0
        with open(index_file, "w") as f:
            f.write(str(index))

        audio_urls = [os.environ[f'AUDIO_{i}'] for i in range(4)]
        audio_url  = audio_urls[index]
        print(f"Calling {to_number} with message #{index+1}")

        # ----- place the real call -----
        client = Client(project_id, api_token, signalwire_space_url=space_url)
        call = client.calls.create(
            from_=from_number,
            to=to_number,
            twiml=f'<Response><Play>{audio_url}</Play></Response>'
        )

        # ----- log -----
        timestamp = datetime.datetime.utcnow().isoformat()
        log_to_google_sheets(
            sheet_id, [timestamp, f"Message {index+1}", call.sid], creds_json
        )
        print("Completed ok:", call.sid)
        return {'statusCode': 200, 'body': f"Call SID {call.sid}"}

    except Exception as e:
        print("ERROR:", e)
        return {'statusCode': 500, 'body': str(e)}


if __name__ == "__main__":
    lambda_handler()

