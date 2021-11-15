from flask import Blueprint, render_template
from app.models import Operation
from app.library.cache import cache
from app import config


bp = Blueprint('api', 'api')


@bp.route('/api/info/<codename>')
def get_info(codename):
    op = Operation.query.filter(Operation.codename == codename).first()
    if op:
        return cache.get_info(op.codename)
    else:
        return {}

@bp.route('/api/export/ansible')
def export_ansible():
    ops = Operation.query.filter(
        Operation.droplet_id > 0
    )
    return render_template(
        'export_ansible.html',
        ops=ops,
        domain=config.DO_DOMAIN
    )

@bp.route('/api/export/upstreams')
def export_upstreams():
    ops = Operation.query.filter(
        Operation.droplet_id > 0
    )
    return render_template(
        'export_upstreams.html',
        ops=ops,
        domain=config.DO_DOMAIN
    )
