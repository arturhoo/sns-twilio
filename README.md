# sns-twilio

A gateway between AWS' SNS and Twilio. Since SNS only sends SMSes to the US, this Flask app exposes an HTTP endpoint for SNS, and then forwards the messages as SMSes worldwide thanks to Twilio.

There is a basic web interface for admin tasks.

<p align="center">
  <img src="https://raw.github.com/arturhoo/sns-twilio/gh-pages/imgs/sns-twilio.png" alt="Sample screenshot"/>
</p>

## Setup

General system requirements: `build-essential`, `swig`.

The python requirements are specified in `requirements.txt`. **Special attetion must be paid to M2Crypto**, as it should be manually built on Ubuntu 12.04, [there is a script that can be used](https://github.com/arturhoo/sns-twilio/wiki/M2Crypto-on-Ubuntu-12.04).

A `local_settings.py` file must exist. Here is how it should be populated:

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

## Deploying

We are running SNS-Twilio in production using:

- OS: Ubuntu Server 12.04
- Static server and reverse proxy: Nginx
- App server: uWSGI
- Monitoring: Supervisor

Here are the relevant configuration files:

> `/etc/nginx/sites-available/sns-twilio`

```
server {
        listen PORT;
        server_name SERVER_NAME;

        location / { try_files $uri @yourapplication; }

        location @yourapplication {
                include uwsgi_params;
                uwsgi_pass unix:/tmp/sns-twilio.sock;
        }

        location /static {
                alias /PATH/TO/SNS-TWILIO/static/;
                autoindex off;
        }

        location /favicon.ico {
                alias /PATH/TO/SNS-TWILIO/static/favicon.ico;
        }

}
```

> `sns-twilio.ini`

```
[uwsgi]
socket = /tmp/%n.sock
module = app:app
processes = 1
master = 1
logto = /var/log/uwsgi/%n.log
virtualenv = /PATH/TO/VIRTUALENV
chmod-socket = 777
```

> `/etc/supervisor/conf.d/sns-twilio.conf`

```
[program:sns-twilio]
command=/PATH/TO/VIRTUALENV/bin/uwsgi --ini sns-twilio.ini
directory=/PATH/TO/SNS-TWILIO/sns-twilio
user=USER
stdout_logfile=/var/log/supervisor/sns-twilio-out.log
stderr_logfile=/var/log/supervisor/sns-twilio-err.log
autostart=true
```

## Thanks

- Flask
- SQL Alchemy
- M2Crypto

## License

MIT
