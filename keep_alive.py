from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Telegram Bot Status</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                }
                .status {
                    background: rgba(255,255,255,0.2);
                    padding: 20px;
                    border-radius: 10px;
                    margin-top: 20px;
                }
                h1 {
                    font-size: 48px;
                    margin-bottom: 10px;
                }
            </style>
        </head>
        <body>
            <h1>🤖 Telegram Bot</h1>
            <div class='status'>
                <h2>✅ Бот работает!</h2>
                <p>Версия: 1.0</p>
                <p>Статус: Active</p>
                <p>Сервер: Render.com</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return 'OK', 200

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
