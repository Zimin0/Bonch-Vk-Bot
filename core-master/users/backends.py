import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions

from cyberbot.settings import AUTH_TOKEN
from users.models import User

logger = logging.getLogger(__name__)


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = "Authorization"

    def authenticate(self, request):
        token = request.headers.get("Authorization")
        # if not token:
        #     raise exceptions.AuthenticationFailed(_("No token provided"))

        return self._authenticate_credentials(token)

    @staticmethod
    def _authenticate_credentials(token):
        # if not token == AUTH_TOKEN:
        #     raise exceptions.AuthenticationFailed(
        #         _("Can't decode token")
        #     ) from Exception

        try:
            user = User.objects.first()
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _("No such user")
            ) from User.DoesNotExist

        return user, token

    def authenticate_header(self, request):  # pylint: disable=W0613
        return "JWT"
