from flask import Flask, render_template
from services import get_vpn_configs

# Указываем static_folder='media', чтобы сохранить пути /media/... как в оригинале
app = Flask(__name__, static_folder='media', static_url_path='/media')

@app.route('/')
def home():
    configs = get_vpn_configs()
    return render_template('index.html', configs=configs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)