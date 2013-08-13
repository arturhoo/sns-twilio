# -*- coding: utf-8 -*-
from flask import Flask, request, json, render_template, redirect, url_for, \
    flash
from flask.ext.sqlalchemy import SQLAlchemy
from twilio.rest import TwilioRestClient
from requests import get as rget
from datetime import datetime as dt
from sns import is_message_signature_valid
import local_settings

app = Flask(__name__)
app.secret_key = local_settings.FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
db = SQLAlchemy(app)
twilio_client = TwilioRestClient(local_settings.ACCOUNT_SID,
                                 local_settings.AUTH_TOKEN)


class Subscription(db.Model):
    arn = db.Column(db.String(60), primary_key=True)
    status = db.Column(db.Integer)
    subscribe_url = db.Column(db.String(600))
    unsubscribe_url = db.Column(db.String(600))

    def __init__(self, arn, subscribe_url):
        self.arn = arn
        self.status = 0
        self.subscribe_url = subscribe_url
        self.unsubscribe_url = None

    def __repr__(self):
        return '<Arn %r>' % self.arn


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    telephone = db.Column(db.String(20))
    subscription_arn = db.Column(db.String(60),
                                 db.ForeignKey('subscription.arn'))
    subscription = db.relationship('Subscription',
                                   backref=db.backref('users', lazy='dynamic'))

    def __init__(self, email, telephone, subscription):
        self.email = email
        self.telephone = telephone
        self.subscription = subscription

    def __repr__(self):
        return '<User %r>' % self.email


class Notification(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    timestamp = db.Column(db.DateTime())
    subject = db.Column(db.String(160))
    message = db.Column(db.String())
    subscription_arn = db.Column(db.String(60),
                                 db.ForeignKey('subscription.arn'))
    subscription = db.relationship('Subscription',
                                   backref=db.backref('notifications',
                                                      lazy='dynamic'))

    def __init__(self, id, timestamp, subject, message, subscription):
        self.id = id
        self.timestamp = timestamp
        self.subject = subject
        self.message = message
        self.subscription = subscription

    def __repr__(self):
        return '<Notification %r>' % self.id


@app.route('/')
def subscriptions():
    return render_template('index.html',
                           subscriptions=Subscription.query.all())


@app.route('/subscription/<string:subscription_arn>', methods=['GET', 'POST'])
def show_subscription(subscription_arn):
    subscription = Subscription.query.get(subscription_arn)
    if request.method == 'POST':
        user = User(request.form.get('email'), request.form.get('telephone'),
                    subscription)
        db.session.add(user)
        db.session.commit()
        flash(u'User added!', 'success')
    return render_template('subscription.html', subscription=subscription)


@app.route('/subscription/<string:subscription_arn>/subscribe',
           methods=['GET'])
def subscribe(subscription_arn):
    subscription = Subscription.query.get(subscription_arn)
    if subscription.status == 0:
        r = rget(subscription.subscribe_url)
        if r.status_code == 200:
            subscription.status = 1
            db.session.commit()
            flash(u'Subscription confirmed!', 'success')
        else:
            flash(u'Subscription not confirmed! Response code was %i' %
                  r.status_code, 'danger')
    else:
        flash(u'Subscription already confirmed!', 'danger')
    return redirect(url_for('show_subscription',
                    subscription_arn=subscription.arn))


@app.route('/subscription/<string:subscription_arn>/unsubscribe',
           methods=['GET'])
def unsubscribe(subscription_arn):
    subscription = Subscription.query.get(subscription_arn)
    if not subscription.unsubscribe_url:
        flash(u'A message must be received to unsubscribe', 'danger')
    elif subscription.status == 1:
        r = rget(subscription.unsubscribe_url)
        if r.status_code == 200:
            subscription.status = 2
            db.session.commit()
            flash(u'Ubsubscription request sent!', 'success')
        else:
            flash((u'Unsubscription request unsuccessful!',
                   u' Response code was %i' % r.status_code), 'danger')
    else:
        flash(u'Subscription is not valid to be unsubscribed!', 'danger')
    return redirect(url_for('show_subscription',
                    subscription_arn=subscription.arn))


@app.route('/%s' % local_settings.SNS_ENDPOINT, methods=['POST'])
def sns():
    headers = request.headers
    arn = headers.get('x-amz-sns-subscription-arn')
    obj = json.loads(request.data)
    if app.debug != True:
        assert is_message_signature_valid(obj)

    if headers.get('x-amz-sns-message-type') == 'SubscriptionConfirmation':
        subscribe_url = obj[u'SubscribeURL']
        subscription = Subscription(arn, subscribe_url)
        db.session.add(subscription)
        db.session.commit()

    elif headers.get('x-amz-sns-message-type') == 'UnsubscribeConfirmation':
        subscription = Subscription.query.get(arn)
        subscription.status = 3
        db.session.commit()

    elif headers.get('x-amz-sns-message-type') == 'Notification':
        subscription = Subscription.query.get(arn)
        notification_id = obj[u'MessageId']
        timestamp = dt.strptime(obj[u'Timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        message = obj[u'Message']

        unsubscribe_url = obj[u'UnsubscribeURL']
        subscription.unsubscribe_url = unsubscribe_url

        msg_subject = obj[u'Subject'] if u'Subject' in obj.keys() else 'empty'
        subject = local_settings.PRE_SUBJECT + msg_subject

        notification = Notification(notification_id, timestamp, subject,
                                    message, subscription)
        db.session.add(notification)
        db.session.commit()

        for user in subscription.users:
            create_sms = twilio_client.sms.messages.create
            message = creae_sms(to=user.telephone,
                                from_=local_settings.FROM_NUMBER, body=subject)
    return '', 200

if __name__ == '__main__':
    app.debug = True
    app.run()
