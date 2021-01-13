from flask import Blueprint, render_template, request
from app.models import Operation
from app import config


bp = Blueprint('meta', 'meta')


@bp.route('/')
def index():
    funded_ops = Operation.query.filter(
        Operation.droplet_id > 0
    )
    return render_template(
        'index.html',
        funded_ops=funded_ops,
        site_name=config.DO_DOMAIN,
    )


@bp.route('/info')
def info():
    return render_template(
        'info.html',
        prices=Operation().get_pricing(),
        config=config
    )


@bp.route('/stats')
def stats():
    token = config.STATS_TOKEN == request.args.get('token')
    ops = Operation.query.all()
    return render_template(
        'stats.html',
        ops=ops,
        token=token
    )
