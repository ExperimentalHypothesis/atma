 import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    FLASK_ENV = os.environ.get("FLASK_ENV")

    # Icecast/Ices paths configuration
    # These can be overridden via environment variables
    ICECAST_PLAYLIST_LOG = os.environ.get("ICECAST_PLAYLIST_LOG", "/etc/icecast2/log/playlist.log")
    ICES_CUE_CHANNEL1 = os.environ.get("ICES_CUE_CHANNEL1", "/etc/ices/log/channel1/ices.cue")
    ICES_CUE_CHANNEL2 = os.environ.get("ICES_CUE_CHANNEL2", "/etc/ices/log/channel2/ices.cue")

    # Audio directories - use home directory by default
    HOME_DIR = os.path.expanduser("~")
    AUDIO_DIR_CHANNEL1 = os.environ.get("AUDIO_DIR_CHANNEL1", os.path.join(HOME_DIR, "audio/channel1"))
    AUDIO_DIR_CHANNEL2 = os.environ.get("AUDIO_DIR_CHANNEL2", os.path.join(HOME_DIR, "audio/channel2"))
