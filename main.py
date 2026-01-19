from flask import Flask, render_template, send_from_directory
from services import get_vpn_configs

app = Flask(__name__)

@app.route('/')
def home():
    configs = get_vpn_configs()
    return render_template('index.html', configs=configs)

@app.route('/LICENSE')
def serve_license():
    return send_from_directory('static', 'LICENSE')

if __name__ == '__main__':
    app.run(debug=True, port=5000)