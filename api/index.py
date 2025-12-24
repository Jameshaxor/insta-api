from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import random
import time
import re

app = Flask(__name__)
CORS(app)

# The most "Trusted" User Agents in the current bypass meta
APEX_IDENTITIES = [
    {
        'ua': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'clients': ['web', 'mweb']
    },
    {
        'ua': 'com.google.android.youtube/19.01.33 (Linux; U; Android 14; en_US; Pixel 8 Pro; Build/UD1A.231105.004; Cronet/121.0.6167.71)',
        'clients': ['android', 'tv']
    },
    {
        'ua': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'clients': ['ios', 'mweb']
    }
]

def clean_url(url):
    """Strips tracking IDs that trigger bot detection."""
    return re.sub(r'(\?|&)(igsh|utm|s|feature|app_id)=[^&]+', '', url)

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    raw_url = data.get('url')
    if not raw_url:
        return jsonify({"error": "Target URL missing"}), 400

    target_url = clean_url(raw_url)
    
    # Attempt 3-Stage Breach
    for attempt in range(3):
        identity = random.choice(APEX_IDENTITIES)
        
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': identity['ua'],
            'socket_timeout': 15,
            'retries': 2,
            # Extractor-specific logic to confuse the target
            'extractor_args': {
                'youtube': {
                    'player_client': identity['clients'],
                    'player_skip': ['webpage', 'configs', 'js'],
                },
                'instagram': {
                    'check_hashtags': False,
                    'include_dash_manifest': False,
                }
            },
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
            }
        }

        # Add Referer based on platform
        if "instagram.com" in target_url:
            ydl_opts['http_headers']['Referer'] = 'https://www.instagram.com/'
        elif "facebook.com" in target_url:
            ydl_opts['http_headers']['Referer'] = 'https://www.facebook.com/'
        else:
            ydl_opts['http_headers']['Referer'] = 'https://www.google.com/'

        try:
            # Random "Human" wait time
            time.sleep(random.uniform(1.2, 2.5))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Force-extract basic info first
                info = ydl.extract_info(target_url, download=False)
                
                # Logic to find the realest download link
                download_url = info.get('url')
                if not download_url:
                    # Scan for direct MP4 links in the formats array
                    formats = info.get('formats', [])
                    for f in reversed(formats):
                        if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                            download_url = f.get('url')
                            break
                
                if download_url:
                    return jsonify({
                        "title": info.get('title', 'Apex Secured Video'),
                        "thumbnail": info.get('thumbnail'),
                        "downloadUrl": download_url,
                        "source": info.get('extractor_key'),
                        "identity_used": identity['clients'][0]
                    })
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            # If we're on the last attempt, return a detailed failure
            if attempt == 2:
                return jsonify({
                    "error": "Access Denied. All bypass identities compromised.",
                    "details": "Target server has initiated a hard block. Try again in 5 minutes."
                }), 403
            # If not last attempt, wait a bit and loop again
            time.sleep(1)
            continue

# Entry point for Vercel Serverless
