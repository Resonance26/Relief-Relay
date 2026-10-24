"""Send a demo request to the local dashboard WITHOUT using radio hardware.
Run the warehouse server first, then: python simulate_packet.py
"""
import json
import secrets
import urllib.request

rid = 'RDEMO' + secrets.token_hex(3).upper()
packet = f'RR1|{rid}|YEL03|4|1|FLOOD'
req = urllib.request.Request('http://127.0.0.1:5000/api/demo',
    data=json.dumps({'message': packet}).encode(),
    headers={'Content-Type': 'application/json'}, method='POST')
print('Simulating:', packet)
with urllib.request.urlopen(req) as response:
    print(response.read().decode())
