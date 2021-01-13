from flask import Blueprint
from app.models import Operation
from app.library.cache import cache


bp = Blueprint('api', 'api')


@bp.route('/api/info/<codename>')
def get_info(codename):
    op = Operation.query.filter(Operation.codename == codename).first()
    if op:
        return cache.get_info(op.codename)
    else:
        return {}
