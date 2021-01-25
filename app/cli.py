import click
from flask import Blueprint
from app.factory import db


bp = Blueprint('cli', 'cli', cli_group=None)


@bp.cli.command('init')
def init():
    import app.models
    db.create_all()

@bp.cli.command('list_ops')
def list_ops():
    from app.models import Operation
    ops = Operation.query.all()
    for op in ops:
        click.echo(f'Operation {op.codename} ({op.id})')

@bp.cli.command('list_keys')
def list_keys():
    from app.library.digitalocean import do
    r = do.list_keys()
    click.echo(r.content)

@bp.cli.command('list_volumes')
def list_volumes():
    from app.library.digitalocean import do
    r = do.list_volumes()
    click.echo(r)

@bp.cli.command('create_key')
@click.argument('name')
@click.argument('pubkey_path')
def create_key(name, pubkey_path):
    from app.library.digitalocean import do
    from os.path import expanduser
    with open(expanduser(pubkey_path), 'r') as f:
        pubkey = f.read()
    click.echo(pubkey)
    c = do.create_key(name, pubkey)
    click.echo(c.content)
    c.raise_for_status()
    click.echo(f'Created SSH key {c.json()["ssh_key"]["id"]}')

@bp.cli.command('process_payouts')
def process_payouts():
    import arrow
    from time import sleep
    from app.models import Operation, Payout
    from app.library.monero import wallet, monero
    from app.library.digitalocean import do
    from app.helpers import to_ausd
    from app.helpers import cancel_operation
    from app import config

    operations = Operation.query.all()
    for op in operations:
        if op.droplet_id and op.volume_id:
            click.echo(f'Processing cost of node for operation {op.codename} ({op.id})')
            prices = op.get_pricing(live=True)
            balances = wallet.balances(op.account_idx, atomic=True)
            latest_payout = Payout.query.filter(
                Payout.operation_id == op.id
            ).order_by(Payout.create_date.desc()).first()
            if latest_payout is None:
                last = arrow.get(do.show_droplet(op.droplet_id)['created_at']).datetime
                latest_payout = 'droplet boot time'
            else:
                last = arrow.get(latest_payout.create_date).datetime
                latest_payout = str(latest_payout.id)

            diff = arrow.utcnow() - last
            minutes = diff.seconds / 60
            hours = minutes / 60
            xmr_to_send = hours * prices['in_xmr']
            axmr_to_send = monero.to_atomic(xmr_to_send)
            unlocked_xmr = monero.from_atomic(balances[1])
            locked_xmr = monero.from_atomic(balances[0] - balances[1])
            msg = [
                f' - XMR balance in wallet: {unlocked_xmr} ({locked_xmr} locked) XMR',
                f'\n - XMR market price: ${prices["xmr_price"]}',
                f'\n - Droplet Cost: ${prices["droplet_cost"]}/hour',
                f'\n - Volume Cost: ${prices["volume_cost"]}/hour',
                f'\n - Mgmt Cost: ${prices["mgmt_cost"]}/hour',
                f'\n - Total Cost: ${prices["in_usd"]}/hour ({prices["in_xmr"]} XMR/hour)',
                f'\n - Last payout: {str(latest_payout)}',
                f'\n - {hours} hours ({minutes} minutes) since last payout.',
                f'\n - Planning to send {xmr_to_send} XMR to payout address',
                f'\n - Payout every {config.PAYOUT_FREQUENCY} hours at minimum',
            ]
            click.echo("".join(msg))

            if hours > config.PAYOUT_FREQUENCY:
                click.echo(' - Proceeding to payout.....')
                sleep(10)
                if balances[1] > axmr_to_send:
                    res = wallet.transfer(op.account_idx, config.PAYOUT_ADDRESS, axmr_to_send)
                    if 'tx_hash' in res:
                        click.echo(f' - Sent XMR, Tx ID: {res["tx_hash"]}')
                        p = Payout(
                            operation_id=op.id,
                            total_cost_ausd=to_ausd(prices['in_usd']),
                            xmr_price_ausd=to_ausd(prices['xmr_price']),
                            xmr_sent_axmr=axmr_to_send,
                            xmr_tx_id=res['tx_hash'],
                            hours_since_last=round(hours)
                        )
                        db.session.add(p)
                        db.session.commit()
                        click.echo(f' - Save payout details as {p.id}')
                    elif 'message' in res:
                        click.echo(f' - There was a problem sending XMR: {res["message"]}')
                    else:
                        click.echo(' - Unable to send XMR')
                else:
                    click.echo(f' - Not enough unlocked balance ({monero.from_atomic(balances[1])}) to send XMR')

                if balances[0] < axmr_to_send:
                    click.echo(' - There is not enough locked balance, this droplet should be destroyed')
                    sleep(5)
                    cancel_operation(op.codename)
            else:
                click.echo(' - Skipping payout, not enough time elapsed')

@bp.cli.command('launch_funded_operations')
def launch_funded_operations():
    from time import sleep
    from app.models import Operation
    from app.library.monero import wallet
    from app.library.digitalocean import do

    ops = Operation.query.all()
    prices = Operation().get_pricing()
    for op in ops:
        if not op.droplet_id:
            bal = wallet.balances(op.account_idx, atomic=False)[1]
            if bal > prices['minimum_xmr']:
                click.echo(f'found op {op.codename} with balance {bal} - creating server')
                common_name = 'op-' + op.id

                if do.check_volume_exists(common_name, op.region)[0] is False:
                    volume = do.create_volume(common_name, op.region)
                    op.volume_id = volume['id']
                    db.session.commit()
                    click.echo(f'Created new volume {op.volume_id}')

                droplet = do.create_droplet(
                    op.codename,
                    op.region,
                    [op.volume_id]
                )
                op.droplet_id = droplet['id']
                db.session.commit()
                click.echo(f'Created new droplet {op.droplet_id}')

                sleep(5)
                droplet = do.show_droplet(op.droplet_id)
                for net in droplet['networks']['v4']:
                    if net['type'] == 'public':
                        record = do.create_record(
                            f'{op.codename}.node',
                            net['ip_address'],
                            'A'
                        )
                        op.record_v4_id = record['id']
                        db.session.commit()
                        click.echo(f'Created v4 DNS record {record["id"]}')

                for net in droplet['networks']['v6']:
                    if net['type'] == 'public':
                        record = do.create_record(
                            f'{op.codename}.node',
                            net['ip_address'],
                            'AAAA'
                        )
                        op.record_v6_id = record['id']
                        db.session.commit()
                        click.echo(f'Created v6 DNS record {record["id"]}')

@bp.cli.command('cancel_operation')
@click.argument('codename')
def cancel_operation(codename):
    from app.helpers import cancel_operation
    return cancel_operation(codename)
