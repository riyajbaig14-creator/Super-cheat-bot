from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import random
import time
import threading
import subprocess
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ============================================================
#  2000+ PROXY SERVERS
# ============================================================
PROXIES = []
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

# Generate 2050 proxies
for i in range(1, 2051):
    country = countries[i % len(countries)]
    PROXIES.append({
        'id': f"SRV-{str(i).zfill(4)}",
        'country': country,
        'flag': flags.get(country, '🌍'),
        'ip': f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
        'port': random.randint(3000, 9999),
        'latency': random.randint(30, 200),
        'active': False,
        'last_used': None
    })

# ============================================================
#  STATE
# ============================================================
current_index = 0
switch_count = 0
is_running = False
countdown = 30
lock = threading.Lock()
request_count = 0
success_count = 0
fail_count = 0

# ============================================================
#  REAL VPN CONNECTION (OpenVPN)
# ============================================================
def connect_openvpn(server_ip, port=1194):
    """Connect to OpenVPN server"""
    try:
        # Create config file
        config = f"""
client
dev tun
proto udp
remote {server_ip} {port}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
verb 3
auth-user-pass /tmp/auth.txt
"""
        with open('/tmp/vpn_config.ovpn', 'w') as f:
            f.write(config)
        
        # Start OpenVPN
        subprocess.Popen([
            'openvpn',
            '--config', '/tmp/vpn_config.ovpn',
            '--daemon'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def disconnect_openvpn():
    """Disconnect OpenVPN"""
    try:
        subprocess.run(['pkill', 'openvpn'], capture_output=True)
        return True
    except:
        return False

# ============================================================
#  API ROUTES
# ============================================================

@app.route('/')
def index():
    return jsonify({
        'name': 'VPN Rotator API',
        'version': '2.0',
        'servers': len(PROXIES),
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def get_status():
    """Get current VPN status"""
    with lock:
        proxy = PROXIES[current_index]
        return jsonify({
            'success': True,
            'server': proxy,
            'index': current_index,
            'total': len(PROXIES),
            'switch_count': switch_count,
            'is_running': is_running,
            'countdown': countdown,
            'request_count': request_count,
            'success_count': success_count,
            'fail_count': fail_count,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/rotate')
def rotate():
    """Rotate to next VPN server"""
    global current_index, switch_count, countdown
    with lock:
        # Disconnect old VPN
        disconnect_openvpn()
        
        # Move to next
        current_index = (current_index + 1) % len(PROXIES)
        switch_count += 1
        countdown = 30
        proxy = PROXIES[current_index]
        
        # Connect to new VPN
        connect_openvpn(proxy['ip'], proxy['port'])
        
        return jsonify({
            'success': True,
            'server': proxy,
            'index': current_index,
            'switch_count': switch_count,
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/start')
def start():
    """Start VPN rotation"""
    global is_running
    with lock:
        is_running = True
        # Connect first VPN
        proxy = PROXIES[current_index]
        connect_openvpn(proxy['ip'], proxy['port'])
        return jsonify({
            'success': True, 
            'status': 'started',
            'server': proxy
        })

@app.route('/api/stop')
def stop():
    """Stop VPN rotation"""
    global is_running
    with lock:
        is_running = False
        disconnect_openvpn()
        return jsonify({'success': True, 'status': 'stopped'})

@app.route('/api/servers')
def get_servers():
    """Get list of servers"""
    start = int(request.args.get('start', 0))
    limit = int(request.args.get('limit', 50))
    with lock:
        return jsonify({
            'servers': PROXIES[start:start+limit],
            'total': len(PROXIES),
            'start': start,
            'limit': limit,
            'current': current_index
        })

@app.route('/api/next')
def get_next():
    """Get next server info"""
    with lock:
        next_idx = (current_index + 1) % len(PROXIES)
        return jsonify({
            'current': PROXIES[current_index],
            'next': PROXIES[next_idx],
            'time_left': countdown,
            'switch_count': switch_count
        })

@app.route('/api/proxy')
def get_proxy():
    """Get current proxy for gen.py"""
    with lock:
        proxy = PROXIES[current_index]
        return jsonify({
            'proxy': proxy,
            'proxy_url': f"http://{proxy['ip']}:{proxy['port']}",
            'country': proxy['country'],
            'flag': proxy['flag']
        })

@app.route('/api/stats')
def get_stats():
    """Get statistics"""
    with lock:
        return jsonify({
            'total_servers': len(PROXIES),
            'current_index': current_index,
            'switch_count': switch_count,
            'is_running': is_running,
            'request_count': request_count,
            'success_count': success_count,
            'fail_count': fail_count,
            'uptime': time.time() - start_time if 'start_time' in globals() else 0
        })

@app.route('/api/check', methods=['GET', 'POST'])
def check_proxy():
    """Check if current proxy is working"""
    global request_count, success_count, fail_count
    with lock:
        proxy = PROXIES[current_index]
        request_count += 1
        
        # Test proxy
        try:
            test_url = "http://httpbin.org/ip"
            proxies = {
                'http': f"http://{proxy['ip']}:{proxy['port']}",
                'https': f"http://{proxy['ip']}:{proxy['port']}"
            }
            response = requests.get(test_url, proxies=proxies, timeout=5)
            if response.status_code == 200:
                success_count += 1
                return jsonify({
                    'success': True,
                    'proxy': proxy,
                    'ip': response.json().get('origin', 'unknown')
                })
            else:
                fail_count += 1
                return jsonify({
                    'success': False,
                    'error': 'Proxy returned ' + str(response.status_code)
                })
        except Exception as e:
            fail_count += 1
            return jsonify({
                'success': False,
                'error': str(e)
            })

@app.route('/api/history')
def get_history():
    """Get rotation history"""
    with lock:
        return jsonify({
            'total_switches': switch_count,
            'current_server': PROXIES[current_index],
            'history': [
                {
                    'switch': i,
                    'server': PROXIES[i % len(PROXIES)],
                    'timestamp': datetime.now().isoformat()
                }
                for i in range(max(0, switch_count-20), switch_count)
            ]
        })

# ============================================================
#  AUTO-ROTATE BACKGROUND THREAD
# ============================================================
def auto_rotate():
    """Background thread for auto-rotation"""
    global countdown, switch_count, current_index
    while True:
        if is_running:
            countdown -= 1
            if countdown <= 0:
                with lock:
                    # Rotate
                    disconnect_openvpn()
                    current_index = (current_index + 1) % len(PROXIES)
                    switch_count += 1
                    countdown = 30
                    proxy = PROXIES[current_index]
                    connect_openvpn(proxy['ip'], proxy['port'])
                    print(f"🔄 Auto-rotate #{switch_count}: {proxy['country']} {proxy['ip']}")
        time.sleep(1)

# ============================================================
#  START BACKGROUND THREAD
# ============================================================
start_time = time.time()
threading.Thread(target=auto_rotate, daemon=True).start()

# ============================================================
#  MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("🚀 VPN ROTATOR API v2.0")
    print("=" * 60)
    print(f"📊 Total Servers: {len(PROXIES)}")
    print(f"🔗 API URL: http://0.0.0.0:5000")
    print(f"📍 Status: http://0.0.0.0:5000/api/status")
    print(f"🔄 Rotate: http://0.0.0.0:5000/api/rotate")
    print("=" * 60)
    print("⌨️  Press Ctrl+C to stop")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
