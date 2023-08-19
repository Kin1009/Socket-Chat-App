import base64
import socket
from tkinter import Tk, Toplevel, filedialog, CENTER, DISABLED, NORMAL, END
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
import time
import threading
import os
class GUI:
    
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.Window = Tk()
        self.Window.withdraw()

        self.login = Toplevel()

        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=350)

        self.pls = Label(self.login, text="Please login to a chatroom", justify=CENTER)
        self.pls.grid(column=0, row=0, columnspan=2)
        Label(self.login, text="Server ID:").grid(column=0, row=1)
        self.serverID = Entry(self.login, show="*")
        self.serverID.grid(column=1, row=1)

        self.userLabelName = Label(self.login, text="Username:")
        self.userLabelName.grid(column=0, row=3)

        self.userEntryName = Entry(self.login)
        self.userEntryName.grid(column=1, row=3)
        self.userEntryName.focus()

        self.roomLabelName = Label(self.login, text="Room ID:")
        self.roomLabelName.grid(column=0, row=2)

        self.roomEntryName = Entry(self.login, show="*")
        self.roomEntryName.grid(column=1, row=2)
        
        self.go = Button(self.login,
                         width=30, 
                            text="Continue",
                            command = lambda: self.goAhead(self.serverID.get(), self.userEntryName.get(), self.roomEntryName.get()))
        
        self.go.grid(column=0, row=4, columnspan=2)

        self.Window.mainloop()
    def goAhead(self, server, username, room_id=0):
        server = base64.b64decode(server.encode()).decode()
        ip, port = server.split(":")
        self.server.connect((ip, int(port)))
        self.name = username
        self.server.send(str.encode(username))
        time.sleep(0.1)
        self.server.send(str.encode(room_id))
        
        self.login.destroy()
        self.layout()

        rcv = threading.Thread(daemon=True, target=self.receive) 
        rcv.start()

    def insert(self, text):
        self.fileLocation.config(state="normal")
        self.fileLocation.delete(0, END)
        self.fileLocation.insert(END, text)
        self.fileLocation.config(state="disabled")
    def layout(self):
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550)
        self.chatBoxHead = Label(self.Window, text = self.name)

        self.chatBoxHead.grid(column=0, row=0, columnspan=3)
		
        self.textCons = ScrolledText(self.Window, 
                                width=60, 
                                height=30,
                                font="Segoe 9") 
		
        self.textCons.grid(column=0, row=1, columnspan=3)
		
        self.entryMsg = Entry(self.Window, width=60)
        self.entryMsg.grid(column=0, row=2, columnspan=2)
        self.entryMsg.focus()

        self.buttonMsg = Button(self.Window, 
								text = "Send", 
								command = lambda : self.sendButton(self.entryMsg.get())) 
        self.buttonMsg.grid(column=2, row=2)
		
        self.fileLocation = Entry(self.Window, width=48)
        self.fileLocation.config(state="disabled")
        self.insert("Choose file to send")
        self.fileLocation.grid(column=0, row=3) 

        self.browse = Button(self.Window, text = "Browse", command = self.browseFile)
        self.browse.grid(column=1, row=3)

        self.sengFileBtn = Button(self.Window, 
								text = "Send", 
								command = self.sendFile)
        self.sengFileBtn.grid(column=2, row=3)
        self.textCons.config(state = DISABLED)


    def browseFile(self):
        self.filename = filedialog.askopenfilename(initialdir="/", 
                                    title="Select a file",
                                    filetypes = (("Text files", 
                                                "*.txt*"), 
                                                ("all files", 
                                                "*.*")))
        self.insert("File opened: "+ self.filename)


    def sendFile(self):
        try:
            self.server.send("FILE".encode())
            time.sleep(0.1)
            self.server.send(str("client_" + os.path.basename(self.filename)).encode())
            time.sleep(0.1)
            self.server.send(str(os.path.getsize(self.filename)).encode())
            time.sleep(0.1)
        except:
            pass

        file = open(self.filename, "rb")
        data = file.read(1024)
        while data:
            self.server.send(data)
            data = file.read(1024)
        self.textCons.config(state=DISABLED)
        self.textCons.config(state = NORMAL)
        self.textCons.insert(END, "<You> "
                                     + str(os.path.basename(self.filename)) 
                                     + " Sent\n\n")
        self.textCons.config(state = DISABLED) 
        self.textCons.see(END)


    def sendButton(self, msg):
        self.textCons.config(state = DISABLED) 
        self.msg=msg 
        self.entryMsg.delete(0, END) 
        snd= threading.Thread(daemon=True, target = self.sendMessage) 
        snd.start() 


    def receive(self):
        while True:
            try:
                message = self.server.recv(1024).decode()

                if str(message) == "FILE":
                    file_name = self.server.recv(1024).decode()
                    lenOfFile = self.server.recv(1024).decode()
                    send_user = self.server.recv(1024).decode()

                    if os.path.exists(file_name):
                        os.remove(file_name)

                    total = 0
                    with open(file_name, 'wb') as file:
                        while str(total) != lenOfFile:
                            data = self.server.recv(1024)
                            total = total + len(data)     
                            file.write(data)
                    
                    self.textCons.config(state=DISABLED)
                    self.textCons.config(state = NORMAL)
                    self.textCons.insert(END, "<" + str(send_user) + "> " + file_name + " Received\n\n")
                    self.textCons.config(state = DISABLED) 
                    self.textCons.see(END)

                else:
                        if message != "":
                            self.textCons.config(state=DISABLED)
                            self.textCons.config(state = NORMAL)
                            self.textCons.insert(END, 
                                            message+"\n\n") 

                            self.textCons.config(state = DISABLED) 
                            self.textCons.see(END)

            except: 
                print("An error occured!") 
                self.server.close() 
                break

    def sendMessage(self):
        self.textCons.config(state=DISABLED) 
        while True:  
            self.server.send(self.msg.encode())
            self.textCons.config(state = NORMAL)
            self.textCons.insert(END, 
                            "<You> " + self.msg + "\n\n") 

            self.textCons.config(state = DISABLED) 
            self.textCons.see(END)
            break



if __name__ == "__main__":
    g = GUI()
