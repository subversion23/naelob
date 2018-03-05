# -*- coding: utf-8 -*-
#from matrix_python_sdk.matrix_client.client import MatrixClient
from my_matrix_client import NaelobClient
import db_helper
from logger import log
import re
from config import user,password,room_id


client =NaelobClient("https://matrix.org",user,password,room_id)

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

def on_message(text,sender):
    log(text)
    text = text.strip().lower() #TODO comments NOT
    #msg: !elo W-B p
    if text.startswith("!elo"):
        cmd = text.replace("!elo","").lstrip()
        parse_cmd(sender,cmd)
    elif text.startswith("!"):
        cmd = text.replace("!","").lstrip()
        parse_cmd(sender,cmd)


def parse_cmd(sender,cmd):
        #Check for cmds
        #r" *!elo (?P<white>) ?- ?(?P<black>) ","!elo a-b 1 bla bla"
        log("cmd:"+cmd)

        if cmd.startswith("quit"):
            client.send_text("baba")
            client.close()
            return

        elif cmd.startswith("help"): # in cmd:
            client.send_text(help_text)
            return

        elif cmd.startswith("stats") or cmd.startswith("list"):
            liste = db_helper.get_elolist()
            client.send_text("{0}".format(liste))
            #myroom.send_html(liste)
            return

        elif cmd.startswith("games"):
            client.send_text(db_helper.get_games())
            return

        elif cmd.startswith("addplayer"):
            playerdata = cmd.split(' ')
            name = playerdata[1]

            if db_helper.create_player(name,sender):
                client.send_text("Neuen Spieler {} erstellt.".format(name))
            else:
                client.send_text("Fehler beim erstellen von neuen Spieler {}.".format(name))
            return

        elif cmd.startswith("delgame"):
            try:
                cmds = cmd.split()
                g_id = cmds[1]
                comment = "[del:"+cmd[2] + "]"
            except ValueError:
                client.send_text("Fehler bei cmd parse")
            if (db_helper.remove_game(g_id,sender)):
                client.send_text("Spiel {0} aus der Wertung entfernt.".format(g_id))

        #cmd = new game TODO: Error handling!
        elif cmd == "":
            client.send_text("JA?")
        else: #cmd Processing:
            #(?P<white>) ?- ?(?P<black>)
            p = re.compile("(?P<white>\w+) *- *(?P<black>\w+) +(?P<result>\S{1,3}) *(?P<comment>.*$)")
            m = p.search(cmd)
            if m == None:
                client.send_text("Fehler in cmd parse")
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
                client.send_text("Fehler: Falsches Ergebnis!")
                return

            add_result = db_helper.check_add_game(white,black,result,sender,comment)
            if add_result.startswith("fehler"):
                client.send_text(add_result)
            else:
                client.send_text(msg_result+"\n"+add_result)


client.send_text("Naelob returns!")
client.start_listener(on_message)



