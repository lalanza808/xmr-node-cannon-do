from flask import Blueprint, render_template, request
from app.models import Operation
from app.helpers import generate_qr
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
    qrcode = generate_qr(
        config.PAYOUT_ADDRESS, "Donation to @lza_menace on xmrcannon.net"
    )
    return render_template(
        'info.html',
        prices=Operation().get_pricing(),
        config=config,
        qrcode=qrcode
    )


@bp.route('/stats')
def stats():
    token = config.STATS_TOKEN == request.args.get('token')
    all_ops = {'active': [], 'inactive': []}
    ops = Operation.query.all()
    for op in ops:
        if op.has_txes():
            all_ops['active'].append(op)
        else:
            all_ops['inactive'].append(op)
    return render_template(
        'stats.html',
        all_ops=all_ops,
        token=token
    )
