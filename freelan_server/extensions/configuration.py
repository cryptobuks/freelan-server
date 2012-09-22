"""
Configuration related information.
"""

import M2Crypto as m2

def register_configuration_information(app):
    """
    Register configuration information.
    """

    authority_certificate_file = app.config['AUTHORITY_CERTIFICATE_FILE']
    authority_private_key_file = app.config['AUTHORITY_PRIVATE_KEY_FILE']
    authority_private_key_passphrase = app.config['AUTHORITY_PRIVATE_KEY_PASSPHRASE'] or ''

    try:
        authority_certificate = m2.X509.load_cert_string(
            open(authority_certificate_file, 'r').read(),
            m2.X509.FORMAT_PEM
        )
        authority_certificate_error = None

    except (IOError, m2.X509.X509Error) as ex:
        authority_certificate = None
        authority_certificate_error = str(ex)

    try:
        authority_private_key = m2.RSA.load_key_string(
            open(authority_private_key_file, 'r').read(),
            callback=(lambda v: authority_private_key_passphrase or '')
        )
        authority_private_key_error = None

    except (IOError, m2.RSA.RSAError) as ex:
        authority_private_key = None
        authority_private_key_error = str(ex)

    app.config['AUTHORITY_CERTIFICATE'] = authority_certificate
    app.config['AUTHORITY_CERTIFICATE_ERROR'] = authority_certificate_error
    app.config['AUTHORITY_PRIVATE_KEY'] = authority_private_key
    app.config['AUTHORITY_PRIVATE_KEY_ERROR'] = authority_private_key_error
