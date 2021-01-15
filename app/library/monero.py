import requests
import six
import json
from decimal import Decimal
from flask import current_app
from app import config


class WalletRPC(object):
    def __init__(self, rpc_endpoint, username='', password=''):
        self.endpoint = f'{rpc_endpoint}/json_rpc'
        self.auth = requests.auth.HTTPDigestAuth(
            username, password
        )

    def make_wallet_rpc(self, method, params={}):
        r = requests.get(
            self.endpoint,
            timeout=8,
            data=json.dumps({'method': method, 'params': params}),
            auth=self.auth
        )
        r.raise_for_status()
        current_app.logger.info(f'GET - {self.endpoint} - {method}')
        if 'error' in r.json():
            return r.json()['error']
        else:
            return r.json()['result']

    def height(self):
        return self.make_wallet_rpc('get_height', {})

    def new_address(self, account=0, label=None):
        data = {'account_index': account, 'label': label}
        _address = self.make_wallet_rpc('create_address', data)
        return (_address['address_index'], _address['address'])

    def new_account(self, label=None):
        data = {'label': label}
        _account = self.make_wallet_rpc('create_account', data)
        return (_account['account_index'], _account['address'])

    def balances(self, account=0, atomic=True):
        data = {'account_index': account}
        _balance = self.make_wallet_rpc('get_balance', data)
        if atomic:
            return (_balance['balance'], _balance['unlocked_balance'])
        else:
            bal = monero.from_atomic(_balance['balance'])
            unl_bal = monero.from_atomic(_balance['unlocked_balance'])
            return (bal, unl_bal)

    def transfer(self, account_idx, address, amount):
        data = {
            'account_index': account_idx,
            'destinations': [{'address': address, 'amount': amount}],
            'priority': 1,
            'unlock_time': 0,
            'get_tx_key': False,
            'get_tx_hex': False,
            'new_algorithm': True,
            'do_not_relay': False,
        }
        transfer = self.make_wallet_rpc('transfer', data)
        return transfer

    def incoming_transfers(self, subaddress_index):
        data = {
            'subaddr_indices': [subaddress_index],
            'transfer_type': 'all'
        }
        return self.make_wallet_rpc('incoming_transfers', data)

    def get_transfers(self, account_index=0, subaddress_index=None):
        if subaddress_index:
            indices = [subaddress_index]
        else:
            indices = None
        data = {
            'in': True,
            'out': True,
            'subaddr_indices': indices,
            'account_index': account_index
        }
        return self.make_wallet_rpc('get_transfers', data)

    def get_accounts(self):
        return self.make_wallet_rpc('get_accounts')

    def get_balance(self, subaddress_index):
        data = {
            'address_indices': [subaddress_index]
        }
        _balance = self.make_wallet_rpc('get_balance', data)
        res = _balance['per_subaddress'][0]
        return (res['balance'], res['unlocked_balance'])


class CoinUtils(object):
    def __init__(self):
        pass

    def to_atomic(self, amount):
        if not isinstance(amount, (Decimal, float) + six.integer_types):
            raise ValueError("Amount does not have numeric type.")
        return int(amount * 10**self.decimal_points)

    def from_atomic(self, amount):
        fn = Decimal(amount) * self.full_notation
        return (fn).quantize(self.full_notation)

    def as_real(self, amount):
        real = Decimal(amount).quantize(self.full_notation)
        return float(real)


class Monero(CoinUtils):
    def __init__(self):
        self.decimal_points = 12
        self.full_notation = Decimal('0.000000000001')


wallet = WalletRPC(
    '{proto}://{host}:{port}'.format(
        proto=config.XMR_WALLET_RPC_PROTO,
        host=config.XMR_WALLET_RPC_HOST,
        port=config.XMR_WALLET_RPC_PORT
    ),
    config.XMR_WALLET_RPC_USER,
    config.XMR_WALLET_RPC_PASS
)

monero = Monero()
