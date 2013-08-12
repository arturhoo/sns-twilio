# sns-twilio

A gateway between AWS' SNS and Twilio. Since SNS only sends SMSes to the US, this Flask app exposes an HTTP endpoint for SNS, and then forwards the messages as SMSes worldwide thanks to Twilio.

There is a basic web interface for admin tasks.

## Setup

There should be a `tmp` folder (the SQLite3 DB will sit there) and a `local_settings.py` file. Here is how it should be populated:

```python
ACCOUNT_SID = "d41d8cd98f00b204e9800998ecf8427e"
AUTH_TOKEN = "df5ea29924d39c3be8785734f13169c6"
FROM_NUMBER = "+1415556789"

```

## Thanks

- Flask
- SQL Alchemy

## License

MIT
