# Landscaping Call-Bot
A minimal serverless system that places automated calls via SignalWire
and logs outcomes to Google Sheets while emailing a confirmation.

#1. Architecture Overview
Caller -> SignalWire/Twilio (HTTP POST)
 |
 v
Amazon API Gateway --> optional auth/throttle
 |
 v
AWS Lambda (call_initiator / status_logger)
 |
 +--+-------------------+
 | |
Google Sheets Amazon SES
(append row) (send email)

