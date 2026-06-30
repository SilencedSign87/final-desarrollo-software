from ..models.user import User
from ..extensions import db
from sqlalchemy.exc import SQLAlchemyError

@staticmethod
def get_all():
    return User.query.all()
