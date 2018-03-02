# -*- coding: utf-8 -*-
from matrix_python_sdk.matrix_client.client import MatrixClient
import db_helper
from logger import log
import re
from config import user,password,room_id


client = MatrixClient("https://matrix.org")
token = client.login_with_password(username=user, password=password)
myroom = client.join_room(room_id)

help_text=''' == H I L F E == \n
Partie eintragen:
!elo Weiß-Schwarz {0, 0.5, 1} [Kommentar] - 1 = Sieg weiß; 0 = Sieg schwarz; 0.5 Unentschieden

!stats, liste = ruft die aktuelle Rangliste ab

!addplayer <name>

!games  - gibt eine Liste der letzten 5 Spiele zurück

!delgame x  -löscht game x(nummer aus !games) und berechnet elo liste neu.

'''

#TODO:
#    - log prio
#    - addplayer can map to matrix_name + "!addme" cmd
#    - comments: @mom. in games. --> put to own table ?

#class myroom():
#    def send_text(text):
#        print(text)

def on_message(room,event):
    if event['type'] == "m.room.member":
        if event['membership'] == "join":
            log("{0} joined".format(event['content']['displayname']))
    elif event['type'] == "m.room.message":
        if event['content']['msgtype'] == "m.text":
            log("{0}: {1}".format(event['sender'], event['content']['body']))
            #parse here
            msg = event['content']['body']
            sender = event['sender']
            log(msg)
            msg = msg.strip().lower() #TODO comments NOT
            #msg: !elo W-B p
            if msg.startswith("!elo"):
                cmd = msg.replace("!elo","").lstrip()
                parse_cmd(sender,cmd)
            elif msg.startswith("!"):
                cmd = msg.replace("!","").lstrip()
                parse_cmd(sender,cmd)
    else:
        log(event['type'])

def parse_cmd(sender,cmd):
        #Check for cmds
        #r" *!elo (?P<white>) ?- ?(?P<black>) ","!elo a-b 1 bla bla"
        log("cmd:"+cmd)
        if  cmd.startswith("help"): # in cmd:
            myroom.send_text(help_text)
            return

        elif cmd.startswith("stats") or cmd.startswith("list"):
            liste = db_helper.get_elolist()
            myroom.send_text("{0}".format(liste))
            #myroom.send_html(liste)
            return

        elif cmd.startswith("games"):
            myroom.send_text(db_helper.get_games())
            return

        elif cmd.startswith("addplayer"):
            playerdata = cmd.split(' ')
            name = playerdata[1]

            if db_helper.create_player(name,sender):
                myroom.send_text("Neuen Spieler {} erstellt.".format(name))
            else:
                myroom.send_text("Fehler beim erstellen von neuen Spieler {}.".format(name))
            return

        elif cmd.startswith("delgame"):
            try:
                cmds = cmd.split()
                g_id = cmds[1]
                comment = "[del:"+cmd[2] + "]"
            except ValueError:
                myroom.send_text("Fehler bei cmd parse")
            if (db_helper.remove_game(g_id,sender)):
                myroom.send_text("Spiel {0} aus der Wertung entfernt.".format(g_id))

        #cmd = new game TODO: Error handling!
        elif cmd == "":
            myroom.send_text("JA?")
        else: #cmd Processing:
            #(?P<white>) ?- ?(?P<black>)
            p = re.compile("(?P<white>\w+) *- *(?P<black>\w+) +(?P<result>\S{1,3}) *(?P<comment>.*$)")
            m = p.search(cmd)
            if m == None:
                myroom.send_text("Fehler in cmd parse")
                log("Fehler in cmd parse. cmd:" + cmd)
                return
            else:
                white,black,result,comment = m.groups()

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
            add_result = db_helper.check_add_game(white,black,result,sender,comment)
            if add_result.startswith("fehler"):
                myroom.send_text(add_result)
            else:
                myroom.send_text(msg_result+"\n"+add_result)

def listenhandler(err):
    log("error aus listenhandler:" +str(err.args))

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


