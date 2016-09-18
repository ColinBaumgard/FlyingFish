#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from tkinter import *
import threading
import time
import queue
import socket
import select
import pickle


outputQueue = queue.Queue()
inputQueue = queue.Queue()



class Interface(threading.Thread, Frame):

    def __init__(self, fenetre, **kwargs):
        threading.Thread.__init__(self)
        self.fenetre = fenetre
        Frame.__init__(self, self.fenetre, **kwargs)


        self.defaultport = StringVar()
        self.defaultport.set("5050")
        self.defaulthost = StringVar()
        self.defaulthost.set("127.0.0.1")
        self.defaultname = StringVar()
        self.defaultname.set('Newbie')

        self.construire()



    def construire(self):
        ##########################################
        ######### cadre de communication #########
        ##########################################


        self.cadreCommunication = Frame(self.fenetre)
        self.cadreCommunication.pack(side='bottom', fill="both", padx=5, pady=5)

        # cadre console avec scroll bar :
        self.cadreConsole = Frame(self.cadreCommunication)
        self.cadreConsole.pack(fill="both", padx=5, pady=5)

        self.console = Text(self.cadreConsole)

        self.scrollbar1 = Scrollbar(self.cadreConsole)
        self.scrollbar1.config(command=self.console.yview)
        self.console.config(yscrollcommand=self.scrollbar1.set)

        self.scrollbar1.pack(side="right", fill="y")
        self.console.pack(fill="both")
        # fin cadre console

        self.champ_commande = Entry(self.cadreCommunication)
        self.champ_commande.bind("<Return>", self.sendMessage)
        self.champ_commande.pack(padx=5, fill='x')

        ##########################################
        #########   Tableaud de bord     #########
        ##########################################


        # frame principale
        self.tbBord = LabelFrame(self.fenetre, text="Liste des serveurs", padx=15, pady=10)
        self.tbBord.pack(side="top", fill="both", padx=5, pady=5)

        # liste utilisateurm on lance un thread pour afficher la liste des users
        self.textPort = Label(self.tbBord, text="Port :")
        self.textPort.pack(side='left', padx=5)
        self.containerPort = Spinbox(self.tbBord, from_=0, to=50000, textvariable=self.defaultport)
        self.containerPort.pack(side='left', padx=5)

        self.textHost = Label(self.tbBord, text='Hôte :')
        self.textHost.pack(side='left', padx=5)
        self.containerHost = Entry(self.tbBord, textvariable=self.defaulthost)
        self.containerHost.pack(side='left', padx=5)

        self.textName = Label(self.tbBord, text='Nom :')
        self.textName.pack(side='left', padx=5)
        self.containerName = Entry(self.tbBord, textvariable=self.defaultname)
        self.containerName.pack(side='left', padx=5)

        self.textState = Label(self.tbBord, text='Etat de connexion:')
        self.textState.pack(side='left', padx=5)
        self.containerState = Label(self.tbBord, text='Déconnecté')
        self.containerState.pack(side='left', padx=5)

        self.startButton = Button(self.tbBord, text='Connecter', command=self.startButtonPressed)
        self.startButton.pack(side='right', padx=5)

    def startButtonPressed(self):

        inputQueue.put_nowait({'type':'cmd', 'host': self.containerHost.get(), 'port': int(self.containerPort.get()), 'name':self.containerName.get()})

    def sendMessage(self, event):

        outputQueue.put_nowait({'type':'text', 'var':'{}: {}'.format(self.containerName.get(), self.champ_commande.get())})
        blank= StringVar()
        blank.set("")
        self.champ_commande.config(textvariable=blank)

    def getAndShowOutput(self):

        self.fenetre.after(100, self.getAndShowOutput)

        try:
            outputDico = outputQueue.get_nowait()
            for cle, valeur in outputDico.items():
                if (cle == 'state'):
                    self.containerState.config(text=valeur)
                    self.containerState.pack(side='left', padx=5)

                elif cle == 'log':
                    self.log = '{}\n{}'.format(self.log, valeur)
                    self.console.config(text=self.log)
                    self.console.pack()

        except:
            pass




class client(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.quit = False
        self.running = False

        outputQueue.put_nowait({'state':'Déconnecté'})


    def run(self):

        while not self.quit:

            self.checkInputsGui()

            if self.running:

                self.requestsReading() #not changed yet from there




    def checkInputsGui(self):

        try:
            inputsDico = inputQueue.get_nowait()
            if inputsDico["type"] == 'cmd':
                port = inputsDico['port']
                name = inputsDico['name']
                host = inputsDico['host']

                self.setConnexion(port, host)

            elif inputsDico["type"] == 'text':
                text = inputsDico['var']
                self.send_to_server('text', text)


        except:
            pass
            #outputQueue.put_nowait({'log':'Erreur: In Server class in checkInputsGui.'})

    def checkNewClients(self):

        connections_calls, wlist, xlist = select.select([self.main_connection], [], [], 0.05)

        try:

            for connection in connections_calls:
                connection_with_client, connection_infos = connection.accept()
                self.clientsListing.append(connection_with_client)

                outputQueue.put_nowait({'nombreConnectes':len(self.clientsListing)})

        except:
            pass

    def requestsReading(self):

        to_read_clients = []
        try:
            to_read_clients, wlist, xlist = select.select(self.clientsListing, [], [], 0.05)

            for client in to_read_clients:

                request_binary = client.recv(1024)
                request = pickle.loads(request_binary)

                isRequestFine = False

                if isinstance(request, []):
                    if len(request) == 2:
                        self.answerRequest(request)
                        isRequestFine = True

                if not isRequestFine:
                    outputQueue.put_nowait({'log':'Erreur : un client a envoyé un msg non conforme (requestsReading in Server class)'})




        except select.error:
            return []

    def answerRequest(self, request):

        if request[0] == 'message':
            self.send_to_all(request[1])

        else:
            outputQueue.put_nowait({'log':'Erreur: requête "'+request[0]+'" pas encore implémentée.'})


    def send_to_server(self, type, var):

        for client in self.clientsListing:

            try:
                client.send(pickle.dumps([type, var]))
                outputQueue.put_nowait({'nombreMessages':self.numberMessages})

            except:
                outputQueue.put_nowait({'log':"Erreur: l'envoie des messages à echoué. (send_to_all in Server class)"})


    def setConnexion(self, port, hote=''):

        try:

            self.main_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.main_connection.connect((hote, port))
            outputQueue.put_nowait({'log': "Connexion établie".format(port)})


            self.running = True
            outputQueue.put_nowait({'state': 'Connecté'})

        except:
            pass


    def stop(self):

        self.quit = True




fenetre = Tk()
fenetre.title("Flying Fish")
fenetre.resizable(0,0)
interface = Interface(fenetre)



interface.mainloop()
