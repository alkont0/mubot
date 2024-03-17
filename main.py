from flask import Flask, jsonify, request
import yt_dlp
import pyshorteners
import os

app = Flask(__name__)
ydl_opts = {
    'quiet': True,
    'noplaylist': True
}

def scrape_music_from_yt(searchQuery):
    ydlp = yt_dlp.YoutubeDL(ydl_opts)
    
    try:
        with ydlp:
            result = ydlp.extract_info(
                f"ytsearch:{searchQuery}",
                download=False
            )
            
            if not result['entries']:
                return None  # No results found
            
            entry = result['entries'][0]
            formats = entry.get('formats', [])
            video_title = entry.get('title')
            thumbnail_url = entry.get('thumbnail')
            duration = entry.get('duration')
            minutes, seconds = divmod(duration, 60)

            for data in formats:
                if data.get('format_id') == '140':
                    url = data.get('url')
                    if url:
                        song = {
                            "url": url,
                            "duration": f"{minutes}m {seconds}s",
                            "song_name": video_title,
                            "thumbnail": thumbnail_url
                        }
                        return song
            return None  # Suitable format not found
    except Exception as e:
        print(f"Error: {e}")
        return None

def shorten_url(url):
    try:
        s = pyshorteners.Shortener()
        return s.isgd.short(url)
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return url  # Return the original URL in case of error

@app.route('/get_song', methods=['GET'])
def get_song():
    search_music = request.args.get('search_music')
    if not search_music:
        return jsonify({"error": "No search query provided"}), 400

    song = scrape_music_from_yt(search_music)
    
    if song:
        shortened_url = shorten_url(song['url'])
        return jsonify({
            "song_name": song['song_name'],
            "download_link": shortened_url,
            "duration": song['duration'],
            "thumbnail": song['thumbnail']
        })
    else:
        return jsonify({"error": "Song not found"}), 404
