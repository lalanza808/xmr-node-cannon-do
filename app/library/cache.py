from json import loads as json_loads
from json import dumps as json_dumps
from datetime import timedelta
from redis import Redis
from requests import get as r_get
from app.library.coingecko import get_market_data
from app.library.monero import wallet
from app.library.digitalocean import do
from app import config


class Cache(object):
    def __init__(self):
        self.redis = Redis(host=config.CACHE_HOST, port=config.CACHE_PORT)

    def store_data(self, item_name, expiration_minutes, data):
        self.redis.setex(
            item_name,
            timedelta(minutes=expiration_minutes),
            value=data
        )

    def get_info(self, codename):
        key_name = f'node_{codename}_info'
        data = self.redis.get(key_name)
        if data:
            return json_loads(data)
        else:
            try:
                dns = f'{codename}.node.{config.DO_DOMAIN}'
                url = f'http://{dns}:18081/get_info'
                r = r_get(url, timeout=6)
                data = r.json()
                self.store_data(key_name, 8, json_dumps(data))
                return data
            except:
                return {'error': 'true'}

    def get_transfers(self, account_idx):
        key_name = f'wallet_txes_{account_idx}'
        data = self.redis.get(key_name)
        if data:
            return json_loads(data)
        else:
            txes = wallet.get_transfers(account_idx)
            self.store_data(key_name, 1, json_dumps(txes))
            return txes

    def get_balances(self, account_idx, atomic=True):
        if atomic:
            extra = '_atomic'
        else:
            extra = ''
        key_name = f'wallet_balances_{account_idx}{extra}'
        data = self.redis.get(key_name)
        if data:
            return json_loads(data)
        else:
            balances = wallet.balances(account_idx, atomic)
            data = {'balance': balances[0], 'unlocked': balances[1]}
            self.store_data(key_name, 1, json_dumps(data))
            return data

    def show_droplet(self, droplet_id):
        key_name = f'droplet_{droplet_id}'
        data = self.redis.get(key_name)
        if data:
            return json_loads(data)
        else:
            droplet = do.show_droplet(droplet_id)
            self.store_data(key_name, 120, json_dumps(droplet))
            return droplet

    def show_volume(self, volume_id):
        key_name = f'volume_{volume_id}'
        data = self.redis.get(key_name)
        if data:
            return json_loads(data)
        else:
            volume = do.show_volume(volume_id)
            self.store_data(key_name, 120, json_dumps(volume))
            return volume

    def get_coin_price(self, cur='usd'):
        key_name = f'xmr_price_{cur}'
        data = self.redis.get(key_name)
        if data:
            return float(data.decode())
        else:
            d = get_market_data()
            amt = d['market_data']['current_price'][cur]
            self.store_data(key_name, 5, amt)
            return amt

    def get_transfer_data(self, subaddress_index):
        key_name = f'xmr_wallet_{subaddress_index}_txes'
        data = self.redis.get(key_name)
        if data:
            return json_loads(data)
        else:
            wallet.get_transfers(subaddress_index)
            self.store_data(key_name, 2, json_dumps(data))
            return data


cache = Cache()
