"""Relief-Relay warehouse: 100% Python standard library for simulation.

No third-party packages needed for the dashboard/simulation.
For USB radios, install pyserial: python -m pip install pyserial
Start dashboard: python server.py
With LoRa receiver: python server.py --radio COM5
With physical scale: python server.py --radio COM5 --scale COM6
Access only on the warehouse laptop: http://127.0.0.1:5000/
"""
import argparse
import json
import re
import sqlite3
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

try:
    import serial
except ImportError:
    serial = None

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'relief_relay.sqlite3'
HTML_PATH = ROOT / 'templates' / 'index.html'
DRIVER_PATH = ROOT / 'templates' / 'driver.html'

# Demo-only kit recipe and weights: NOT actual humanitarian allocation standards.
ITEMS = {
    'water': {'name': 'Water 500mL', 'weight_g': 520, 'stock': 150},
    'food': {'name': 'Food ration pack', 'weight_g': 300, 'stock': 150},
    'infant': {'name': 'Infant-care kit', 'weight_g': 250, 'stock': 20},
    'senior_support': {'name': 'Senior support kit (non-medical)', 'weight_g': 220, 'stock': 30},
    'repellent': {'name': 'Mosquito repellent', 'weight_g': 100, 'stock': 30},
    'thermal': {'name': 'Thermal blanket', 'weight_g': 380, 'stock': 30},
    'tarp': {'name': 'Tarpaulin', 'weight_g': 650, 'stock': 30},
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def connect():
    db = sqlite3.connect(str(DB_PATH), timeout=8)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA busy_timeout=8000')
    return db


def init_db():
    with connect() as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('''CREATE TABLE IF NOT EXISTS requests (
            id TEXT PRIMARY KEY, zone TEXT NOT NULL, people INTEGER NOT NULL,
            infants INTEGER NOT NULL, disaster TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'RECEIVED', created_at TEXT NOT NULL,
            expected_g REAL, last_weight_g REAL, checked INTEGER DEFAULT 0
        )''')
        # Upgrade existing databases without erasing their saved requests.
        current_cols = {row[1] for row in db.execute('PRAGMA table_info(requests)')}
        for col, ddl in (
            ('seniors', 'INTEGER NOT NULL DEFAULT 0'),
            ('medicine', "TEXT NOT NULL DEFAULT 'NONE'"),
            ('medicine_note', "TEXT NOT NULL DEFAULT ''"),
        ):
            if col not in current_cols:
                db.execute(f'ALTER TABLE requests ADD COLUMN {col} {ddl}')
        db.execute('''CREATE TABLE IF NOT EXISTS inventory (
            item TEXT PRIMARY KEY, qty INTEGER NOT NULL CHECK(qty >= 0)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS kit_items (
            request_id TEXT NOT NULL, item TEXT NOT NULL, qty INTEGER NOT NULL,
            PRIMARY KEY(request_id,item)
        )''')
        db.execute('''CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY CHECK(id=1), grams REAL,
            source TEXT, measured_at REAL
        )''')
        for key, item in ITEMS.items():
            db.execute('INSERT OR IGNORE INTO inventory(item,qty) VALUES (?,?)',
                       (key, item['stock']))


def decode(message):
    '''Accept old RR1 messages (6 fields), and V4 messages (9 fields).

    V4: RR1|ID|ZONE|PEOPLE|INFANTS|DISASTER|SENIORS|MED_TYPE|MED_NOTE
    Medication notes are short demo-only request hints, not prescriptions.
    '''
    if not isinstance(message, str):
        raise ValueError('Message must be text')
    if len(message) > 120:
        raise ValueError('Message too long')
    parts = message.strip().split('|')
    if len(parts) not in (6, 9) or parts[0] != 'RR1':
        raise ValueError('Wrong protocol or field count')
    _, rid, zone, people_str, infants_str, disaster = parts[:6]
    if not (3 <= len(rid) <= 30 and rid.isascii() and rid.isalnum() and
            1 <= len(zone) <= 12 and zone.isascii() and zone.isalnum()):
        raise ValueError('Bad ID or zone')
    people, infants = int(people_str), int(infants_str)
    if not 1 <= people <= 12 or not 0 <= infants <= people:
        raise ValueError('Impossible household size')
    if disaster not in ('FLOOD', 'QUAKE', 'CYCLONE'):
        raise ValueError('Unknown disaster')
    if len(parts) == 6:
        return rid, zone, people, infants, disaster
    seniors_str, medicine, note = parts[6:]
    seniors = int(seniors_str)
    if not 0 <= seniors <= people or seniors + infants > people:
        raise ValueError('Senior/infant counts exceed household size')
    if medicine not in ('NONE', 'REGULAR', 'FIRST_AID', 'URGENT'):
        raise ValueError('Unknown medical need category')
    if not re.fullmatch(r'[A-Za-z0-9 ._-]{0,24}', note):
        raise ValueError('Medicine note: use up to 24 English letters/numbers/spaces; no | separators')
    return rid, zone, people, infants, disaster, seniors, medicine, note


def ingest(message):
    row = decode(message)
    if len(row) == 5:
        row = (*row, 0, 'NONE', '')
    with connect() as db:
        cur = db.execute('''INSERT OR IGNORE INTO requests
            (id,zone,people,infants,disaster,seniors,medicine,medicine_note,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)''', (*row, now()))
        return cur.rowcount > 0


def planned_items(people, infants, disaster, seniors=0):
    kits = {'water': people, 'food': people}
    if infants:
        kits['infant'] = infants
    if seniors:
        kits['senior_support'] = seniors
    if disaster == 'FLOOD':
        kits['repellent'] = 1
    elif disaster == 'QUAKE':
        kits['thermal'] = 1
    elif disaster == 'CYCLONE':
        kits['tarp'] = 1
    # NO prescription medicines are automatically packed or recommended.
    # Medical requests must be reviewed by an appropriately qualified person.
    return kits


def rows_to_dict(rows):
    return [dict(r) for r in rows]


def state():
    with connect() as db:
        reqs = rows_to_dict(db.execute('SELECT * FROM requests ORDER BY created_at DESC'))
        stock = {r['item']: r['qty'] for r in rows_to_dict(db.execute('SELECT * FROM inventory'))}
        kits = {}
        for r in rows_to_dict(db.execute('SELECT * FROM kit_items')):
            kits.setdefault(r['request_id'], {})[r['item']] = r['qty']
        measurement = db.execute('SELECT * FROM measurements WHERE id=1').fetchone()
    m = dict(measurement) if measurement else None
    if m:
        m['fresh'] = time.time() - m['measured_at'] <= 15
    for r in reqs:
        r['proposed'] = planned_items(r['people'], r['infants'], r['disaster'], r['seniors'])
        r['kit'] = kits.get(r['id'], {})
    return {'requests': reqs, 'inventory': stock, 'items': ITEMS, 'measurement': m}


def assign(rid):
    with connect() as db:
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT * FROM requests WHERE id=?', (rid,)).fetchone()
        if row is None:
            return 404, {'error': 'Unknown request'}
        if row['status'] != 'RECEIVED':
            return 409, {'error': 'Can only assign a new request'}
        proposed = planned_items(row['people'], row['infants'], row['disaster'], row['seniors'])
        stock = {r['item']: r['qty'] for r in db.execute('SELECT * FROM inventory')}
        shortages = {k: qty - stock.get(k, 0) for k, qty in proposed.items()
                     if stock.get(k, 0) < qty}
        if shortages:
            return 409, {'error': 'Insufficient stock. Coordinator review needed.',
                         'shortages': shortages}
        for item, qty in proposed.items():
            db.execute('UPDATE inventory SET qty=qty-? WHERE item=?', (qty, item))
            db.execute('INSERT INTO kit_items(request_id,item,qty) VALUES(?,?,?)',
                       (rid, item, qty))
        grams = sum(ITEMS[k]['weight_g'] * qty for k, qty in proposed.items())
        db.execute("UPDATE requests SET status='ASSIGNED',expected_g=? WHERE id=?", (grams, rid))
        return 200, {'ok': True, 'expected_g': grams}


def record_weight(grams, source):
    if not 0 <= grams <= 10000:
        raise ValueError('Implausible reading (0–10000 g)')
    with connect() as db:
        db.execute('''INSERT INTO measurements(id,grams,source,measured_at)
            VALUES(1,?,?,?) ON CONFLICT(id) DO UPDATE SET
            grams=excluded.grams,source=excluded.source,measured_at=excluded.measured_at''',
            (grams, source, time.time()))


def verify(rid, data):
    if data.get('checklist_confirmed') is not True:
        return 400, {'error': 'Worker must independently confirm every item'}
    with connect() as db:
        row = db.execute('SELECT * FROM requests WHERE id=?', (rid,)).fetchone()
        reading = db.execute('SELECT * FROM measurements WHERE id=1').fetchone()
        if not row or row['status'] != 'ASSIGNED':
            return 409, {'error': 'Assign the kit first'}
        if reading is None or time.time() - reading['measured_at'] > 15:
            return 409, {'error': 'No fresh scale reading (last 15 seconds)'}
        tolerance = max(100, row['expected_g'] * 0.05)
        if abs(reading['grams'] - row['expected_g']) > tolerance:
            return 409, {'error': 'Weight outside demo tolerance',
                         'expected_g': row['expected_g'],
                         'measured_g': reading['grams'], 'tolerance_g': tolerance}
        db.execute('''UPDATE requests SET status='VERIFIED',last_weight_g=?,checked=1
            WHERE id=?''', (reading['grams'], rid))
        return 200, {'ok': True, 'source': reading['source']}


def advance(rid):
    with connect() as db:
        row = db.execute('SELECT status FROM requests WHERE id=?', (rid,)).fetchone()
        if not row:
            return 404, {'error': 'Unknown request'}
        next_status = {'VERIFIED': 'DISPATCHED', 'DISPATCHED': 'DELIVERED'}.get(row['status'])
        if not next_status:
            return 409, {'error': 'Invalid status transition'}
        db.execute('UPDATE requests SET status=? WHERE id=?', (next_status, rid))
        return 200, {'ok': True, 'status': next_status}


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        buf = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(buf)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(buf)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ('/', '/driver'):
            buf = (HTML_PATH if path == '/' else DRIVER_PATH).read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(buf)))
            self.end_headers()
            self.wfile.write(buf)
        elif path == '/api/state':
            self.send_json(state())
        else:
            self.send_json({'error': 'Not found'}, 404)

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 0 or length > 2000:
                self.send_json({'error': 'Request too large'}, 413)
                return
            data = json.loads(self.rfile.read(length)) if length else {}
            if not isinstance(data, dict):
                raise ValueError('Expected JSON object')
            if path == '/api/demo':
                inserted = ingest(data.get('message'))
                result = 200, {'ok': True, 'inserted': inserted,
                               'note': 'SIMULATED: bypassed radio'}
            elif path == '/api/demo-weight':
                record_weight(float(data['grams']), 'SIMULATED')
                result = 200, {'ok': True, 'note': 'SIMULATED weight'}
            elif path.startswith('/api/assign/'):
                result = assign(path.removeprefix('/api/assign/'))
            elif path.startswith('/api/verify/'):
                result = verify(path.removeprefix('/api/verify/'), data)
            elif path.startswith('/api/advance/'):
                result = advance(path.removeprefix('/api/advance/'))
            else:
                result = 404, {'error': 'Not found'}
            self.send_json(result[1], result[0])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.send_json({'error': str(exc)}, 400)
        except (sqlite3.Error, OSError) as exc:
            self.send_json({'error': 'Local server error: ' + str(exc)}, 500)


def read_radio(port):
    if serial is None:
        print('[RADIO] Please install pyserial with: python -m pip install pyserial')
        return
    while True:
        try:
            with serial.Serial(port, 115200, timeout=1) as dev:
                print('[RADIO] Connected to', port)
                while True:
                    line = dev.readline().decode('ascii', errors='replace').strip()
                    if line.startswith('RR1|'):
                        try:
                            inserted = ingest(line)
                            print('[RADIO]', 'NEW' if inserted else 'DUPLICATE', line)
                        except (ValueError, sqlite3.Error) as exc:
                            print('[RADIO] REJECTED', exc)
        except Exception as exc:
            print('[RADIO] Port unavailable; retrying:', exc)
            time.sleep(3)


def read_scale(port):
    if serial is None:
        print('[SCALE] Please install pyserial with: python -m pip install pyserial')
        return
    while True:
        try:
            with serial.Serial(port, 115200, timeout=1) as dev:
                print('[SCALE] Connected to', port)
                while True:
                    line = dev.readline().decode('ascii', errors='replace').strip()
                    if line.startswith('WEIGHT|'):
                        try:
                            record_weight(float(line.split('|', 1)[1]), 'PHYSICAL SCALE')
                        except ValueError:
                            pass
        except Exception as exc:
            print('[SCALE] Port unavailable; retrying:', exc)
            time.sleep(3)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--radio', help='LoRa receiver USB serial port (COM5 or /dev/ttyUSB0)')
    parser.add_argument('--scale', help='HX711 ESP32 USB serial port (COM6 or /dev/ttyUSB1)')
    parser.add_argument('--web-port', type=int, default=5000)
    parser.add_argument('--lan', action='store_true', help='Bind to local network; demo only, no authentication')
    args = parser.parse_args()
    init_db()
    for port, fn in ((args.radio, read_radio), (args.scale, read_scale)):
        if port:
            threading.Thread(target=fn, args=(port,), daemon=True).start()
    print('Warehouse dashboard: http://127.0.0.1:%d' % args.web_port)
    print('No external Python packages are needed until a USB sensor/radio is connected.')
    bind = '0.0.0.0' if args.lan else '127.0.0.1'
    if args.lan: print('LOCAL DEMO ACCESS: http://<warehouse-laptop-local-IP>:%d/driver' % args.web_port)
    ThreadingHTTPServer((bind, args.web_port), Handler).serve_forever()
