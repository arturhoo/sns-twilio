# sns-twilio

A gateway between AWS' SNS and Twilio. Since SNS only sends SMSes to the US, this Flask app exposes an HTTP endpoint for SNS, and then forwards the messages as SMSes worldwide thanks to Twilio.

There is a basic web interface for admin tasks.

## Setup

General system requirements: `build-essential`, `swig`.

The python requirements are specified in `requirements.txt`. **Special attetion must be paid to M2Crypto**, as it should be manually built on Ubuntu 12.04, [there is a script that can be used](https://github.com/arturhoo/sns-twilio/wiki/M2Crypto-on-Ubuntu-12.04).

There should be a `tmp` folder (the SQLite3 DB will sit there) and a `local_settings.py` file. Here is how it should be populated:

```python
# Twilio settings
ACCOUNT_SID = "d41d8cd98f00b204e9800998ecf8427e"
AUTH_TOKEN = "df5ea29924d39c3be8785734f13169c6"
FROM_NUMBER = "+1415556789"

# Flask settings
FLASK_SECRET_KEY = "2095497fef8978477de913f147446421"
SNS_ENDPOINT = "b113256183c5983c9989d8ff86cf62b4"
PRE_SUBJECT = ""
```

## Thanks

- Flask
- SQL Alchemy

## License

MIT
