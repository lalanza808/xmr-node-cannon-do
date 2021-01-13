from dotenv import load_dotenv
from secrets import token_urlsafe
from os import getenv


load_dotenv()

# Site meta
SITE_NAME = getenv('SITE_NAME', 'XMR Node Cannon')
SECRET_KEY = getenv('SECRET_KEY')
SERVER_NAME = getenv('SERVER_NAME', 'localhost:5000')
MGMT_SURCHARGE_PER_HOUR = float(getenv('MGMT_CHARGE_HOUR', 0.006))
PAYOUT_ADDRESS = getenv('PAYOUT_ADDRESS')
PAYOUT_FREQUENCY = int(getenv('PAYOUT_FREQUENCY', 3))
ADMIN_EMAIL = getenv('ADMIN_EMAIL')
STATS_TOKEN = getenv('STATS_TOKEN', token_urlsafe(12))
GRAF_PASS = getenv('GRAF_PASS', token_urlsafe(12))
GRAF_USER = getenv('GRAF_USER', 'admin')
LAUNCHPAD_ENABLED = int(getenv('LAUNCHPAD_ENABLED', 1))

# Crypto RPC
XMR_WALLET_PASS = getenv('XMR_WALLET_PASS')
XMR_WALLET_RPC_USER = getenv('XMR_WALLET_RPC_USER')
XMR_WALLET_RPC_PASS = getenv('XMR_WALLET_RPC_PASS')
XMR_WALLET_RPC_ENDPOINT = getenv('XMR_WALLET_RPC_ENDPOINT')
XMR_WALLET_RPC_HOST = getenv('XMR_WALLET_RPC_HOST')
XMR_WALLET_RPC_PORT = getenv('XMR_WALLET_RPC_PORT')
XMR_WALLET_RPC_PROTO = getenv('XMR_WALLET_RPC_PROTO')
XMR_DAEMON_URI = getenv('XMR_DAEMON_URI')

# Database
DB_HOST = getenv('DB_HOST', 'localhost')
DB_PORT = getenv('DB_PORT', 5432)
DB_NAME = getenv('DB_NAME', 'nodecannon')
DB_USER = getenv('DB_USER', 'nodecannon')
DB_PASS = getenv('DB_PASS')

# Cache
CACHE_HOST = getenv('CACHE_HOST', 'localhost')
CACHE_PORT = getenv('CACHE_PORT', 6379)

# Development
TEMPLATES_AUTO_RELOAD = True

# Digital Ocean
DO_TOKEN = getenv('DO_TOKEN')
DO_SSH_KEY = getenv('DO_SSH_KEY')
DO_DROPLET_IMAGE = getenv('DO_DROPLET_IMAGE', 'ubuntu-20-04-x64')
DO_DROPLET_SIZE = getenv('DO_DROPLET_SIZE', 's-2vcpu-2gb')
DO_DROPLET_STORAGE_GB = int(getenv('DO_DROPLET_STORAGE_GB', 110))
DO_DOMAIN = getenv('DO_DOMAIN', SERVER_NAME)
