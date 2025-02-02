from flask import Flask, render_template, request
import requests
import random
import json
import os

app = Flask(__name__)

STATS_FILE = "stats.json"
VISITOR_LOG_FILE = "visitor_logs.txt"

def load_stats():
    """Load meme count from stats.json, create file if missing."""
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'w') as f:
            json.dump({"totalcount": 0}, f)

    with open(STATS_FILE, 'r') as f:
        return json.load(f)

def save_stats(stats):
    """Save meme count to stats.json."""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=4)

def log_visitor_ip(ip):
    """Log visitor IP addresses in a file."""
    with open(VISITOR_LOG_FILE, 'a') as f:
        f.write(f"{ip}\n")

def get_meme():
    """Fetch a meme from the API, ensuring it's not NSFW, and update stats."""
    sr = "memes"
    url = f"https://meme-api.com/gimme/{sr}"

    for _ in range(5):  # Retry up to 5 times
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if not data.get("nsfw", False):  # Skip NSFW memes
                stats = load_stats()
                stats["totalcount"] += 1  # Increment meme count
                save_stats(stats)
                return data.get("url", get_local_meme())

        except requests.exceptions.RequestException as e:
            print(f"Error fetching meme: {e}")

    return get_local_meme()  # Fallback if all API attempts fail

def get_local_meme():
    """Retrieve a random meme URL from a local file."""
    try:
        with open('reddit_media_logs.txt', 'r') as f:
            memes = [line.strip() for line in f.readlines() if line.strip()]

        if memes:
            return random.choice(memes)
        else:
            return "https://i.imgur.com/J5LVHEL.jpg"  # Default meme if empty

    except FileNotFoundError:
        return "https://i.imgur.com/J5LVHEL.jpg"  # Default meme if missing

@app.route('/')
def index():
    """Render the meme page, log IP, and show a safe meme."""
    visitor_ip = request.remote_addr
    log_visitor_ip(visitor_ip)
    
    meme_pic = get_meme()
    return render_template('meme_index.html', meme_pic=meme_pic)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
