from domain import AuthDomain
from application import UseCases
class AuthApplication(AuthDomain, UseCases):
    pass