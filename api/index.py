from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import random
import time

app = Flask(__name__)
CORS(app)

# A list of real mobile devices to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8 Build/UD1A.230805.019) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36'
]

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # The "Ghost" strategy: Randomize everything for every request
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': random.choice(USER_AGENTS),
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Connection': 'keep-alive',
        },
        # This tells yt-dlp to stop "screaming" and start "whispering"
        'socket_timeout': 10,
        'extractor_args': {
            'instagram': {
                'check_hashtags': False,
            }
        }
    }

    try:
        # Add a tiny "human" delay (0.5 to 1.5 seconds)
        time.sleep(random.uniform(0.5, 1.5))
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                "title": info.get('title', 'Haxor Video'),
                "thumbnail": info.get('thumbnail'),
                "downloadUrl": info.get('url'),
                "source": info.get('extractor_key')
            })
    except Exception as e:
        error_msg = str(e)
        # If we see the "403" or "429" error, we rotate the message
        if "429" in error_msg or "403" in error_msg:
            return jsonify({"error": "IP Cooldown: Instagram is watching. Try again in 60s."}), 403
        return jsonify({"error": "Bypass failed. Meta is blocking this IP range."}), 403

# Vercel entry
# IP Rotation 1 
