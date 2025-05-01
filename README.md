# Landscaping Call-Bot

_A minimal serverless system that places automated calls via SignalWire and logs outcomes to Google Sheets while emailing a confirmation._

**GitHub repository:** [https://github.com/onurarslan-ce/landscaping-call-bot](https://github.com/onurarslan-ce/landscaping-call-bot)  
**Author:** Onur Arslan  

---

## 1. Architecture Overview
![image](https://github.com/user-attachments/assets/0092f733-f8a6-4ab7-b905-c072557b1445)


<pre>
          +-----------------+
          |     Caller      |
          +-----------------+
                  |
                  v
   +--------------------------------------+
   | SignalWire/Twilio (HTTP POST)        |
   +--------------------------------------+
                  |
                  v
   +--------------------------------------+
   | Amazon API Gateway                   |
   | (auth/throttle optional)             |
   +--------------------------------------+
                  |
                  v
   +--------------------------------------+
   | AWS Lambda                           |
   | (call_initiator/status_logger)       |
   +--------------------------------------+
                  |
         -------------------------
         |                       |
         v                       v
+---------------------+   +---------------------+
|   Google Sheets     |   |     Amazon SES      |
|    (append row)     |   |    (send email)     |
+---------------------+   +---------------------+
</pre>


## 2. Prerequisites & .env Config

- **AWS:** Lambda, API Gateway, SES (sandbox OK).
- **Google Cloud:** Service account JSON with Sheets API.
- **SignalWire:** Project ID, API token, space URL, phone number.
- **Local tools:** Python 3.8+, AWS CLI v2, Git.

### .env Example
<pre>
SIGNALWIRE_PROJECT_ID=...
SIGNALWIRE_API_TOKEN=...
SIGNALWIRE_SPACE_URL=example.signalwire.com
SIGNALWIRE_NUMBER=+1xxxxxxxxxx
TO_NUMBER=+1xxxxxxxxxx
AUDIO_0=https://.../msg0.mp3
AUDIO_1=https://.../msg1.mp3
AUDIO_2=https://.../msg2.mp3
AUDIO_3=https://.../msg3.mp3
SHEET_ID=...
GOOGLE_CREDENTIALS={...}
SES_REGION=us-east-1
SES_FROM=you@example.com
SES_TO=you@example.com,partner@example.com
</pre>


---

## 3. Setup & Deployment

### Local Run

```bash
git clone <repo> && cd landscaping-call-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit secrets
python -m dotenv run -- python src/call_initiator.py
```
### Package for Lambda
```bash
mkdir build && pip install -r requirements.txt -t build/
cp -r src build/
(cd build && zip -qr ../package.zip .)
```
### Deploy
```bash
aws lambda update-function-code --function-name CALL_INITIATOR \
  --zip-file fileb://package.zip --region us-east-1

aws lambda update-function-configuration --function-name CALL_INITIATOR \
  --handler src/call_initiator.lambda_handler --region us-east-1
```
## 4.Testing & Troubleshooting
### Test Locally
```bash
python -m dotenv run -- python src/call_initiator.py
```
### Simulate Webhook
```bash
curl -X POST "CALLBACK_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "CallSid=TEST&CallStatus=completed"
```
### Verify
- Google Sheets row appended.
- SES email arrives.
- CloudWatch shows INFO logs.

### Common Issues
- Runtime.ImportModuleError: Missing dependency in package.
- 403 from Sheets API: Share your sheet with the service account.
- Email in spam: Move out of the SES sandbox or add SPF/DKIM.

### Repository Structure
<pre>
.
├── src/
│   ├── call_initiator.py   # SignalWire caller
│   └── status_logger.py    # Sheets + SES webhook
├── requirements.txt
├── .gitignore
└── README.md
</pre>
