from app.models import Operation
from app.library.digitalocean import do
from app.factory import db
from flask import current_app


def to_ausd(amount):
    return int(amount * 1000000)


def from_ausd(amount):
    return amount / 1000000


def cancel_operation(codename):
    op = Operation.query.filter(
        Operation.codename == codename
    ).first()
    if op:
        if op.droplet_id:
            do.destroy_droplet(op.droplet_id)
            op.droplet_id = None
            op.volume_id = None
            db.session.commit()
            current_app.logger.info(f'Deleted droplet and associated volume for {codename}')
        if op.record_v4_id:
            r = do.delete_record(op.record_v4_id)
            if r:
                op.record_v4_id = None
                db.session.commit()
                print(f'Deleted A records for {codename}')
        if op.record_v6_id:
            r = do.delete_record(op.record_v6_id)
            if r:
                op.record_v6_id = None
                db.session.commit()
                current_app.logger.info(f'Deleted AAAA records for {codename}')
    else:
        print('Not an op')
