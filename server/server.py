import socket
import struct
from timeit import default_timer as timer
import os
import pickle
#10.245.161.146
"""
Use this to send integers or floats directly. Takes care of packing them as bytes
"""
def sendIntorFloat(IntorFloat):
    if type(IntorFloat) == int: #determines whether param is int or float
        marker = '!i' #and passes result to struct.
    else:
        marker = '!f'
    buf = struct.pack(marker, IntorFloat) #packs float or int to bytes
    connection.sendall(buf) #sends bytes

"""
Returns integer or float received through socket. Parameter IorF should be passed
as a string consisting in '!i' for receiving integers and '!f' for receiving floats.
Takes care of unpacking bytes and returns float or int directly.
"""
def recvIntorFloat(IorF):
    received = 0 #initializing amount received as 0
    while received < 4: #int or floats are 4 bytes large
        buf = connection.recv(4) #receive data
        received += len(buf) #increase amount received
    IntorFloat = struct.unpack(IorF, buf)[0] #unpack bytes to int or float
    return IntorFloat #return int or float

"""
Returns a string received through socket as bytes. Parameter describing expected
size in bytes of string is necessary.
"""
def recvBytestoString(expectedAmount):
    received = 0 #initializing amount received as 0
    string = "" #initializing empty string
    while received < expectedAmount:
        buf = connection.recv(4) #receiving data
        string += buf.decode() #building string
        received += len(buf)
    return string

class Server():
    """
    -a Server, able to receive connections
    -Server has a "state", address and port attributes
    """
    def __init__(self, state, address, port):
        self.state = state
        self.address = address
        self.port = port

    """
    Accepts incoming connection on socket and returns connection
    object and client address
    """
    def connect(self):
        while True: #
            conn, c_address = sock.accept() #accept incoming connections
            print ("\nconnection from ", c_address) #diagnostics
            self.state = "connected" #set state to connected
            return conn, c_address #returns connection and client address to
            #be handled by rest of program


    """
    Handles the uploading of files from the Client to the Server.
    """
    def readwrite(self):
        while self.state == "upload":
            print("Ready to receive length of file name") #entering receipt loop for length of file name
            received = 0 #initalizing amount received to 0
            while received < 4: #length will be a 32 bit int, so 4 bytes
                buf = connection.recv(4)
                if len(buf) == 1: #special case where client pressed enter
                    print("\nUpload operation canceled by Client.\
                    \nReturning to prompt state.")
                    self.state = "connected" #change state
                    break #break out of receive loop
                received += len(buf) #increment received with amount received

            if self.state == "connected": #what to do when client cancels upload
                break #break out of readwrite and return to prompt state

            filenamelength = struct.unpack('!i', buf)[0] #unpack bytes object into int
            print("\nLength of file name received and processed. Ready to read file name")

            print("\nReading file name...") #receiving file name
            filename = recvBytestoString(filenamelength)

            #determining if filename is received correctly
            if len(filename) == filenamelength: #if expected and actual length match
                ack = 1 #then the filename received is correct
                result = "positive"
            else: #otherwise
                ack = 0 #then incorrect filename received
                result = "negative"
                print("Filename error, returning to prompt state, please try again")
                self.state = "connected"
                break

            #sending acknowledgement to client
            print("\nsending %s acknowledgement to client..." % result)
            sendIntorFloat(ack)

            size = recvIntorFloat('!i')
            print("\n%d byte file size received and processed, entering read loop" % size)

            received = 0 #entering read and writeloop for file itself
            upldfile = open("resources/" + filename, "wb") #creating new file with filename. Will write in bytes directly.
            t = timer() #begin timing the read and write process
            print("...reading...")
            while received < size:
                data = connection.recv(64)
                upldfile.write(data) #writing bytes
                received += len(data)
            print("...writing...")
            upldfile.close() #closing file when done
            print("\nClient Upload complete, returning to prompt state.")
            total = timer() - t #determining timing of upload
            sendIntorFloat(total) #sending timing of upload
            self.state = "connected" #changing state back to connected...exiting loop.

    def ls(self):
        print("gathering directory information...")
        lsresult = os.listdir("resources") #gets directory of resources folder
        print("processing directory information...") #to avoid considering "server.py"
        pickledlist = pickle.dumps(lsresult) #serializes list object into bytes object
        listsize = len(pickledlist) #determines size of list in bytes
        print("sending directory size and directory...")
        sendIntorFloat(listsize)
        connection.sendall(pickledlist) #sending list
        print("\nOperation completed, returning to prompt state.")
        self.state = "connected" #returning to prompt state


    def sendwrite(self):
        while self.state == "download":

            while True: #while true to allow client to try again in case of non existing file
                print("Ready to receive length of file name") #entering receipt loop for length of file name
                received = 0 #initalizing amount received to 0
                while received < 4: #length will be a 32 bit int, so 4 bytes
                    buf = connection.recv(4)
                    if len(buf) == 1: #special case where client pressed enter
                        print("\nDownload operation canceled by Client.\
                        \nReturning to prompt state.")
                        self.state = "connected" #change state
                        break #break out of receive loop
                    received += len(buf) #increment received with amount received

                if self.state == "connected": #what to do when client cancels donload
                    break #break out of While True loop. (will have to do this twice)

                filenamelength = struct.unpack('!i', buf)[0] #unpack bytes object into int
                print("\nLength of file name received and processed. Ready to read file name")

                print("\nReading file name...")
                filename = recvBytestoString(filenamelength) #receiving filename

                try: #checking if file is on server
                    f = open("resources/" + filename, "rb")
                    DWLDfile = f.read()
                    f.close()
                    filesize = len(DWLDfile) #if error not raised, compute filesize
                    sendIntorFloat(filesize)
                except FileNotFoundError as e:
                    print("File does not exist, letting user know and waiting for them to try again")
                    filesize = -1 #if file does not exist, send file size of -1
                    sendIntorFloat(filesize)
                    continue

                break

            if self.state == "connected": #what to do when client cancels donload
                break #break out of sendwrite() and return to prompt state

            print("\nFile found on server, sending File to client")
            connection.sendall(DWLDfile) #sends file
            print("\nClient download operation terminated, returning to prompt state.")
            self.state = "connected"

    def delete(self):
        while self.state == "delete":
            #receiving file name length and file name
            print("\nReceiving file name length and file name from client.")
            filenamelength = recvIntorFloat('!i')
            filename = recvBytestoString(filenamelength)

            #checking that file exists on server.
            print("\nVerifying that file exists on server and letting client know.")
            if os.path.isfile("resources/"+filename): #does exist
                ack = 1
                print("File exists")
                sendIntorFloat(ack)
            else: #doesn't exist
                ack = -1
                sendIntorFloat(ack)
                print("\nFile not present on server.\
                \nCanceling deletion process.\
                \nReturning to prompt state.")
                self.state = "connected" #canceling deletion operation
                break

            #awaiting and processing confirmation
            print("\nAwaiting confirmation from client before deletion")
            confirm = recvIntorFloat('!i') #delete?
            if confirm == 1: #Yes
                print("Positive confirmation.\
                \nFile deleted.\
                \nReturning to prompt state")
                os.remove("resources/"+filename) #deletes desired file
                #checking that file deleted

                if os.path.isfile("resources/"+filename): #if file still exists
                    sendIntorFloat(0) #sending failure of deletion
                else: #file no longer exists after deletion
                    sendIntorFloat(1) #sending confirmation of deletion

                self.state = "connected" #end of deletion process
                break

            else: #No
                print("\nDelete abandoned by the user!\
                \nReturning to prompt state.")
                self.state = "connected"
                break #canceling deletion operation



#Initiating server object in a "waiting for connections" state.
server = Server("ConnWait", "localhost", 10000)

while True: #while True to be able to continuously change state
    if server.state == "ConnWait":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creating socket object
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #to allow address to be reused
        server_address = (server.address, server.port) #defining server address and port
        sock.bind(server_address) #binding socket to server address
        sock.listen(1) #listening for incoming connections
        print("...Waiting for a connection...")
        connection, client_address = server.connect() #initiate connect() function

    if server.state == "connected": #"prompt" state
        print("\nWaiting for command from client")
        data = connection.recv(4096) #Receive command from client
        if data.decode() == "": #Result of client sending QUIT command
            print("\nClient ended session and disconnected from Server\n")
            connection.close() #clean up connection
            server.state = "ConnWait" #return to waiting for connection state
            #enter upload state, to handle files uploaded from client
        elif data.decode() == "UPLD":
            print("\nReceived upload command, initiating read mode.")
            server.state = "upload"
            #enter list state, to send client a list of server files
        elif data.decode() == "LIST":
            print("\nReceived list command, initiating list mode.")
            server.state = "list"
            #enter download state, to send files requested by client
        elif data.decode() == "DWLD":
            print("\nReceived download command, initiating write mode.")
            server.state = "download"
            #enter delete state, to delete file requested by client
        elif data.decode() == "DELF":
            print("\nReceived delete command, initiating delete mode.")
            server.state = "delete"

    if server.state == "upload": #perform readwrite if in this state
        server.readwrite() #when client uploads

    if server.state == "list": #perform ls if in this state
        server.ls()

    if server.state == "download": #perform sendwrite if in this state
        server.sendwrite() #when client downloads

    if server.state == "delete": #perform delete if in this state
        server.delete()
