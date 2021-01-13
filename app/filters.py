from flask import Blueprint, current_app


bp = Blueprint('filters', 'filters')


@bp.app_template_filter()
def humanize(s):
    from arrow import get as arrow_get
    return arrow_get(s).humanize()

@bp.app_template_filter()
def humanizes(s):
    from arrow import get as arrow_get
    return arrow_get(s).humanize()

@bp.app_template_filter()
def from_atomic_xmr(v):
    from app.library.monero import monero
    return monero.as_real(monero.from_atomic(v))

@bp.app_template_filter()
def from_atomic_usd(v):
    from app.helpers import from_ausd
    return from_ausd(v)

@bp.app_template_filter()
def ts(v):
    from datetime import datetime
    return datetime.fromtimestamp(v)

@bp.app_template_filter()
def xmr_block_explorer(v):
    if current_app.config['DEBUG']:
        return f'https://stagenet.xmrchain.net/search?value={v}'
    else:
        return f'https://www.exploremonero.com/transaction/{v}'
