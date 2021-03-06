"""
The user view.
"""

import re

from flask.views import MethodView

from flask import redirect, url_for, request, session, render_template, abort
from flask_login import current_user, login_required
from freelan_server.database import DATABASE, User
from freelan_server.forms.user import UserForm
from sqlalchemy.exc import IntegrityError

def create_form(user=None):
    """
    Create a form.
    """

    form = UserForm(obj=user)

    # Only an administrator might edit the network membership.
    if not current_user.admin_flag:
        del form.networks

    # If we are editing a user that is not the current user, we don't need
    # to specify the current password.
    if user != current_user:
        del form.current_password

        if not current_user.admin_flag:
            del form.new_password
            del form.new_password_repeat
            del form.email
            del form.admin_flag
    else:
        del form.admin_flag

    return form

class UserView(MethodView):
    """
    The user view.
    """

    decorators = [login_required]

    def get(self, user_id):

        user = User.query.get(user_id)

        if not user:
            abort(404)

        form = create_form(user)

        referrer = url_for('users')

        return render_template('pages/user.html', form=form, user=user, referrer=referrer)

    def post(self, user_id):

        user = User.query.get(user_id)

        if not user:
            abort(404)

        form = create_form(user)

        referrer = url_for('users')

        if form.validate_on_submit():

            if (user == current_user) and form.new_password.data and not user.check_password(form.current_password.data):
                form.current_password.errors.append('Incorrect password.')
            else:
                if current_user != user and not current_user.admin_flag:
                    abort(403)

                form.populate_obj(user)

                # A new password was set, we need to update the user's one.
                if form.new_password.data:
                    user.password = form.new_password.data

                DATABASE.session.add(user)

                try:
                    DATABASE.session.commit()
                except IntegrityError as ex:
                    DATABASE.session.rollback()

                    m = re.search('column (\w+) is not unique', str(ex.orig))

                    attribute = m and m.group(1) or None

                    if hasattr(form, attribute):
                        form_attribute = getattr(form, attribute)
                    else:
                        form_attribute = form.username

                    form_attribute.errors.append('Database error: "%s".' % ex.orig)

        return render_template('pages/user.html', form=form, user=user, referrer=referrer)

class UserCreateView(MethodView):
    """
    The user create view.
    """

    decorators = [login_required]

    def get(self):

        if not current_user.admin_flag:
            abort(403)

        form = create_form()

        referrer = url_for('users')

        return render_template('pages/user.html', form=form, user=None, referrer=referrer)

    def post(self):

        if not current_user.admin_flag:
            abort(403)

        user = None

        form = create_form()

        referrer = url_for('users')

        if form.validate_on_submit():
            user = User()

            form.populate_obj(user)
            user.password = form.new_password.data

            DATABASE.session.add(user)

            try:
                DATABASE.session.commit()
            except IntegrityError as ex:
                user = None
                DATABASE.session.rollback()

                m = re.search('column (\w+) is not unique', str(ex.orig))

                attribute = m and m.group(1) or None

                if hasattr(form, attribute):
                    form_attribute = getattr(form, attribute)
                else:
                    form_attribute = form.username

                form_attribute.errors.append('Database error: "%s".' % ex.orig)

        return render_template('pages/user.html', form=form, user=user, referrer=referrer)

class UserDeleteView(MethodView):
    """
    The user delete view.
    """

    decorators = [login_required]

    def post(self, user_id):

        if not current_user.admin_flag:
            abort(403)

        user = User.query.get(user_id)

        if not user:
            abort(404)

        if user == current_user:
            abort(403)

        DATABASE.session.delete(user)
        DATABASE.session.commit()

        return redirect(url_for('users'))
