from google.cloud import storage
import re
import json
import time

client = storage.Client()
song_bucket = client.bucket("cs131_song_bucket")
leaderboard_bucket = client.bucket("cs131_leaderboard_bucket")

#functions for everything lyric based:
#normalizes song lyrics from database
def normalize(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

#grabs song lyrics from DB, used for calculating final score
def get_song_lyrics(song_id: str):
    blob = song_bucket.blob(f"{song_id}.txt")
    raw = blob.download_as_text()
    return normalize(raw)

#grabs raw lyrics for display on edge device
def get_song_lyrics_raw(song_id: str) -> str:
    blob = song_bucket.blob(f"{song_id}.txt")
    return blob.download_as_text()


def list_songs() -> list:
    blobs = song_bucket.list_blobs()
    names = {blob.name for blob in blobs}
    song_ids = set()
    for name in names:
        if name.endswith(".txt"):
            song_id = name[:-4]
    return sorted(song_ids)


#function to save score to buckets 
def save_score(player_id: str, score: str, song_id: str):
    entry = {
        "player_id": player_id,
        "song_id": song_id,
        "score": score,
        "timestamp": int(time.time()),
    }
    blob_name = f"{song_id}/{player_id}_{entry['timestamp']}.json"
    blob = leaderboard_bucket.blob(blob_name)
    blob.upload_from_string(json.dumps(entry), content_type="application/json")