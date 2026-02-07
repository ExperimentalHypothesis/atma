import os
import pprint
from flask import request, abort
from flask_restful import Resource
from application import api
from config import Config

from marshmallow import Schema, fields


class Artists(Resource):
    """
    GET endpoint looking like this:
        - api/artists => return all artists for both channels
        - api/artists/channel1 => return all artists played on channel1
        - api/artists/channel2 => return all artists played on channel2
    """

    def get(self, channel=None):
        ret = {}
        if channel == None:
            ret["channel1"] = sorted(os.listdir(Config.AUDIO_DIR_CHANNEL1))
            ret["channel2"] = sorted(os.listdir(Config.AUDIO_DIR_CHANNEL2))
            return ret, 200
        elif channel == "channel1":
            ret["channel1"] = sorted(os.listdir(Config.AUDIO_DIR_CHANNEL1))
            return ret, 200
        elif channel == "channel2":
            ret["channel2"] = sorted(os.listdir(Config.AUDIO_DIR_CHANNEL2))
            return ret, 200

api.add_resource(Artists, "/artists", "/artists/<channel>", endpoint="artists")
