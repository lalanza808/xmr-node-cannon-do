from requests import get as r_get
from flask import current_app


def get_market_data(coin_name='monero'):
    data = {
        'localization': False,
        'tickers': False,
        'market_data': True,
        'community_data': False,
        'developer_data': False,
        'sparkline': False
    }
    headers = {'accept': 'application/json'}
    url = f'https://api.coingecko.com/api/v3/coins/{coin_name}'
    current_app.logger.info(f'GET - {url}')
    r = r_get(url, headers=headers, data=data)
    return r.json()
