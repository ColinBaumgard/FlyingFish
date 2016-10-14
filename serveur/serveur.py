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



class Interface(Frame):

    def __init__(self, fenetre, **kwargs):

        self.fenetre = fenetre
        Frame.__init__(self, self.fenetre, **kwargs)

        self.nombreMessages = 0
        self.nombreConnectes = 0
        self.log = ''

        self.construire()
        self.getAndShowOutput()

        self.dicoTmpGetOuput = {}


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

        self.boxRun = Button(self.frameOption, text="Lancer", command=self.refreshInput)
        self.boxRun.grid(row=2, column=0, columnspan=2)

        # Frame INfo

        self.frameInfo = LabelFrame(self.fenetre, text="Info", padx=5, pady=5)
        self.frameInfo.grid(row=0, column=1)

        self.textCompteur = Label(self.frameInfo, text=": personnes connectés ")
        self.textCompteur.grid(row=0, column=1, sticky=W)
        self.boxCompteur = Label(self.frameInfo, text=self.nombreConnectes)
        self.boxCompteur.grid(row=0, column=0)

        self.textNbreMessages = Label(self.frameInfo, text=": messages envoyés ")
        self.textNbreMessages.grid(row=1, column=1, sticky=W)
        self.boxNbreMessages = Label(self.frameInfo, text=self.nombreMessages)
        self.boxNbreMessages.grid(row=1, column=0)

        self.textEtat = Label(self.frameInfo, text=": état du serveur")
        self.textEtat.grid(row=2, column=1, sticky=W)
        self.boxEtat = Label(self.frameInfo, text="Etat")
        self.boxEtat.grid(row=2, column=0)

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


    def refreshInput(self):

        inputQueue.put_nowait({'nom': self.boxName.get(), 'port': int(self.boxPort.get())})
        

    def getAndShowOutput(self):
        
        self.fenetre.after(100, self.getAndShowOutput)


        try:
            outputDico = outputQueue.get_nowait()
            for cle, valeur in outputDico.items():
                if(cle == 'nombreMessages'):
                    self.boxNbreMessages.config(text=valeur)
                    self.boxNbreMessages.grid()
                elif(cle == 'nombreConnectes'):
                    self.boxCompteur.config(text=valeur)
                    self.boxCompteur.grid()
                elif(cle == 'log'):
                    self.boxLog.config(state="normal")
                    self.boxLog.insert(END, '\n'+time.strftime("%H:%M:%S -> ")+valeur)
                    self.boxLog.config(state="disable")
                    self.boxLog.pack()
                elif(cle == 'etat'):
                    self.boxEtat.config(text=valeur)
                    self.boxEtat.grid()
                

        except:
            pass


class Server(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.quit = False
        self.running = False

        self.clientsListing = []
        self.numberMessages = 0

        outputQueue.put_nowait({'etat':'Prêt'})


    def run(self):

        while not self.quit:

            self.checkInputsGui()

            if self.running:

                self.checkNewClients()

                self.requestsReading()




    def checkInputsGui(self):

        try:
            inputsDico = inputQueue.get_nowait()
            port = inputsDico['port']
            #nom = inputsDico['nom']

            self.setConnexion(port)

        except:
            pass
            #outputQueue.put_nowait({'log':'Erreur: In Server class in checkInputsGui.'})

    def checkNewClients(self):

        connections_calls, wlist, xlist = select.select([self.main_connection], [], [], 0.05)

        try:

            for connection in connections_calls:
                connection_with_client, connection_infos = connection.accept()
                self.clientsListing.append(connection_with_client)

                connection_with_client.send(pickle.dumps(['text', 'Bienvenu !']))
                outputQueue.put_nowait({'nombreMessages': self.numberMessages})

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

                if type(request) == type([]):
                    if len(request) == 2:
                        outputQueue.put_nowait({'log': request[1]})
                        self.answerRequest(request)
                        isRequestFine = True

                if not isRequestFine:
                    outputQueue.put_nowait({'log':'Erreur : un client a envoyé un msg non conforme (requestsReading in Server class)'})




        except select.error:
            return []

    def answerRequest(self, request):

        if request[0] == 'text':
            self.send_to_all('text', request[1])

        else:
            outputQueue.put_nowait({'log':'Erreur: requête "'+request[0]+'" pas encore implémentée.'})


    def send_to_all(self, type, var):

        for client in self.clientsListing:

            try:
                client.send(pickle.dumps([type, var]))
                self.numberMessages += 1
                outputQueue.put_nowait({'nombreMessages':self.numberMessages})

            except:
                outputQueue.put_nowait({'log':"Erreur: l'envoie des messages à echoué. (send_to_all in Server class)"})


    def setConnexion(self, port, hote=''):



        self.main_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_connection.bind((hote, port))
        self.main_connection.listen(5)
        outputQueue.put_nowait({'log': "Le serveur est lancé sur le port {}".format(port)})


        self.running = True
        outputQueue.put_nowait({'etat': 'Activé'})


    def stop(self):

        self.quit = True

#definition fenetre

fenetre = Tk()
fenetre.title("Flying Fish")
fenetre.resizable(0,0)
interface = Interface(fenetre)


#definition modele

server = Server()
server.start()


#lancement des threads


fenetre.mainloop()


server.stop()
server.join()



