"""
The views.
"""

from flask import redirect, url_for
from flask_login import login_required

from freelan_server.views.login import LoginView
from freelan_server.views.logout import LogoutView
from freelan_server.views.settings_overview import SettingsOverviewView
from freelan_server.views.settings import SettingsView
from freelan_server.views.settings_wizard import SettingsWizardView
from freelan_server.views.networks import NetworksView
from freelan_server.views.users import UsersView
from freelan_server.views.user import UserView

@login_required
def root():
    """
    The root page.
    """

    return redirect(url_for('networks'))

def setup_views(app):
    """
    Setup the views of the specified Flask application.
    """

    app.add_url_rule('/', view_func=root, endpoint='root')
    app.add_url_rule('/login', view_func=LoginView.as_view('login'))
    app.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
    app.add_url_rule('/settings_overview', view_func=SettingsOverviewView.as_view('settings_overview'))
    app.add_url_rule('/settings', view_func=SettingsView.as_view('settings'), methods=['GET', 'POST'])
    app.add_url_rule('/settings_wizard', view_func=SettingsWizardView.as_view('settings_wizard'), methods=['GET', 'POST'])
    app.add_url_rule('/networks', view_func=NetworksView.as_view('networks'))
    app.add_url_rule('/users', view_func=UsersView.as_view('users'))
    app.add_url_rule('/user/', view_func=UserView.as_view('user'), methods=['POST',])
    app.add_url_rule('/user/<int:user_id>', view_func=UserView.as_view('user'), methods=['GET', 'PUT', 'DELETE',])
