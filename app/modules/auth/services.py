import os

from flask import current_app, url_for

from flask_login import login_user, current_user
from itsdangerous import BadTimeSignature, SignatureExpired, URLSafeTimedSerializer

from app import mail_service
from authlib.integrations.flask_client import OAuth

from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from app.modules.profile.models import UserProfile
from app.modules.profile.repositories import UserProfileRepository
from core.configuration.configuration import uploads_folder_name
from core.services.BaseService import BaseService
from sqlalchemy.exc import IntegrityError


class AuthenticationService(BaseService):

    SALT = "user-confirm"
    MAX_AGE = 3600

    def __init__(self):
        super().__init__(UserRepository())
        self.user_profile_repository = UserProfileRepository()
        self.oauth, self.github = self.configure_oauth(current_app)
        self.orcid, self.orcid = self.configure_oauth_orcid(current_app)

    def configure_oauth(self, app):
        oauth = OAuth(app)
        github = oauth.register(
            name='github',
            api_base_url='https://api.github.com/',
            client_id=os.getenv('GITHUB_CLIENT_ID'),
            client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
            authorize_url='https://github.com/login/oauth/authorize',
            authorize_params=None,
            access_token_url='https://github.com/login/oauth/access_token',
            access_token_params=None,
            refresh_token_url=None,
            client_kwargs={'scope': 'user:email'}
        )
        return oauth, github
    
    def configure_oauth_orcid(self, app):
        oauth = OAuth(app)
        orcid = oauth.register(
            name='orcid',
            api_base_url='https://orcid.org/',
            client_id=os.getenv('ORCID_CLIENT_ID'),
            client_secret=os.getenv('ORCID_CLIENT_SECRET'),
            authorize_url='https://orcid.org/oauth/authorize',
            access_token_url='https://orcid.org/oauth/token',
            client_kwargs={'scope': '/authenticate email',
            'token_endpoint_auth_method': 'client_secret_post'}
        )
        return oauth, orcid

    def login(self, email, password, remember=True):
        user = self.repository.get_by_email(email)
        if user is not None and user.check_password(password):
            login_user(user, remember=remember)
            return True
        return False

    def is_email_available(self, email: str) -> bool:
        return self.repository.get_by_email(email) is None

    def create_with_profile(self, **kwargs):
        try:
            email = kwargs.pop("email", None)
            password = kwargs.pop("password", None)
            name = kwargs.pop("name", None)
            surname = kwargs.pop("surname", None)

            if not email:
                raise ValueError("Email is required.")
            if not password:
                raise ValueError("Password is required.")
            if not name:
                raise ValueError("Name is required.")
            if not surname:
                raise ValueError("Surname is required.")

            user_data = {
                "email": email,
                "password": password,
                "active": False
            }

            profile_data = {
                "name": name,
                "surname": surname,
            }

            user = self.create(commit=False, **user_data)
            profile_data["user_id"] = user.id
            self.user_profile_repository.create(**profile_data)
            self.repository.session.commit()
        except Exception as exc:
            self.repository.session.rollback()
            raise exc
        return user

    def update_profile(self, user_profile_id, form):
        if form.validate():
            updated_instance = self.update(user_profile_id, **form.data)
            return updated_instance, None

        return None, form.errors

    def get_token_from_email(self, email):
        s = self.get_serializer()
        return s.dumps(email, salt=self.SALT)

    def send_confirmation_email(self, user_email):
        token = self.get_token_from_email(user_email)
        url = url_for("auth.confirm_user", token=token, _external=True)
        mail_service.send_email(
            "Email confirmation",
            recipients=[user_email],
            body="Confirm your email",
            html_body=f"<a href='{url}'>Email confirmation</a>",
        )

    def confirm_user_with_token(self, token):
        s = self.get_serializer()
        try:
            email = s.loads(token, salt=self.SALT, max_age=self.MAX_AGE)
        except SignatureExpired:
            raise Exception("The confirmation link has expired.")
        except BadTimeSignature:
            raise Exception("The confirmation link has been tampered with.")
        user = self.repository.get_by_email(email, active=False)
        user.active = True
        self.repository.session.commit()
        return user

    def get_serializer(self):
        return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    def get_authenticated_user(self) -> User | None:
        if current_user.is_authenticated:
            return current_user
        return None

    def get_authenticated_user_profile(self) -> UserProfile | None:
        if current_user.is_authenticated:
            return current_user.profile
        return None

    def temp_folder_by_user(self, user: User) -> str:
        return os.path.join(uploads_folder_name(), "temp", str(user.id))

    def login_from_github(self, user_info) -> User | str:
        email = user_info["email"]
        if email is None:
            return None, "Ensure your email is public in your GitHub account"
        user = self.repository.get_by_email(email)
        if user is None:
            # Generate a random password. It should be notified to the user
            password = User.generate_password()
            user = self.create_with_profile(
                email=email,
                password=password,
                name=user_info["name"] or user_info["login"],
                surname=user_info["name"] or user_info["login"]
            )
        login_user(user, remember=True)
        return user, None
    
    def login_from_orcid(self, user_info):
        orcid_id = user_info.get("sub")
        if orcid_id is None:
            return None, "No se pudo obtener el ORCID ID."

        given_name = user_info.get("given_name", "Usuario ORCID")
        family_name = user_info.get("family_name", f"ORCID-{orcid_id.split('-')[-1]}")
        email = f"{orcid_id}@orcid.org"


        # Verificar si el usuario ya existe por correo electrónico
        user = self.repository.get_by_orcid_id(orcid_id)

        if user is None:
            try:
                # Crear un nuevo usuario si no existe
                password = User.generate_password()
                user = self.create_with_profile(
                    email=email,
                    password=password,
                    name=given_name,
                    surname=family_name,
                )
                user.orcid_id = orcid_id
                self.repository.session.commit()
            except IntegrityError as e:
                self.repository.session.rollback()  # Revertir la transacción
                user = self.repository.get_by_email(email)

        # Iniciar sesión con el usuario (existente o recién creado)
        if user:
            login_user(user, remember=True)
            return user, None
        else:
            return None, "No se pudo completar el inicio de sesión."
