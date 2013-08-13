## 0.1.1 (August 13, 2013)

FEATURES:

* controllers: message authenticity is checked. M2Crypto is used to verify the message signature, using the pubkey extracted from the X509 certificate

IMPROVEMENTS:

* views: wrap word in message body

BUG FIXES:

* controllers: notifications without subject are correctly handled

## 0.1.0 (August 13, 2013)

* Initial release
