# naelob

matrix client bot with elo rating system for Nachtasyl-chess 


## Installation:  
Create a config.py in the path:  
```
user=""
password=""
room_id=""
```




## Help
```
!elo Weiß-Schwarz {0, 0.5, 1} [Kommentar] - 1 = Sieg weiß; 0 = Sieg schwarz; 0.5 Unentschieden

!stats, liste = ruft die aktuelle Rangliste ab

!addplayer <name>

!games [spieler1] - [spieler2] [anzahl] - gibt eine Liste der letzten 5 Spiele zurück

!delgame x  -löscht game x(nummer aus !games) und berechnet elo liste neu.
```
