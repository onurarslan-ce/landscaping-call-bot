import os
import json
from twilio.rest import Client
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

def lambda_handler(event, context):
    # Load environment variables
    account_sid = os.environ['TWILIO_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    twilio_number = os.environ['TWILIO_NUMBER']
    target_number = os.environ['TO_NUMBER']
    sheet_id = os.environ['SHEET_ID']
    to_notify = os.environ['TO_SMS'].split(',')

    # Twilio Client Setup
    client = Client(account_sid, auth_token)

    # Choose MP3 URL
    audio_url = os.environ['AUDIO_0']

    # Make the call
    call = client.calls.create(
        to=target_number,
        from_=twilio_number,
        twiml=f'<Response><Play>{audio_url}</Play></Response>'
    )

    # Log to Google Sheets (Google API Integration here)
    timestamp = datetime.utcnow().isoformat()
    creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    log_to_google_sheets(sheet_id, [timestamp, call.sid], creds_json)

    return {
        'statusCode': 200,
        'body': json.dumps('Call successfully made')
    }

def log_to_google_sheets(sheet_id, values, creds_json):
    creds = service_account.Credentials.from_service_account_info(creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    request = sheet.values().append(
        spreadsheetId=sheet_id,
        range="Sheet1!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [values]}
    )
    request.execute()


