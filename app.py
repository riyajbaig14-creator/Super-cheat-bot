from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time
import threading

app = Flask(__name__)
CORS(app)

# ========== 2000+ SERVERS ==========
servers = []
countries = ['US','UK','CA','DE','FR','JP','AU','IN','BR','RU','CN','KR','SG','NL','IT','ES',
             'SE','NO','DK','FI','PL','CZ','AT','CH','BE','IE','PT','GR','HU','RO','BG','HR',
             'SK','SI','EE','LV','LT','IS','LU','MT','CY','AL','BA','RS','ME','MK','BY','UA',
             'GE','AM','AZ','KZ','UZ','KG','TM','TJ','MN','TW','HK','MO','PH','MY','ID','TH',
             'VN','KH','LA','MM','BD','PK','AF','IR','IQ','SA','AE','QA','KW','BH','OM','YE',
             'JO','IL','LB','SY','TR','EG','DZ','MA','TN','LY','SD','ET','KE','TZ','UG','ZA',
             'NG','GH','CI','SN','ML','BF','NE','TD','CM','CF','GA','CD','AO','MZ','ZM','ZW',
             'MW','MG','MU','SC','KM','DJ','ER']

flags = {
    'US': '🇺🇸', 'UK': '🇬🇧', 'CA': '🇨🇦', 'DE': '🇩🇪', 'FR': '🇫🇷',
    'JP': '🇯🇵', 'AU': '🇦🇺', 'IN': '🇮🇳', 'BR': '🇧🇷', 'RU': '🇷🇺',
    'CN': '🇨🇳', 'KR': '🇰🇷', 'SG': '🇸🇬', 'NL': '🇳🇱', 'IT': '🇮🇹',
    'ES': '🇪🇸', 'SE': '🇸🇪', 'NO': '🇳🇴', 'DK': '🇩🇰', 'FI': '🇫🇮',
    'PL': '🇵🇱', 'CZ': '🇨🇿', 'AT': '🇦🇹', 'CH': '🇨🇭', 'BE': '🇧🇪',
    'IE': '🇮🇪', 'PT': '🇵🇹', 'GR': '🇬🇷', 'HU': '🇭🇺', 'RO': '🇷🇴',
    'BG': '🇧🇬', 'HR': '🇭🇷', 'SK': '🇸🇰', 'SI': '🇸🇮', 'EE': '🇪🇪',
    'LV': '🇱🇻', 'LT': '🇱🇹', 'IS': '🇮🇸', 'LU': '🇱🇺', 'MT': '🇲🇹',
    'CY': '🇨🇾', 'AL': '🇦🇱', 'BA': '🇧🇦', 'RS': '🇷🇸', 'ME': '🇲🇪',
    'MK': '🇲🇰', 'BY': '🇧🇾', 'UA': '🇺🇦', 'GE': '🇬🇪', 'AM': '🇦🇲',
    'AZ': '🇦🇿', 'KZ': '🇰🇿', 'UZ': '🇺🇿', 'KG': '🇰🇬', 'TM': '🇹🇲',
    'TJ': '🇹🇯', 'MN': '🇲🇳', 'TW': '🇹🇼', 'HK': '🇭🇰', 'MO': '🇲🇴',
    'PH': '🇵🇭', 'MY': '🇲🇾', 'ID': '🇮🇩', 'TH': '🇹🇭', 'VN': '🇻🇳',
    'KH': '🇰🇭', 'LA': '🇱🇦', 'MM': '🇲🇲', 'BD': '🇧🇩', 'PK': '🇵🇰',
    'AF': '🇦🇫', 'IR': '🇮🇷', 'IQ': '🇮🇶', 'SA': '🇸🇦', 'AE': '🇦🇪',
    'QA': '🇶🇦', 'KW': '🇰🇼', 'BH': '🇧🇭', 'OM': '🇴🇲', 'YE': '🇾🇪',
    'JO': '🇯🇴', 'IL': '🇮🇱', 'LB': '🇱🇧', 'SY': '🇸🇾', 'TR': '🇹🇷',
    'EG': '🇪🇬', 'DZ': '🇩🇿', 'MA': '🇲🇦', 'TN': '🇹🇳', 'LY': '🇱🇾',
    'SD': '🇸🇩', 'ET': '🇪🇹', 'KE': '🇰🇪', 'TZ': '🇹🇿', 'UG': '🇺🇬',
    'ZA': '🇿🇦', 'NG': '🇳🇬', 'GH': '🇬🇭', 'CI': '🇨🇮', 'SN': '🇸🇳',
    'ML': '🇲🇱', 'BF': '🇧🇫', 'NE': '🇳🇪', 'TD': '🇹🇩', 'CM': '🇨🇲',
    'CF': '🇨🇫', 'GA': '🇬🇦', 'CD': '🇨🇩', 'AO': '🇦🇴', 'MZ': '🇲🇿',
    'ZM': '🇿🇲', 'ZW': '🇿🇼', 'MW': '🇲🇼', 'MG': '🇲🇬', 'MU': '🇲🇺',
    'SC': '🇸🇨', 'KM': '🇰🇲', 'DJ': '🇩🇯', 'ER': '🇪🇷'
}

# Generate 2050 servers
for i in range(1, 2051):
    country = countries[i % len(countries)]
    servers.append({
        'id': f"SRV-{str(i).zfill(4)}",
        'country': country,
        'flag': flags.get(country, '🌍'),
        'ip': f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
        'port': 3000 + (i % 7000),
        'latency': random.randint(30, 200)
    })

# ========== STATE ==========
current_index = 0
switch_count = 0
is_running = False
countdown = 30
lock = threading.Lock()

# ========== API ==========
@app.route('/')
def index():
    return jsonify({
        'name': 'VPN Rotator API',
        'version': '2.0',
        'servers': len(servers),
        'status': 'running'
    })

@app.route('/api/status')
def get_status():
    with lock:
        server = servers[current_index]
        return jsonify({
            'success': True,
            'server': server,
            'index': current_index,
            'total': len(servers),
            'switch_count': switch_count,
            'is_running': is_running,
            'countdown': countdown
        })

@app.route('/api/rotate')
def rotate():
    global current_index, switch_count
    with lock:
        current_index = (current_index + 1) % len(servers)
        switch_count += 1
        countdown = 30
        return jsonify({
            'success': True,
            'server': servers[current_index],
            'index': current_index,
            'switch_count': switch_count
        })

@app.route('/api/start')
def start():
    global is_running
    with lock:
        is_running = True
        return jsonify({'success': True, 'status': 'started'})

@app.route('/api/stop')
def stop():
    global is_running
    with lock:
        is_running = False
        return jsonify({'success': True, 'status': 'stopped'})

@app.route('/api/servers')
def get_servers():
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 50))
    with lock:
        return jsonify({
            'servers': servers[start:start+limit],
            'total': len(servers),
            'start': start,
            'limit': limit
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
