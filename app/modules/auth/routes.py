from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user

from authlib.integrations.base_client.errors import MismatchingStateError

from app.modules.auth import auth_bp
from app.modules.auth.forms import SignupForm, LoginForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService


authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f'Email {email} in use')

        try:
            user = authentication_service.create_with_profile(**form.data)
            authentication_service.send_confirmation_email(user.email)
            flash("Email confirmation", "info")

        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f'Error creating user: {exc}')

        return redirect(url_for('public.index'))

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        if authentication_service.login(form.email.data, form.password.data):
            return redirect(url_for('public.index'))

        return render_template("auth/login_form.html", form=form, error='Invalid credentials')

    return render_template('auth/login_form.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@auth_bp.route("/confirm_user/<token>", methods=["GET"])
def confirm_user(token):
    try:
        user = authentication_service.confirm_user_with_token(token)
    except Exception as exc:
        flash(exc.args[0], "danger")
        return redirect(url_for("auth.show_signup_form"))

    login_user(user, remember=True)
    return redirect(url_for('public.index'))


@auth_bp.route('/login-with-github', methods=['GET'])
def login_with_github():
    callback = url_for('auth.login_with_github_authorized', _external=True)
    return authentication_service.github.authorize_redirect(callback)


@auth_bp.route('/login-with-github/authorized', methods=['GET'])
def login_with_github_authorized():
    try:
        token = authentication_service.github.authorize_access_token()
    except MismatchingStateError:
        return render_template('400.html')

    form = LoginForm()
    if token is None:
        error = 'Access token not provided'
        return render_template("auth/login_form.html", form=form, error=error)

    user_info = authentication_service.github.get('user').json()
    user, error = authentication_service.login_from_github(user_info)
    if user is not None:
        return redirect(url_for('public.index'))

    return render_template("auth/login_form.html", form=form, error=error)


@auth_bp.route('/login-with-google', methods=['GET'])
def login_with_google():
    callback = url_for('auth.login_with_google_callback', _external=True)
    return authentication_service.google.authorize_redirect(callback)


@auth_bp.route('/auth/google/callback', methods=['GET'])
def login_with_google_callback():
    try:
        token = authentication_service.google.authorize_access_token()
    except MismatchingStateError:
        return render_template('400.html')

    form = LoginForm()
    if token is None:
        error = 'Access token not provided'
        return render_template("auth/login_form.html", form=form, error=error)

    user_info = authentication_service.google.get('userinfo').json()
    user, error = authentication_service.login_from_google(user_info)
    if user is not None:
        return redirect(url_for('public.index'))

    return render_template("auth/login_form.html", form=form, error=error)
