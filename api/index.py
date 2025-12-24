from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import random

app = Flask(__name__)
CORS(app)

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # These are the "Elite" clients that currently bypass the bot check
    # 'tv' and 'web_creator' are often less restricted
    STARK_CLIENTS = ['tv', 'web_creator', 'mweb']

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': [random.choice(STARK_CLIENTS)],
                'player_skip': ['webpage', 'configs', 'js'],
            }
        },
        # We use a very specific YouTube TV User-Agent
        'user_agent': 'Mozilla/5.0 (Chromecast; Google TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.225 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract the best direct link
            formats = info.get('formats', [])
            # Find a format that has both audio and video combined
            download_url = None
            for f in reversed(formats):
                if f.get('acodec') != 'none' and f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                    download_url = f.get('url')
                    break
            
            if not download_url:
                download_url = info.get('url')

            return jsonify({
                "title": info.get('title', 'Haxor Video'),
                "thumbnail": info.get('thumbnail'),
                "downloadUrl": download_url,
                "source": info.get('extractor_key')
            })
    except Exception as e:
        error_msg = str(e)
        # Detailed logging for your Terminal
        print(f"Bypass failed: {error_msg}")
        return jsonify({"error": "YouTube blocking detected. Trying to rotate IPs..."}), 403

# No handler needed, Vercel picks up 'app'
