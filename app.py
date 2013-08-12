# -*- coding: utf-8 -*-
from flask import Flask, request, json, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from twilio.rest import TwilioRestClient
from datetime import datetime as dt
import local_settings

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/test.db'
db = SQLAlchemy(app)
twilio_client = TwilioRestClient(local_settings.ACCOUNT_SID, local_settings.AUTH_TOKEN)


class Snstopic(db.Model):
    arn = db.Column(db.String(60), primary_key=True)
    status = db.Column(db.Integer)
    confirmation_url = db.Column(db.String(600))

    def __init__(self, arn, confirmation_url):
        self.arn = arn
        self.status = 0
        self.confirmation_url = confirmation_url

    def __repr__(self):
        return '<Arn %r>' % self.arn


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    telephone = db.Column(db.String(20))
    snstopic_arn = db.Column(db.String(60), db.ForeignKey('snstopic.arn'))
    snstopic = db.relationship('Snstopic', backref=db.backref('users', lazy='dynamic'))

    def __init__(self, email, telephone, snstopic):
        self.email = email
        self.telephone = telephone
        self.snstopic = snstopic

    def __repr__(self):
        return '<User %r>' % self.email


class Notification(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    timestamp = db.Column(db.DateTime())
    subject = db.Column(db.String(160))
    message = db.Column(db.String())
    snstopic_arn = db.Column(db.String(60), db.ForeignKey('snstopic.arn'))
    snstopic = db.relationship('Snstopic', backref=db.backref('notifications', lazy='dynamic'))


    def __init__(self, id, timestamp, subject, message, snstopic):
        self.id = id
        self.timestamp = timestamp
        self.subject = subject
        self.message = message
        self.snstopic = snstopic

    def __repr__(self):
        return '<Notification %r>' % self.id


@app.route('/')
def topics():
    return render_template('index.html', topics=Snstopic.query.all())


@app.route('/topic/<string:topic_arn>', methods=['GET', 'POST'])
def show_topic(topic_arn):
    topic = Snstopic.query.get(topic_arn)
    if request.method == 'POST':
        user = User(request.form.get('email'), request.form.get('telephone'), topic)
        db.session.add(user)
        db.session.commit()
    return render_template('topic.html', topic=topic)


@app.route('/sns', methods=['POST'])
def sns():
    if request.headers.get('x-amz-sns-message-type') == 'SubscriptionConfirmation':
        arn = request.headers.get('x-amz-sns-topic-arn')
        obj = json.loads(request.data)
        confirmation_url = obj[u'SubscribeURL']
        topic = Snstopic(arn, confirmation_url)
        db.session.add(topic)
        db.session.commit()
    elif request.headers.get('x-amz-sns-message-type') == 'Notification':
        arn = request.headers.get('x-amz-sns-topic-arn')
        topic = Snstopic.query.get(arn)
        obj = json.loads(request.data)

        notification_id = obj[u'MessageId']
        timestamp = dt.strptime(obj[u'Timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        subject = obj[u'Subject']
        message = obj[u'Message']
        notification = Notification(notification_id, timestamp, subject, message, topic)
        db.session.add(notification)
        db.session.commit()

        for user in topic.users:
            message = twilio_client.sms.messages.create(to=user.telephone,
                                                        from_=local_settings.FROM_NUMBER,
                                                        body=subject)
    return '', 200

if __name__ == '__main__':
    app.debug = True
    app.run()
