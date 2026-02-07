from flask import current_app as app
from flask import render_template, Response

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