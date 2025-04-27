print("=== lambda_function.py loaded ===")

import os
import json
from datetime import datetime
from twilio.rest import Client
from googleapiclient.discovery import build
from google.oauth2 import service_account

def log_to_google_sheets(sheet_id, values, creds_json):
    creds = service_account.Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    request = sheet.values().append(
        spreadsheetId=sheet_id,
        range="landscape_calls!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [values]}
    )
    request.execute()

def lambda_handler(event=None, context=None):
    print("Script started")

    try:
        # Twilio setup
        account_sid = os.environ['TWILIO_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        twilio_number = os.environ['TWILIO_NUMBER']
        target_number = os.environ['TO_NUMBER']
        sheet_id = os.environ['SHEET_ID']

        # Load Google credentials from local file
        with open("creds.json", "r") as f:
            creds_json = json.load(f)

        # Simulate SSM-style message rotation using a local file
        index_file = "message_index.txt"
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                index = (int(f.read().strip()) + 1) % 4
        else:
            index = 0
        with open(index_file, "w") as f:
            f.write(str(index))

        audio_urls = [
            os.environ['AUDIO_0'],
            os.environ['AUDIO_1'],
            os.environ['AUDIO_2'],
            os.environ['AUDIO_3']
        ]

        selected_audio = audio_urls[index]

        print(f"Simulating call to {target_number} using message #{index+1}: {selected_audio}")

        # Simulated call object (replace with real call later)
        class FakeCall:
            sid = f"SIMULATED-CALL-SID-{index+1}"

        call = FakeCall()

        timestamp = datetime.utcnow().isoformat()
        print(f"Call SID: {call.sid}")

        log_to_google_sheets(sheet_id, [timestamp, f"Message {index+1}", call.sid], creds_json)

        print("Script completed successfully.")
        return {'statusCode': 200, 'body': f"Call placed with message {index+1}."}

    except Exception as e:
        print("An error occurred:")
        print(str(e))
        return {'statusCode': 500, 'body': str(e)}

if __name__ == "__main__":
    lambda_handler()
