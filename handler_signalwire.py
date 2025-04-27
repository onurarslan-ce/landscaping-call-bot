# handler_signalwire.py
import os
import json
from datetime import datetime
from signalwire.rest import Client          # ← only change vs Twilio
from googleapiclient.discovery import build
from google.oauth2 import service_account


def lambda_handler(event, context):
    # --- env vars ---
    project_id  = os.environ['SIGNALWIRE_PROJECT_ID']
    api_token   = os.environ['SIGNALWIRE_API_TOKEN']
    space_url   = os.environ['SIGNALWIRE_SPACE_URL']
    from_number = os.environ['SIGNALWIRE_NUMBER']
    to_number   = os.environ['TO_NUMBER']
    sheet_id    = os.environ['SHEET_ID']

    # --- call flow ---
    client = Client(project_id, api_token, signalwire_space_url=space_url)

    audio_url = os.environ['AUDIO_0']  # rotate later if you like
    call = client.calls.create(
        from_=from_number,
        to=to_number,
        twiml=f'<Response><Play>{audio_url}</Play></Response>'
    )

    # --- log SID to Google Sheets ---
    timestamp = datetime.utcnow().isoformat()
    creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    log_to_google_sheets(sheet_id, [timestamp, call.sid], creds_json)

    return {'statusCode': 200, 'body': json.dumps('Call successfully made')}


def log_to_google_sheets(sheet_id, values, creds_json):
    creds = service_account.Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    sheet.values().append(
        spreadsheetId=sheet_id,
        range="Sheet1!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [values]}
    ).execute()
