import os

from bitbucket.conf import settings


def pytest_configure():
    d = dict(
        # DEFAULT_BITBUCKET_SERVICE_LOCATION='https://git.kpn.org/',
        # KATKA_SERVICE_LOCATION='https://katka-api-acceptance.tools.tcloud.kpn.org/',
        # CREDENTIALS_ACCESS_TOKEN_KEY='token',
        DEFAULT_BITBUCKET_SERVICE_LOCATION='https://bitbucket.org/',
        KATKA_SERVICE_LOCATION='http://katka.com/',
        CREDENTIALS_ACCESS_TOKEN_KEY='token',
    )

    settings.configure(**d)

    REQUESTS_CA_BUNDLE = '/usr/local/lib/python3.7/site-packages/certifi/cacert.pem'
    os.environ['REQUESTS_CA_BUNDLE'] = REQUESTS_CA_BUNDLE

    import requests
    try:
        test = requests.get('https://git.kpn.org', verify=REQUESTS_CA_BUNDLE)
    except requests.exceptions.SSLError as err:
        try:
            with open('/Users/claudiacardoso/Desktop/kpn.pem', 'rb') as infile:
                customca = infile.read()
            with open(REQUESTS_CA_BUNDLE, 'ab') as outfile:
                outfile.write(customca)
        except:
            print('A error occurred configuring certificates')
