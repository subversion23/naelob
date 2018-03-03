# -*- coding: utf-8 -*-

from matrix_python_sdk.matrix_client.api import MatrixHttpApi
from matrix_python_sdk.matrix_client.errors import MatrixRequestError, MatrixUnexpectedResponse
import time

user="naelob"
password="Ksj7fdkkdpPlmvldG"
room_id="!jxAOURaTtmgkNFnuSW:matrix.org"
base_url="https://matrix.org"

#==============================================================================
# api = MatrixHttpApi(base_url,token=None)
# api.validate_certificate(True)
# l_response = api.login("m.login.password", user=user, password=password)
# sync_token=l_response["access_token"]
# api.token = sync_token
# j_response = api.join_room(room_id)
#==============================================================================


#def sync(sync_token=None):
#    s_response = api.sync(sync_token)
#    sync_token = s_response["next_batch"]
#    return s_response


class NaelobClient():
    def __init__(self,base_url,user,password,room_id):
        api = MatrixHttpApi(base_url,token=None)
        api.validate_certificate(True)
        l_resp =api.login("m.login.password", user=user, password=password)
        self.access_token = l_resp["access_token"]
        api.token = self.access_token
        self.room = None
        self.connected = True
        self.sync_token = None
        self.api = api
        self.join_room(room_id)

    def join_room(self,room_id):
        j_resp = self.api.join_room(room_id)
        self.room = room_id
        return j_resp

    def sync(self,since=None):
        if since is not None:
            s_resp = self.api.sync(since)
        else:
            s_resp = self.api.sync(self.sync_token) #TODO filter=...

        self.sync_token = s_resp["next_batch"]
        return s_resp


    def send_text(self,text):
        msg = {"msgtype": "m.text",
               "body": text}
        timestamp = None
        return self.api.send_message_event(self.room,"m.room.message",
               msg,timestamp)

    def listen(self,callback):
        bRun = True
        if self.room is not None and self.connected:
            while bRun:
                msg = self._sync()
                callback(msg)
                time.sleep(2) #TODO track callbacktime

    def close(self):
        return self.api.logout()



def test_cb(msg):
    print (msg)

client = NaelobClient(base_url,user,password,room_id)


#api.logout()
