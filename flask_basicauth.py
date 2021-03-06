"""
    flask.ext.basicauth
    ~~~~~~~~~~~~~~~~~~~

    Flask-BasicAuth is a Flask extension that provides an easy way to protect
    certain views or your whole application with HTTP basic access
    authentication.

    :copyright: (c) 2013 Janne Vanhala.
    :license: BSD, see LICENSE for more details.
"""
from functools import wraps

from flask import current_app, request, Response

from encryption import decrypt_aes

__version__ = '1.0.2'


class BasicAuth(object):
    """
    A Flask extension for adding HTTP basic access authentication to the
    application.

    :param app: a :class:`~flask.Flask` instance. Defaults to `None`. If no
        application is provided on creation, then it can be provided later on
        via :meth:`init_app`.
    """

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        """
        Initialize this BasicAuth extension for the given application.

        :param app: a :class:`~flask.Flask` instance
        """
        app.config.setdefault('BASIC_AUTH_FORCE', False)
        app.config.setdefault('BASIC_AUTH_REALM', '')
        app.config.setdefault('BASIC_AUTH_EXCLUDE', [])

        @app.before_request
        def require_basic_auth():
            if not current_app.config['BASIC_AUTH_FORCE']:
                return
            else:
                print(request.path)
                if request.method == "OPTIONS" or 'favicon.ico' in request.path:
                    return Response("{}", status=204, mimetype='application/json')
                req = request
                method, endpoint = request.method, request.url_rule.endpoint
                print("{0}:{1}".format(endpoint, method))
                exclude = current_app.config['BASIC_AUTH_EXCLUDE']
                if not "{0}:{1}".format(endpoint, method) in exclude and not self.authenticate():
                    return self.challenge()

    def check_credentials(self, username, password):
        """
        Check if the given username and password are correct.

        By default compares the given username and password to
        ``BASIC_AUTH_USERNAME`` and ``BASIC_AUTH_PASSWORD``
        configuration variables.

        :param username: a username provided by the client
        :param password: a password provided by the client
        :returns: `True` if the username and password combination was correct,
            and `False` otherwise.
        """
        correct_username = current_app.config['BASIC_AUTH_USERNAME']
        correct_password = current_app.config['BASIC_AUTH_PASSWORD']
        if username is not None and password is not None:
            return True
        else:
            return False

    def authenticate(self):
        """
        Check the request for HTTP basic access authentication header and try
        to authenticate the user.

        :returns: `True` if the user is authorized, or `False` otherwise.
        """
        # auth = request.authorization
        try:
            auth = request.headers["Authorization"]
            print(auth)
            auth = auth[auth.rfind(" ") + 1:]
            print(auth)
            auth = decrypt_aes(auth)
            print(auth)
            cred = auth.split(":")
            usertype, username, password = cred[0], cred[1], cred[2]
            return self.check_credentials(username, password)
        except:
            return False

    def challenge(self):
        """
        Challenge the client for username and password.

        This method is called when the client did not provide username and
        password in the request, or the username and password combination was
        wrong.

        :returns: a :class:`~flask.Response` with 401 response code, including
            the required authentication scheme and authentication realm.
        """
        realm = current_app.config['BASIC_AUTH_REALM']
        return Response(
            status=401,
            headers={'WWW-Authenticate': 'Basic realm="%s"' % realm}
        )

    def required(self, view_func):
        """
        A decorator that can be used to protect specific views with HTTP
        basic access authentication.
        """

        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if self.authenticate():
                return view_func(*args, **kwargs)
            else:
                return self.challenge()

        return wrapper
