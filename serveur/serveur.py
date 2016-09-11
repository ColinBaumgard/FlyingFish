#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from tkinter import *
import threading




class Interface(threading.Thread, Frame):

    def __init__(self, fenetre, **kwargs):
        threading.Thread.__init__(self)
        self.fenetre = fenetre
        Frame.__init__(self, self.fenetre, **kwargs)
        self.construire()



    def construire(self):

        #Frame Option

        self.frameOption = LabelFrame(self.fenetre, text="Options", padx=5, pady=5)
        self.frameOption.grid(row=0, column=0)

        self.textName = Label(self.frameOption, text="Nom: ")
        self.textName.grid(row=0, column=0)
        value = StringVar()
        value.set("Flying Fish")
        self.boxName= Entry(self.frameOption, textvariable=value)
        self.boxName.grid(row=0, column=1)

        self.textPort = Label(self.frameOption, text="Port: ")
        self.textPort.grid(row=1, column=0)
        value = StringVar()
        value.set("5050")
        self.boxPort = Spinbox(self.frameOption, from_=0, to=50000, textvariable=value)
        self.boxPort.grid(row=1, column=1)

        # Frame INfo

        self.frameInfo = LabelFrame(self.fenetre, text="Info", padx=5, pady=5)
        self.frameInfo.grid(row=0, column=1)

        self.textCompteur = Label(self.frameInfo, text="On est: ")
        self.textCompteur.grid(row=0, column=0)
        self.boxCompteur = Label(self.frameInfo)
        self.boxCompteur.grid(row=0, column=1)

        self.textNbreMessages = Label(self.frameInfo, text="Nombre de messages envoyés: ")
        self.textNbreMessages.grid(row=1, column=0)
        self.boxNbreMessages = Label(self.frameInfo)
        self.boxNbreMessages.grid(row=1, column=1)

        # Frame log

        self.frameLog = LabelFrame(self.fenetre, text="Log", padx=5, pady=5)
        self.frameLog.grid(row=1, column=0, rowspan=2, columnspan=2)

        self.boxLog = Text(self.frameLog, width="40", height="15")

        self.scrollbar1 = Scrollbar(self.frameLog)
        self.scrollbar1.config(command=self.boxLog.yview)
        self.boxLog.config(yscrollcommand=self.scrollbar1.set)
        self.scrollbar1.pack(side="right", fill="y")
        self.boxLog.pack(fill="both")
        self.boxLog.config(state="disabled")









fenetre = Tk()
fenetre.title("Flying Fish")
interface = Interface(fenetre)

interface.mainloop()
interface.destroy()