# -*- coding: utf-8 -*-
from requests import get as rget
from pprint import pprint
from M2Crypto import X509
from base64 import b64decode
from re import compile as regex_compile, IGNORECASE


def build_notification_string(msg):
    not_str = 'Message\n' + msg[u'Message'] + '\nMessageId\n' + \
              msg[u'MessageId']
    if u'Subject' in msg.keys():
        not_str = not_str + '\nSubject\n' + msg[u'Subject']
    not_str = not_str + '\nTimestamp\n' + msg[u'Timestamp'] + \
                        '\nTopicArn\n' + msg[u'TopicArn'] + '\nType\n' + \
                        msg[u'Type'] + '\n'
    return not_str


def build_subscription_string(msg):
    sub_str = 'Message\n' + msg[u'Message'] + '\nMessageId\n' + \
              msg[u'MessageId'] + '\nSubscribeURL\n' + msg[u'SubscribeURL'] + \
              '\nTimestamp\n' + msg[u'Timestamp'] + '\nToken\n' + \
              msg[u'Token'] + '\nTopicArn\n' + msg[u'TopicArn'] + \
              '\nType\n' + msg[u'Type'] + '\n'
    return sub_str


def is_message_signature_valid(msg):
    if msg[u'SignatureVersion'] != '1':
        raise Exception('Wrong signature version')

    signing_url = msg[u'SigningCertURL']
    prog = regex_compile(r'^https://sns\.[-a-z0-9]+\.amazonaws\.com/.*$', IGNORECASE)
    if not prog.match(signing_url):
        raise Exception("Cert is not hosted at AWS URL (https): %s",
                        signing_url)

    r = rget(signing_url)
    cert = X509.load_cert_string(str(r.text))
    str_to_sign = None
    if msg[u'Type'] == 'Notification':
        str_to_sign = build_notification_string(msg)
    elif any(msg[u'Type'] == s for s in ['SubscriptionConfirmation',
                                         'UnsubscribeConfirmation']):
        str_to_sign = build_subscription_string(msg)

    pubkey = cert.get_pubkey()
    pubkey.reset_context(md='sha1')
    pubkey.verify_init()
    pubkey.verify_update(str_to_sign.encode())
    result = pubkey.verify_final(b64decode(msg['Signature']))
    if result != 1:
        raise Exception('Notification could not be confirmed')
    else:
        return True
