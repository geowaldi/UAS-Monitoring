from flask import Flask, render_template, request, jsonify
import requests
import socket
import ssl
from datetime import datetime

app = Flask(__name__)

# Rute utama untuk menampilkan halaman web (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Tambahkan ini di app.py Anda
@app.route('/loadtest')
def load_test():
    # Loop ini akan memakan banyak CPU untuk sementara
    for i in range(10000000):
        _ = i * i
    return "Load test complete!"


# API untuk pengecekan status uptime
@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    url = data.get('url', '')
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    try:
        response = requests.get(url, timeout=5)
        return jsonify({'url': url, 'status': 'UP', 'status_code': response.status_code})
    except requests.exceptions.RequestException as e:
        return jsonify({'url': url, 'status': 'DOWN', 'error': 'Connection timed out or failed'})

# API untuk Pengecekan Port
@app.route('/check_ports', methods=['POST'])
def check_ports():
    data = request.get_json()
    host = data.get('host', '')
    common_ports = {21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 8080: "HTTP-Alt"}
    results = []
    try:
        ip = socket.gethostbyname(host)
        for port, service in common_ports.items():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result_code = sock.connect_ex((ip, port))
                status = "OPEN" if result_code == 0 else "CLOSED"
                results.append({'port': port, 'service': service, 'status': status})
        return jsonify({'host': host, 'ip': ip, 'ports': results})
    except socket.gaierror:
        return jsonify({'error': f'Could not resolve host: {host}', 'host': host, 'ip': 'N/A'})

# API untuk Pengecekan Header Keamanan
@app.route('/check_headers', methods=['POST'])
def check_headers():
    data = request.get_json()
    url = data.get('url', '')
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    try:
        response = requests.get(url, timeout=5)
        ip = socket.gethostbyname(response.url.split('/')[2].split(':')[0])
        headers_to_check = ['Content-Security-Policy', 'Strict-Transport-Security', 'X-Content-Type-Options', 'X-Frame-Options', 'Referrer-Policy', 'Permissions-Policy']
        found_headers = {h: response.headers.get(h) for h in headers_to_check if response.headers.get(h)}
        return jsonify({'url': url, 'ip': ip, 'headers': found_headers})
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Failed to fetch headers', 'url': url, 'ip': 'N/A'})

# API BARU: Pengecekan Sertifikat SSL
@app.route('/check_ssl', methods=['POST'])
def check_ssl():
    data = request.get_json()
    host = data.get('host', '')
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                
        # Parse expiration date
        expire_date_str = cert['notAfter']
        expire_date = datetime.strptime(expire_date_str, '%b %d %H:%M:%S %Y %Z')
        days_remaining = (expire_date - datetime.now()).days
        
        # Parse issuer
        issuer = dict(x[0] for x in cert['issuer'])
        
        return jsonify({
            'host': host,
            'issuer': issuer.get('organizationName', 'Unknown'),
            'expires_in': f"{days_remaining} hari",
            'days_remaining': days_remaining
        })
    except Exception as e:
        return jsonify({'error': 'Could not retrieve SSL certificate.', 'host': host})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)