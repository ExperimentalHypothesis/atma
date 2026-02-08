from flask import current_app as app
from flask import render_template, Response, stream_with_context
import time
import os
import json
from config import Config

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/channel1.pls")
def channel1_pls():
    pls_content = """[playlist]
NumberOfEntries=1
File1=http://173.212.246.158:7778/channel1
Title1=Atma FM - Channel 1 (Ambient, Atmospheric, Experimental)
Length1=-1
Version=2
"""
    return Response(pls_content, mimetype="audio/x-scpls", headers={
        "Content-Disposition": "attachment; filename=atma-fm-channel1.pls"
    })

@app.route("/channel2.pls")
def channel2_pls():
    pls_content = """[playlist]
NumberOfEntries=1
File1=http://173.212.246.158:7778/channel2
Title1=Atma FM - Channel 2 (Dark Ambient, Industrial, Gothic)
Length1=-1
Version=2
"""
    return Response(pls_content, mimetype="audio/x-scpls", headers={
        "Content-Disposition": "attachment; filename=atma-fm-channel2.pls"
    })

@app.route("/channel1.m3u")
def channel1_m3u():
    m3u_content = """#EXTM3U
#EXTINF:-1,Atma FM - Channel 1 (Ambient, Atmospheric, Experimental)
http://173.212.246.158:7778/channel1
"""
    return Response(m3u_content, mimetype="audio/x-mpegurl", headers={
        "Content-Disposition": "attachment; filename=atma-fm-channel1.m3u"
    })

@app.route("/channel2.m3u")
def channel2_m3u():
    m3u_content = """#EXTM3U
#EXTINF:-1,Atma FM - Channel 2 (Dark Ambient, Industrial, Gothic)
http://173.212.246.158:7778/channel2
"""
    return Response(m3u_content, mimetype="audio/x-mpegurl", headers={
        "Content-Disposition": "attachment; filename=atma-fm-channel2.m3u"
    })

def get_current_song(channel_num):
    """Get current song from cue file"""
    try:
        cue_file = Config.ICES_CUE_CHANNEL1 if channel_num == 1 else Config.ICES_CUE_CHANNEL2
        with open(cue_file, "r") as f:
            lines = [line.strip() for line in f.readlines()]
            if len(lines) >= 2:
                artist = lines[-2].lower()
                album = lines[-1].lower()
                return {"artist": artist, "album": album}
    except Exception as e:
        app.logger.error(f"Error reading cue file: {e}")
    return {"artist": "unknown artist", "album": "unknown song"}

@app.route("/api/events/channel<int:channel_num>")
def stream_events(channel_num):
    """SSE endpoint for real-time updates"""
    if channel_num not in [1, 2]:
        return Response("Invalid channel", status=404)

    def generate():
        last_song = None
        while True:
            try:
                current_song = get_current_song(channel_num)
                song_id = f"{current_song['artist']}|{current_song['album']}"

                # Only send event if song changed
                if song_id != last_song:
                    last_song = song_id
                    data = json.dumps({
                        "type": "nowplaying",
                        "channel": channel_num,
                        "artist": current_song["artist"],
                        "album": current_song["album"]
                    })
                    yield f"data: {data}\n\n"

                time.sleep(5)  # Check every 5 seconds
            except GeneratorExit:
                break
            except Exception as e:
                app.logger.error(f"SSE error: {e}")
                time.sleep(5)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )