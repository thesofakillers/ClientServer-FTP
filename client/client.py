import socket
import struct
import os
import pickle
from timeit import default_timer as timer

"""
Use this to let the server know that the operation has been canceled.
This is done by sennding 1 character to the server, when the server expects
an int. The server receives 1 byte rather than the expected 4, and therefore
knows that the Client has canceled the operation.
"""
def cancelOp(emptyString):
    emptyString += "q" #adds character to empty string (usually result of enter key)
    sock.sendall(emptyString.encode()) #sends 1 byte string (i.e. a char)

"""
Use this to send integers directly. Takes care of packing them as bytes
"""
def sendInt(intgr):
    buf = struct.pack('!i', intgr) #packs integer as bytes object
    sock.sendall(buf) #sends bytes object

"""
Returns integer or float received through socket. Parameter IorF should be passed
as a string consisting in '!i' for receiving integers and '!f' for receiving floats.
Takes care of unpacking bytes and returns float or int directly.
"""
def recvIntorFloat(IorF):
    received = 0 #initializing amount received as 0
    while received < 4: #int or floats are 4 bytes large
        buf = sock.recv(4) #receive data
        received += len(buf) #increase amount received
    IntorFloat = struct.unpack(IorF, buf)[0] #unpack bytes to int or float
    return IntorFloat #return int or float

"""
Receives and deserializes a serialized object received as bytes through the TCP stream.
Parameter passed is the expected size of the object.
"""
def recvSerializedObject(expectedAmount):
    received = 0 #initializing amount received as 0
    bytestream = bytearray() #initializing empty bytearray received as 0
    while received < expectedAmount:
        buf = sock.recv(4) #receiving
        bytestream += buf #appending received bytes to bytestream
        received += len(buf) #counting amount of received bytes
    #deserializing bytestream
    result = pickle.loads(bytestream)
    return result #returning deserialized object

class Client():
    """
    -a Client, able to connect to a Server
    -Client has a "state" attribute
    """

    def __init__(self, state):
        self.state = state

    """
    Attempts connection to a server and handles case where server is not present.
    Once connected, client state will change "prompt" and provide user with
    other commands.
    """
    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket object
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #to allow address to be reused
        server_address = ('localhost', 10000) #defining server properties
        print('\n...attempting to connect to %s via port %s...' \
        %server_address)

        try: #try/except because server may not be running
            sock.connect(server_address) #attempts connection to server address
            print("\nConnection succesful on %s via port %s!\n"\
             %server_address)
            self.state = "prompt" #changing state to move on
            return sock #returns sock so that the rest of the script can handle it
        except Exception as e: #handles the case when server is not running
             print("\nConnection to server failed.\
             \nEnsure that server.py is running before attempting to connect\n")

    """
    Asks user what file they wish to upload and uploads it to Server.
    Handles non-existing files, allows user to cancel upload, and
    provides information on upload time.
    """
    def upload(self):
        while self.state == "uploading":
            sock.sendall(command.encode()) #sends Upload Command to server

            while True: #Asks user to enter the name of the file.
                filename = input("\nEnter the name of the file you wish to upload.\
                \nPress enter to cancel upload.\
                \nFile name: ")

                if filename == "": #If user presses enter
                    self.state = "prompt" #change state to prompt
                    break #break out of loop

                else:
                    try: #try/except to handle invalid filenames
                        f = open(filename, "rb")
                        upldfile = f.read() #reads the bytes directly
                        f.close()

                    except FileNotFoundError as e: #handles the error
                        print("\nFile not found. (Ensure to include the extension!)")
                        continue #Allows user to try again.
                break #breaks once try is succesful

            if self.state == "prompt":
                cancelOp(filename) #cancels operation
                print("\nUpload operation terminated, returning to prompt state\n")
                break #breaks out of loop and hence out of upload()

            #otherwise
            print("\nSending file name information to server")
            #pack and send integer file name and length info as bytes
            sendInt(len(filename.encode())) #filename length
            sock.sendall(filename.encode()) #send filename

            ack = recvIntorFloat('!i') #receiving acknowledgement
            #processing acknowledgement
            if ack == 1: #if positive
                print("\nFile name read by server with success.\
                \nCommencing upload...") #all good to upload

                print("\nSending file size to server") #sending file size
                size = os.stat(filename).st_size #gets file size
                sendInt(size) #sends file size

                sock.sendall(upldfile) #sending file

                print("\nWaiting for server response") #time information
                time = recvIntorFloat('!f') #receiving time float
                print("\n%s bytes uploaded in %f seconds\n" % (size, time))

                self.state = "prompt" #changing state to prompt, ending upload()

            else: #negative ackknowldgement
                print("\nFile name issue on Server Side, please try again")

    def ls(self):
        sock.sendall(command.encode()) #sending LIST command over to server
        listsize = recvIntorFloat('!i') #receiving list size
        lsresult = recvSerializedObject(listsize) #receiving list itself
        #displaying information to user
        print("\nHere are the files/directories present in the server:\n")
        for i in lsresult:
            print(i)
        print ("")
        #returning to prompt state
        self.state = "prompt"

    def download(self):
        while self.state == "downloading":
            sock.sendall(command.encode())

            while True: #Asks user to enter the name of the file.
                filename = input("\nEnter the name of the file you wish to download.\
                \nPress enter to cancel download.\
                \nFile name: ")

                if filename == "": #If user presses enter
                    self.state = "prompt" #change state to prompt to avoid reentering loop
                    break #break out of file name input loop.

                else:
                    filenamelength = len(filename.encode()) #determining length of file name
                    sendInt(filenamelength) #sending it to server
                    sock.sendall(filename.encode()) #sending the actual file name

                    filesize = recvIntorFloat('!i') #receiving file size

                    if filesize > 0:
                        print("File present on server.\
                        \nCommencing download")
                        break
                    elif filesize < 0:
                        print("\nFile not present on server, please try again.")

            if self.state == "prompt":
                cancelOp(filename) #cancels operation
                print("\nDownload operation terminated, returning to prompt state\n")
                break #breaks out of loop and hence out of download()

            received = 0 #entering read and write loop for file itself
            DWLDfile = open(filename, "wb") #creating new file with filename. Will write in bytes directly.
            t = timer() #begin timing the read and write process
            print("...reading...")
            while received < filesize:
                data = sock.recv(64)
                DWLDfile.write(data) #writing bytes
                received += len(data)
            print("...writing...")
            DWLDfile.close() #closing file when done
            total = timer() - t #ending timing of upload
            print("\n%s bytes download successfully completed in %f seconds.\
            \nReturning to prompt state.\n" % (filesize, total))
            self.state = "prompt"

    def delete(self):
        while self.state == "deleting": #while loop so that I can break from this state at different moments
            sock.sendall(command.encode()) #sending DELF command
            #asking user for file name
            filename = input("\nEnter the name of the file you wish to delete: ")
            #sending file name information
            sendInt(len(filename.encode()))
            sock.sendall(filename.encode())
            #Determining whethere requested file exists on server.
            ack = recvIntorFloat('i') #Receiving pos or neg ack
            if ack == -1: #negative
                print("\nThe file does not exist on server.")
                print("Returning to prompt state.\n")
                self.state = "prompt" #cancel delete process and return to prompt
                break
            else: #positive
                #proceed: Ask for user to confirm their delete request
                yesno = input("\nAre you sure you want to delete the file %s?\
                \nType 'Yes' or 'No': " % filename)
                while yesno != 'Yes' or yesno != "No": #to let the user retry if they mistype yes or no
                    if yesno == 'Yes':
                        sendInt(1) # 1 if Yes (safer to send int than string)
                        ack = recvIntorFloat('!i') #receive deletion confirmation
                        if ack == 1: #positive deletion
                            print("\n%s deleted succesfully on Server.\
                            \nReturning to prompt state.\n" % filename)
                            self.state = "prompt" #deletion process ends here
                            break
                        else: #failure to delete
                            print("\nFailed to delete %s on Server.\
                            \Returning to prompt state." % filename)
                            self.state = "prompt" #cancel deletion
                            break #return to prompt
                    elif yesno == 'No':
                        sendInt(0) #0 if no
                        print("\nDelete  abandoned by the user!\
                        \nReturning to prompt state.\n")
                        self.state = "prompt" #canceling delete process
                        break #return to prompt

                    else: #Let the user retry in case they mispell yes or no
                        yesno = input("Invalid response, Type 'Yes' or 'No': ")

    """
    Is utilized only when the client is currently connected to the server.
    Here, the QUIT command merely disconnects the client by closing the socket
    Resulting state is "disconnected" - the script still runs, allowing
    for reconnection
    """
    def quit(self):
        print("\nclosing socket...\n")
        sock.close() #closes socket
        self.state = "disconnected"

#initializing disconnected client
client = Client("disconnected")

while True: #while True to be able to continuously change state
    if client.state == "disconnected":
        val_cmds = ["CONN", "QUIT"] #when disconnected client can only connect or quit entirely
        command = input("You are currently not connected to the server.\
        \n-Type \"CONN\" to send a request to connect to the server.\
        \n-Type \"QUIT\" to close the program.\
        \nPlease enter your desired command: ")

        if (command in val_cmds) == False: #handles invalid command
            print("\nInvalid Command, please try again\n")

        elif command == "QUIT":
            break #breaks out of loop and ends script

        else: #i.e. if command == CONN
            sock = client.connect() #connect!

    try:
        if client.state == "prompt": #resulting state of connecting
            val_cmds = ["QUIT", "UPLD", "LIST", "DWLD", "DELF"]
            command = input("you are currently connected to the server\
            \n-Type \"QUIT\" to end your session with the server\
            \n-Type \"UPLD\" to initiate a sequence for uploading a file to the server.\
            \n-Type \"LIST\" to list the directory of the server\
            \n-Type \"DWLD\" to initiate a sequence for downloading a file from the server.\
            \n-Type \"DELF\" to initate a sequence for deleting a file from the server.\
            \nPlease enter your desired command: ")

            if (command in val_cmds) == False: #handles invalid command
                print("\nInvalid Command, please try again\n")

            elif command == "QUIT":
                client.quit() #disconnects from the server.

            elif command == "UPLD":
                client.state = "uploading" #changes state to uploading

            elif command == "LIST":
                client.state = "listing" #changes state to listing

            elif command == "DWLD":
                client.state = "downloading" #changes state to downloading

            elif command == "DELF":
                client.state = "deleting" #changes state to deleting

        if client.state == "uploading":
            client.upload() #enters uploading sequence

        if client.state == "listing":
            client.ls() #enters listing sequence

        if client.state == "downloading":
            client.download() #enters downloadng sequence

        if client.state == "deleting":
            client.delete() #enters deleting sequence

    except BrokenPipeError as e: #In case server.py drops the connection.
        print("\nOperation failed: Server has suddenly stopped.\n")
        client.state = "disconnected"
