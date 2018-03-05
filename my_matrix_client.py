# -*- coding: utf-8 -*-

from matrix_python_sdk.matrix_client.api import MatrixHttpApi
from matrix_python_sdk.matrix_client.errors import MatrixRequestError, MatrixUnexpectedResponse
import time
import logger

#TODO:
# Exceptions!
#

#sync_filter="{'room': {type': {'timeline': { 'events': {'content':'m.room.message'}}}}}"

class NaelobClient():
    def __init__(self,base_url,user,password,room_id):
        api = MatrixHttpApi(base_url,token=None)
        api.validate_certificate(True)
        l_resp =api.login("m.login.password", user=user, password=password)
        self.access_token = l_resp["access_token"]
        api.token = self.access_token
        self.room = room_id
        self.sync_token = None
        self.api = api
        self.api.join_room(room_id)
        self.room = room_id
        self._sync()
        self.connected = True
        self.bListen = False


    def _sync(self):
        if self.sync_token is None:
            s_resp = self.api.sync()
        else:
            s_resp = self.api.sync(self.sync_token) #TODO filter=..
        self.sync_token = s_resp["next_batch"]
        return s_resp

    def start_listener(self,callback):
        self.bListen = True
        if self.room is not None and self.connected:
            while self.bListen:
                try:
                    msg = self._sync()
                except Exception as e:
                    print(e)
                try: #PreParse
                    events = msg['rooms']['join'][self.room]['timeline']['events']
                    self._parse_events(events,callback)
                except KeyError:
                    pass
                time.sleep(2) #TODO track callbacktime

    def _parse_events(self,events,callback):
        for e in events:
            text = None
            sender = None
            try:
                if e['type'] == 'm.room.message':
                    text=e['content']['body']
                    sender=e['sender']
            except KeyError:
                pass
            if sender is not None and text is not None:
                callback(text,sender)

    def send_text(self,text):
        if self.connected:
            msg = {"msgtype": "m.text",
                   "body": text}
            timestamp = None
            return self.api.send_message_event(self.room,"m.room.message",
                   msg,timestamp)

    def close(self):
        self.bListen = False
        time.sleep(5)
        return self.api.logout()

