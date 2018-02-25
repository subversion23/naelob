# -*- coding: utf-8 -*-
from matrix_python_sdk.matrix_client.client import MatrixClient
import db_helper
from logger import log
import time
from config import user,password,room_id


client = MatrixClient("https://matrix.org")
token = client.login_with_password(username=user, password=password)
myroom = client.join_room(room_id)

help_text=''' == H I L F E == \n
Partie eintragen:
!elo Weiß-Schwarz [0,0.5,1] 1 = Sieg weiß; 0 = Sieg schwarz; 0.5 Unentschieden

!elo stats, liste = ruft die aktuelle Rangliste ab

!elo addplayer <name> <aliases>

!elo games  - gibt eine Liste der letzten 5 Spiele zurück
'''

#TODO:
#    - log prio
#    - regex
#    - ext syntax for cmds: "!cmd x", addgame: "elo a-b x"
#    - event sender to DB
#    - addplayer can map to matrix_name + "!addme" cmd
#    - num games - remove game by num if sender is player or creator
#    - create new elo list from games history


def on_message(room,event):
    if event['type'] == "m.room.member":
        if event['membership'] == "join":
            log("{0} joined".format(event['content']['displayname']))
    elif event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            log("{0}: {1}".format(event['sender'], event['content']['body']))
            #parse here
            parse_msg(event['sender'],event['content']['body'])
    else:
        log(event['type'])

#TODO: super ql: eigener thread - weil hier listener o. db steht, oder?
def parse_msg(sender,msg):
    msg = msg.strip().lower()
    #msg: !elo W-B p
    if msg.startswith("!elo"):
        cmd = msg.replace("!elo","").strip()

        #Check for cmds
        #Regex?!! REGEX!!!!!!!!
        log("cmd:"+cmd)
        if "help" in cmd:
            myroom.send_text(help_text)
            return

        elif "stats" in cmd or "list" in cmd:
            liste = db_helper.get_elolist()
            myroom.send_text("{0}".format(liste))
            return

        elif "games" in cmd:
            myroom.send_text(db_helper.get_games())
            return

        elif cmd.startswith("addplayer"):
            playerdata = cmd.split(' ')
            name = playerdata[1]
            aliases = ""
            if len(playerdata) > 2:
                aliases = playerdata[2]

            if db_helper.create_player(name,aliases,sender):
                myroom.send_text("Neuen Spieler {} erstellt.".format(name))
            else:
                myroom.send_text("Fehler beim erstellen von neuen Spieler {}.".format(name))
            return

        #cmd = new game TODO: Error handling!
        elif cmd == "":
            myroom.send_text("JA?")

        else:
            try:
                wb,result = cmd.strip().split(" ")
                white, black = wb.split("-")
            except ValueError:
                myroom.send_text("Fehler!")
                return

            log(wb+" "+result)
            msg_result = "Partie {0} (weiß)  gegen {1} (schwarz): ".format(white,black)

            if result == "1":
                msg_result += "{} gewinnt.".format(white)
                result = 1
            elif result == "0":
                msg_result += "{} gewinnt.".format(black)
                result = 0
            elif result == "0.5" or result == "0,5":
                result = 0.5
                msg_result += "Unentschieden."
            else:
                #Wrong Result
                myroom.send_text("Fehler: Falsches Ergebnis!")
                return

            #TODO cast result to float
            add_result = db_helper.check_add_game(white,black,result,sender)

            myroom.send_text(msg_result+"\n"+add_result)

def listenhandler(err):
    log(err.msg)

myroom.send_text("Naelob returns!")
myroom.add_listener(on_message)

try:
    client.start_listener_thread(exception_handler=listenhandler)
except Exception as e:
    print("Aha! "+ e.args)

try:
    get_input = raw_input
except NameError:
    get_input = input

#====== MAIN LOOP: ==========
bRun = True
while bRun:
    msg = get_input()
    #TEST
    #time.sleep(0.5)
    if msg == "/quit":
        bRun=False
    #else:
    #    myroom.send_text(msg)

client.stop_listener_thread()
myroom.send_text("Naelob verabschiedet sich und geht offline.")
print ("und aus")
client.logout()


