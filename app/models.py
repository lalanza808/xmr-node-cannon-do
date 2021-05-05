from datetime import datetime
from uuid import uuid4
from sqlalchemy import func
from app.factory import db
from app.library.cache import cache
from app.library.digitalocean import do
from app import config


def utcnow():
    return datetime.utcnow()


def rand_id():
    return uuid4().hex


class Operation(db.Model):
    __tablename__ = 'operations'

    id = db.Column(db.String(80), primary_key=True, default=rand_id)
    create_date = db.Column(db.DateTime, server_default=func.now())
    codename = db.Column(db.String(30), unique=True)
    address = db.Column(db.String(150), unique=True)
    account_idx = db.Column(db.Integer, unique=True)
    region = db.Column(db.String(30))
    droplet_id = db.Column(db.Integer, unique=True, nullable=True)
    volume_id = db.Column(db.String(80), unique=True, nullable=True)
    record_v4_id = db.Column(db.Integer, unique=True, nullable=True)
    record_v6_id = db.Column(db.Integer, unique=True, nullable=True)

    def get_node_tor_url(self):
        u = cache.get_tor_url(self.codename)
        return u.decode()

    def get_node_url(self):
        return f'{self.codename}.node.{config.DO_DOMAIN}'

    def get_balances(self, atomic=True):
        b = cache.get_balances(self.account_idx, atomic=atomic)
        return b

    def get_last_payout(self):
        last_payout = Payout.query.filter(
            Payout.operation_id == self.id
        ).order_by(Payout.create_date.desc()).first()
        return last_payout

    def get_pricing(self, live=False):
        if live:
            droplet_size = cache.show_droplet(self.droplet_id)['size_slug']
            volume_size = cache.show_volume(self.volume_id)['size_gigabytes']
        else:
            droplet_size = config.DO_DROPLET_SIZE
            volume_size = config.DO_DROPLET_STORAGE_GB
        xmr_price = cache.get_coin_price()
        droplet_cost = do.get_droplet_price_usd_per_hour(droplet_size)
        volume_cost = do.get_volume_price_usd_per_hour(volume_size)
        mgmt_cost = config.MGMT_SURCHARGE_PER_HOUR
        total_cost_hour_usd = droplet_cost + volume_cost + mgmt_cost
        total_cost_hour_xmr = total_cost_hour_usd / xmr_price
        pricing = {
            'droplet_cost': droplet_cost,
            'volume_cost': volume_cost,
            'mgmt_cost': mgmt_cost,
            'in_usd': total_cost_hour_usd,
            'in_xmr': total_cost_hour_xmr,
            'xmr_price': xmr_price,
            'minimum_xmr': total_cost_hour_xmr * 336  # 2 weeks
        }
        return pricing

    def has_txes(self):
        txes = cache.get_transfers(self.account_idx)
        if txes:
            return True
        else:
            return False

    def __repr__(self):
        return self.id


class Payout(db.Model):
    __tablename__ = 'payouts'

    id = db.Column(db.Integer, primary_key=True)
    operation_id = db.Column(db.String(80), db.ForeignKey('operations.id'))
    create_date = db.Column(db.DateTime, server_default=func.now())
    total_cost_ausd = db.Column(db.Integer)
    xmr_price_ausd = db.Column(db.Integer)
    xmr_sent_axmr = db.Column(db.BigInteger)
    xmr_tx_id = db.Column(db.String(80))
    hours_since_last = db.Column(db.Integer)

    def __repr__(self):
        return self.id
