## 0.1.4 (unreleased)

FEATURES:

* general: admin login across the whole web application


## 0.1.3 (August 15, 2013)

IMPROVEMENTS:

* sns: ensure signing cert url is from (https) amazonaws.com


## 0.1.2 (August 14, 2013)

FEATURES:

* general: users can be deleted
* general: subscriptions, once canceled, can be deleted
* general: unsubscribe
* general: a custom favicon

IMPROVEMENTS

* general: misconception between topic and subscription addressed
* general: sqlite database now lives on the `db` dir
* models: snstopics is are now subscriptions with proper attributes
* models: user's email is now a generic name
* models: subscriptions now have a subscription date
* controllers: validates that all user's attributes are not empty
* views: subscriptions page is presented as a table with more information


## 0.1.1 (August 13, 2013)

FEATURES:

* controllers: message authenticity is checked. M2Crypto is used to verify the message signature, using the pubkey extracted from the X509 certificate

IMPROVEMENTS:

* views: wrap word in message body

BUG FIXES:

* controllers: notifications without subject are correctly handled


## 0.1.0 (August 13, 2013)

* Initial release
