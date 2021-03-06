# -*- coding: utf-8 -*-
import sqlite3
import datetime
from config import media_path, DEBUG
from logger import log


def execute_q(query,data=""):
    try:
        con = sqlite3.connect("naelo.db")
        cur = con.cursor()
    except sqlite3.Error as err:
        log(err.args)
        con.close()
        return 1
    try:
        r = cur.execute(query,data)
    except sqlite3.Error as err:
        log("DB error: "+err.args[0])
        log("Error Query:" + query + " ; " +str(data))
        con.close()
        return 1
    #if data != None:
    data = r.fetchall()
    con.commit()
    con.close()
    return data

def execute_many_q(querys,data):
    try:
        con = sqlite3.connect("naelo.db")
        cur = con.cursor()
    except sqlite3.Error as err:
        log(err.args)
        con.close()
        return 1
    try:
        r = cur.executemany(querys,data)
    except sqlite3.Error as err:
        log("DB error: "+err.args[0])
        log("Error Query:" + querys + " ; " +str(data))
        con.close()
        return 1
    #if data != None:
    data = r.fetchall()
    con.commit()
    con.close()
    return data



def create_db():
    query = ('CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
             'name TEXT NOT NULL, matrix_name TEXT, points INTEGER NOT NULL,'
             'created_by TEXT, created_at TEXT);')
    execute_q(query)

    query = ('CREATE TABLE IF NOT EXISTS games(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'
             'white_id INTEGER NOT NULL, black_id INTEGER NOT NULL, result REAL NOT NULL,'
             'comment TEXT, pictures TEXT, date TEXT NOT NULL, creator TEXT NOT NULL,'
             'removed INT DEFAULT 0, removed_by TEXT, removed_at TEXT);')
    execute_q(query)


def create_player(name,creator="system"):
    dt = datetime.datetime.now()
    if player_exists(name):
        return False
    else:
        query = 'INSERT INTO players(name,points,created_at, created_by) VALUES(?,1500,?,?);'
        execute_q(query,(name,dt,creator))
    return True


def player_exists(player):
    query = 'SELECT name from players;'
    players = execute_q(query)
    if player in [j for i in players for j in i]:
        return True
    else:
        return False


def check_add_game(white,black,result,creator,comment):
    #TODO check if players exists and if wants to validate

    if player_exists(white) and player_exists(black):
    #TODO ...if good:
        return add_game(white,black,result,creator,comment)
    else:
        return "fehler bei check_add_game()"


def calc_elo(w_elo,b_elo,result):
    #Erwartungswert Weiss:
    EwW = 1/ (1 + 10**((b_elo-w_elo)/400))
    #EwB = 1/ (1 + 10**((w_elo-b_elo)/400)) #brauch ich das?
    k = 36 #const factor
    w_change = k * (result-EwW)
    b_change = w_change *(-1)
    return round(w_change),round(b_change)


    #TODO make sure game is valid and verified.
def add_game(white,black,result,creator,comment=""):
    #Get creator:
    #query = ('SELECT id FROM players WHERE name = \"{}\"'.format(creator))
    #creator_id = execute_q(query)[0][0]
    #DEBUG: =1 until db stores Matrix Names and creator can match:
    #creator_id=1

    dt = datetime.datetime.now() #TODO  datetime sollte bei checkgame gemerkt werden und hier übernommen. -> DB
    #get Players Points from db
    query = 'SELECT id, points FROM players WHERE name = ?;'
    w_id, w_elo = execute_q(query,(white,))[0]
    b_id, b_elo = execute_q(query,(black,))[0]

    #Add Game
    query = ('INSERT INTO games(white_id,black_id,result,comment,date,creator) VALUES(?,?,?,?,?,?);')
    execute_q(query,(w_id,b_id,result,comment,dt,creator))

    #calc new elo
    w_chg,b_chg= calc_elo(w_elo,b_elo,result)
    new_w_elo = w_elo + w_chg
    new_b_elo = b_elo + b_chg

    set_elo(w_id,new_w_elo)
    set_elo(b_id,new_b_elo)
    return ("Punkte Änderung weiß: {0}  schwarz: {1}".format(w_chg,b_chg))


def set_elo(player_id,points):
    query = 'UPDATE players SET points = ? WHERE id = ?;'
    execute_q(query,(points,player_id))


def get_elolist():
    query = "SELECT name,points from players;"
    result = execute_q(query)
    result.sort(key=lambda t:t[1],reverse=True)
    text = "Wertung\n\n"

    i=1
    for e in result:
        text +=  "{0}. {1}  -  {2} Punkte\n".format(i,e[0],e[1])
        #html += "<tr> <td> {0}</td> <td>{1}</td> <td>{2}Punkte</td> <tr>".format(i,e[0],e[1])
        i+=1

    return text
    #return html+"</table></html>"


def get_games(number=5,player1=None,player2=None):
    # TODO make queries nicer
    games = []
    if player1 is None and player2 is None:
        query='SELECT white_id,black_id,result,date,id,comment from games WHERE removed = 0 OR removed is NULL ORDER BY date DESC LIMIT ?'
        games = execute_q(query,(number,))
    # P1
    elif player1 is not None and player2 is None:

        query = """SELECT white_id,black_id,result,date,id,comment from games WHERE
        (removed = 0 OR removed is NULL)
        	AND (
            white_id=(select id from players where name = '{0}')
        	OR black_id=(select id from players where name = '{0}')
            )
         ORDER BY date DESC LIMIT ?""".format(player1)
        games = execute_q(query,(number,))

    # P1+P2
    elif player1 is not None and player2 is not None:
        query = """
                    SELECT white_id, black_id, result,date,id,comment from games WHERE
            (removed = 0 OR removed is NULL)
            	AND (
            		white_id=(select id from players where name = '{0}')
            		OR black_id=(select id from players where name = '{0}')
            		)
            		AND (
            		white_id=(select id from players where name = '{1}')
            		OR black_id=(select id from players where name = '{1}')
            		)
            ORDER BY date DESC
            LIMIT ?
            """.format(player1,player2)
        games = execute_q(query,(number,))


    #query='SELECT white_id,black_id,result,date,id,comment from games WHERE removed = 0 OR removed is NULL ORDER BY date DESC LIMIT ?'
    #games = execute_q(query,(number,))

    #DEBUG:
    #print (games)

    players = dict(execute_q("SELECT id,name from players")) #BUG: Select only players in params! TODO

    result_list = []

    for g in games:
        w = players[g[0]]
        b = players[g[1]]
        g_result = g[2]
        date = g[3][:16]
        g_id = g[4]
        comment = g[5] if g[5] is not None else ""
        date = datetime.datetime.strptime(date,"%Y-%m-%d %H:%M")
        date = date.strftime("%d.%m.%Y - %H:%M")
        result_list.append('{0} gegen {1}   Ergebnis: {2} am {3} Uhr - {5} - [{4}]'.format(w,b,g_result,date,g_id,comment))

    return '\n'.join(result_list)


def rebuild_list():
    query='SELECT white_id,black_id,result,date from games WHERE removed = 0 OR removed is NULL ORDER BY date ASC'
    games = execute_q(query)
    players = execute_q("SELECT id,points,name from players")
    #playernames = {a:n for a,b,n in players}
    players = {a:1500 for a,b,n in players}
    for game in games:
        w = game[0]
        b = game[1]
        r = game[2]
        elo_w = players[w]
        elo_b = players[b]
        w_chg,b_chg = calc_elo(elo_w, elo_b, r)
        players[w] += w_chg
        players[b] += b_chg
    for i,p in players.items():
        set_elo(i,p)
    return players


def remove_game(game_id,sender="system",comment=""):
    dt = datetime.datetime.now()
    #TODO add comment to db
    query='UPDATE games SET removed = 1, removed_at=?, removed_by=? where id=?'
    execute_q(query,(dt,sender,game_id))
    rebuild_list()
    return True

def remove_player(player_id):
    query="SELECT id FROM games WHERE white_id=? OR black_id=?"
    games = execute_q(query,(player_id,player_id))
    for g in games:
        remove_game(g[0])
    #TODO REMOVE PLAYER
    #rebuild_list() #comment here in and out in remove_game

# ---- Picture Handling -------------------------------------------------------

class PictureHandler():
    def __init__(self):
        self.last_pic = ""

PH = PictureHandler()
# pic_list = [] # vorerst billige Lösung  mit einem Pic


def pic_to_db(fname,gamenr):
    pass

def pic_created(fname):
    PH.last_pic = fname
    log("pic created: " +PH.last_pic)

def pic_to_game(gamenr):
    pic = ""
    if PH.last_pic == "":
        return "Kein Bild vorhanden"
    else:
        pic = PH.last_pic

    # Wenn keine nr angegeben dann nimm letztes spiel
    if gamenr == None:
        gamenr = execute_q("SELECT MAX(id) FROM games;")[0][0]

    #why not?
    #query = "update games set pictures = (select IFNULL(pictures || ':0' || ',',':0' || ',') from games where id = :1) where id = :1" #why not?

    query = "update games set pictures = (select IFNULL(pictures || '{0}' || ',','{0}' || ',') from games where id = {1}) where id = {1}".format(pic,gamenr)
    execute_q(query)

    msg = "{0} zu Spiel {1} hinzugefügt.".format(pic,gamenr)
    log(msg)
    return msg


#if DEBUG:
#    PH.last_pic = "VectorImage_2018-06-23_030938.jpg"
#    pic_to_game(79)




