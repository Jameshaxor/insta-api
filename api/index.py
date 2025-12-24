from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import random

app = Flask(__name__)
CORS(app)

# We use a variety of "Mobile" clients to confuse YouTube's bot detection
CLIENTS = ['ios', 'android', 'mweb']

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # These options are specifically tuned to bypass the "Bot" check
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        # This is the "Magic" part: telling yt-dlp to pretend to be different clients
        'extractor_args': {
            'youtube': {
                'player_client': [random.choice(CLIENTS)],
                'skip': ['webpage', 'hls', 'dash']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We use download=False because we only want the direct stream URL
            info = ydl.extract_info(url, download=False)
            
            # Find the best video+audio URL
            download_url = info.get('url')
            if not download_url:
                # Fallback for some formats
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        download_url = f.get('url')
                        break

            return jsonify({
                "title": info.get('title', 'Haxor Video'),
                "thumbnail": info.get('thumbnail'),
                "downloadUrl": download_url,
                "source": info.get('extractor_key')
            })
    except Exception as e:
        # If it still fails, we send the error back to your Terminal
        error_msg = str(e)
        if "Sign in" in error_msg:
            return jsonify({"error": "YouTube Bot Detection is high. Try again in 5 mins."}), 403
        return jsonify({"error": error_msg}), 500

# Required for Vercel
app.debug = False
