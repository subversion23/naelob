# -*- coding: utf-8 -*-
import datetime

def log(msg):
    now = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")
    print (now + ": "+msg)


