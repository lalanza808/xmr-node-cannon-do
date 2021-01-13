import requests
from app import config


class DigitalOcean(object):
    base = 'https://api.digitalocean.com/v2/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + config.DO_TOKEN
    }

    def make_req(self, method, endpoint, data=None):
        url = self.base + endpoint
        if method == 'post':
            r = requests.post(url, headers=self.headers, json=data)
        elif method == 'get':
            r = requests.get(url, headers=self.headers)
        elif method == 'delete':
            r = requests.delete(url, headers=self.headers)
        else:
            return 'method not defined'
        r.raise_for_status()
        return r

    # Domains and records
    def create_record(self, name, ip_addr, type='A'):
        data = {
            'type': type,
            'name': name,
            'data': ip_addr
        }
        r = self.make_req('post', f'domains/{config.DO_DOMAIN}/records', data)
        return r.json()['domain_record']

    def delete_record(self, record_id):
        if record_id:
            route = f'domains/{config.DO_DOMAIN}/records/{record_id}'
            r = self.make_req('delete', route)
            if r.status_code == 204:
                return True
            else:
                return False
        else:
            return False

    # SSH Keys
    def create_key(self, name, public_key):
        data = {
            'name': name,
            'public_key': public_key.strip()
        }
        return self.make_req('post', 'account/keys', data)

    def list_keys(self):
        return self.make_req('get', 'account/keys')

    # Volumes
    def create_volume(self, name, region):
        data = {
            'name': name,
            'size_gigabytes': int(config.DO_DROPLET_STORAGE_GB),
            'region': region,
            'filesystem_type': 'ext4'
        }
        r = self.make_req('post', 'volumes', data)
        return r.json()['volume']

    def list_volumes(self):
        r = self.make_req('get', 'volumes')
        return r.json()['volumes']

    def check_volume_exists(self, name, region):
        r = self.make_req('get', f'volumes?name={name}&region={region}')
        if r.json()['volumes'] == list():
            return (False, None)
        else:
            return (True, r.json()['volumes'][0]['id'])

    def show_volume(self, volume_id):
        r = self.make_req('get', f'volumes/{volume_id}')
        return r.json()['volume']

    # Droplets
    def create_droplet(self, name, region, extra_vols=[]):
        data = {
          'name': name,
          'region': region,
          'size': config.DO_DROPLET_SIZE,
          'image': config.DO_DROPLET_IMAGE,
          'ssh_keys': [
            int(config.DO_SSH_KEY)
          ],
          'backups': False,
          'ipv6': True,
          'user_data': f'#!/bin/bash\nwget https://raw.githubusercontent.com/lalanza808/docker-monero-node/master/cloud-init.sh -q -O - | DOMAIN={name}.node.{config.DO_DOMAIN} ACME_EMAIL={config.ADMIN_EMAIL} GRAF_PASS=${config.GRAF_PASS} GRAF_USER=${config.GRAF_USER} bash',
          'private_networking': None,
          'volumes': extra_vols,
          'tags': []
        }
        r = self.make_req('post', 'droplets', data)
        return r.json()['droplet']

    def destroy_droplet(self, droplet_id):
        if droplet_id:
            route = f'droplets/{droplet_id}/destroy_with_associated_resources/dangerous'
            self.headers['X-Dangerous'] = 'true'
            r = self.make_req('delete', route)
            if r.status_code == 202:
                return True
            else:
                return False
        else:
            return False

    def show_droplet(self, droplet_id):
        if droplet_id:
            r = self.make_req('get', f'droplets/{droplet_id}')
            return r.json()['droplet']
        else:
            return None

    def check_droplet_exists(self, name):
        r = self.make_req('get', 'droplets')
        droplets = r.json()['droplets']
        for d in droplets:
            if d['name'] == name:
                return (True, d['id'])
        return (False, None)

    # Pricing
    def get_droplet_price_usd_per_hour(self, size):
        sizes = {
            's-1vcpu-1gb': .00744,
            's-1vcpu-2gb': .015,
            's-2vcpu-2gb': .022,
            's-2vcpu-4gb': .030,
            's-4vcpu-8gb': .060,
            's-8vcpu-16gb': .119,
        }
        return sizes[size]

    def get_volume_price_usd_per_hour(self, size_gb):
        return round(0.105 * size_gb / 730, 3)


do = DigitalOcean()
