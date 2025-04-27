import os, json, base64, boto3
from datetime import datetime
from urllib.parse import parse_qs
from google.oauth2 import service_account
import google_auth_httplib2
from googleapiclient.discovery import build

SES_REGION        = os.environ['SES_REGION']
SES_FROM          = os.environ['SES_FROM']
SES_TO            = os.environ['SES_TO'].split(',')
SHEET_ID          = os.environ['SHEET_ID']
GOOGLE_CREDS_JSON = os.environ['GOOGLE_CREDENTIALS']

ses = boto3.client('ses', region_name=SES_REGION)

def parse_body(event):
    raw = event.get('body') or ''
    if event.get('isBase64Encoded'):
        raw = base64.b64decode(raw).decode('utf-8')
    ctype = event.get('headers',{}).get('content-type','')
    if 'application/json' in ctype:
        try:
            return json.loads(raw)
        except:
            print("‼ invalid JSON:", raw)
            return {}
    qs = parse_qs(raw, keep_blank_values=True)
    return {k:v[0] for k,v in qs.items()}

def log_to_google_sheets(sheet_id, values, creds_json):
    creds = service_account.Credentials.from_service_account_info(
        creds_json, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    authed_http = google_auth_httplib2.AuthorizedHttp(creds)
    service = build('sheets', 'v4', http=authed_http)
    service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="landscape_calls!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [values]}
    ).execute()

def send_email(params):
    subject = f"Call {params.get('CallSid')} completed"
    body = (
        f"Call SID: {params.get('CallSid')}\n"
        f"Status:   {params.get('CallStatus')}\n"
        f"Answered: {params.get('AnsweredBy')}\n"
        f"Duration: {params.get('Duration')}"
    )
    ses.send_email(
        Source=SES_FROM,
        Destination={'ToAddresses': SES_TO},
        Message={'Subject': {'Data': subject},
                 'Body':    {'Text': {'Data': body}}}
    )

def lambda_handler(event, context=None):
    params = parse_body(event)
    now = datetime.utcnow()
    row = [
        now.strftime('%Y-%m-%d'),
        now.strftime('%H:%M:%S'),
        params.get('CallSid'),
        params.get('CallStatus'),
        params.get('AnsweredBy'),
        params.get('Duration')
    ]
    creds_json = json.loads(GOOGLE_CREDS_JSON)
    log_to_google_sheets(SHEET_ID, row, creds_json)
    send_email(params)
    return {'statusCode': 200, 'body': json.dumps({'message':'OK'})}
