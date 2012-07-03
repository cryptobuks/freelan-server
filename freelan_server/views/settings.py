"""
The settings view.
"""

from flask.views import MethodView

from flask import redirect, url_for, request, session, render_template
from flask_login import current_user, login_required
from freelan_server.database import DATABASE, Setting

import M2Crypto as m2

class SettingsView(MethodView):
    """
    The settings view.
    """

    decorators = [login_required]

    def get(self):
        """
        Get the settings page.
        """

        authority_certificate = Setting.get_value('authority_certificate')
        authority_private_key = Setting.get_value('authority_private_key')

        return render_template(
            'pages/settings.html',
            authority_certificate=authority_certificate,
            authority_private_key=authority_private_key,
        )

    def post(self):
        """
        Update the settings.
        """

        authority_certificate_error = None
        authority_certificate = request.values['authority_certificate'] or ''
        authority_private_key_error = None
        authority_private_key = request.values['authority_private_key'] or ''
        authority_private_key_passphrase = str(request.values['authority_private_key_passphrase'] or '')

        if authority_certificate:
            try:
                cert = m2.X509.load_cert_string(str(authority_certificate), m2.X509.FORMAT_PEM)

                if cert.check_ca():
                    authority_certificate = cert.as_pem()
                    Setting.set_value('authority_certificate', authority_certificate)
                else:
                    authority_certificate_error = 'The certificate must be a certificate authority (aka. self-signed).'
            except m2.X509.X509Error, ex:
                authority_certificate_error = 'Certificate error: %s' % ex
        else:
            Setting.set_value('authority_certificate', '')

        if authority_private_key:
            try:
                key = m2.RSA.load_key_string(str(authority_private_key), callback=(lambda v: authority_private_key_passphrase))
                authority_private_key = key.as_pem(cipher=None)
                Setting.set_value('authority_private_key', authority_private_key)
            except m2.RSA.RSAError, ex:
                authority_private_key_error = 'Private key error: %s' % ex
        else:
            Setting.set_value('authority_private_key', '')

        DATABASE.session.commit()

        if authority_certificate_error or authority_private_key_error:
            return render_template(
                'pages/settings.html',
                authority_certificate_error=authority_certificate_error,
                authority_certificate=authority_certificate,
                authority_private_key_error=authority_private_key_error,
                authority_private_key=authority_private_key,
            )

        else:
            return redirect(url_for('settings_overview'))
