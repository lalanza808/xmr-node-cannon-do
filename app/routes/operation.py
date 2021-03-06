from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.library.monero import wallet
from app.library.digitalocean import do
from app.library.cache import cache
from app.forms import CreateOperation
from app.helpers import generate_qr
from app.factory import db
from app.models import Operation, Payout
from app import config


bp = Blueprint('operation', 'operation')


@bp.route('/launchpad', methods=['GET', 'POST'])
def launchpad():
    enabled = config.LAUNCHPAD_ENABLED == True
    if enabled is False:
        flash(
            'New launches have been disabled by the administrator for the time being.'
            ' Try again later!'
        )
        return redirect(url_for('meta.index'))
    op_count = Operation.query.filter(
        Operation.droplet_id > 0
    ).count()
    op_limit = do.show_account()['droplet_limit']
    if op_count >= op_limit:
        flash('Maximum number of nodes in orbit already. Try again later!')
        return redirect(url_for('meta.index'))
    form = CreateOperation(request.form)
    if form.validate_on_submit():
        op = Operation.query.filter(
            Operation.codename == form.codename.data.lower()
        ).first()
        if not op:
            xmr_addr = wallet.new_account()
            op = Operation(
                codename=form.codename.data.lower(),
                address=str(xmr_addr[1]),
                account_idx=xmr_addr[0],
                region=form.region.data
            )
            db.session.add(op)
            db.session.commit()
            return redirect(url_for('operation.view_operation', id=op.id))
        else:
            flash('That alias already exists')
    return render_template('create_operation.html', form=form)


@bp.route('/operation/<id>')
def view_operation(id):
    op = Operation.query.get(id)
    if op:
        all_transfers = list()
        txes = cache.get_transfers(op.account_idx)
        for type in txes:
            for tx in txes[type]:
                all_transfers.append(tx)
        droplet = cache.show_droplet(op.droplet_id)
        last_payout = Payout.query.filter(
            Payout.operation_id == op.id
        ).order_by(Payout.create_date.desc()).first()
        qrcode = generate_qr(op.address, f"Funding operation {op.id} on xmrcannon.net")
        return render_template(
            'view_operation.html',
            op=op,
            qrcode=qrcode,
            txes=all_transfers,
            prices=op.get_pricing(),
            droplet=droplet,
            last_payout=last_payout,
            config=config
        )
    else:
        flash('ID does not exist')
        return redirect(url_for('meta.index'))


@bp.route('/operation/<id>/payouts')
def view_operation_payouts(id):
    payouts = Payout.query.filter(Payout.operation_id == id)
    if payouts.first() is None:
        flash('No payouts exist for that launch yet')
        return redirect(url_for('operation.view_operation', id=id))
    return render_template('view_payouts.html', payouts=payouts, id=id)
