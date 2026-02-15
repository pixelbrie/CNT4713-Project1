# Help: https://www.eventhelix.com/networking/ftp/
# Help: https://www.eventhelix.com/networking/ftp/FTP_Port_21.pdf
# Help: https://realpython.com/python-sockets/
# Help: PASV mode may be easier in the long run. Active mode works 
# Reading: https://unix.stackexchange.com/questions/93566/ls-command-in-ftp-not-working
# Reading: https://stackoverflow.com/questions/14498331/what-should-be-the-ftp-response-to-pasv-command

#import socket module
from socket import *
import sys # In order to terminate the program

def quitFTP(clientSocket):
    # COMPLETE
    command = "QUIT\r\n"
    dataOut = command.encode("utf-8")
    clientSocket.sendall(dataOut)
    dataIn = clientSocket.recv(1024)
    data = dataIn.decode("utf-8")
    print(data)

def sendCommand(socket, command):
    dataOut = command.encode("utf-8")
    # Complete
    socket.sendall(dataOut)
    dataIn = socket.recv(1024)
    data = dataIn.decode("utf-8")
    return data

def receiveData(clientSocket):
    dataIn = clientSocket.recv(1024)
    data = dataIn.decode("utf-8")
    return data

# If you use passive mode you may want to use this method but you have to complete it
# You will not be penalized if you don't
def modePASV(clientSocket):
    command = "PASV" + "\r\n"
    # Complete
    clientSocket.sendall(command.encode("utf-8"))
    data = clientSocket.recv(1024).decode("utf-8")
    print(data)

    status = 0
    dataSocket = None

    if data.startswith("227"):
        status = 227
        # Complete
        start = data.find("(") + 1
        end = data.find(")")
        nums = data[start:end].split(",")

        ip = nums[0] + "." + nums[1] + "." + nums[2] + "." + nums[3]
        port = int(nums[4]) * 256 + int(nums[5])

        dataSocket = socket(AF_INET, SOCK_STREAM)
        dataSocket.connect((ip, port))

    return status, dataSocket

def main():
    # COMPLETE

    # client should be started by: python myftp.py server-name
    if len(sys.argv) != 2:
        print("Usage: python myftp.py <server>")
        sys.exit()

    username = input("Enter the username: ")
    password = input("Enter the password: ")

    clientSocket = socket(AF_INET, SOCK_STREAM) # TCP socket
    # COMPLETE

    HOST = sys.argv[1]  # COMPLETE
    PORT = 21           # COMPLETE
    clientSocket.connect((HOST, PORT))  # COMPLETE

    dataIn = receiveData(clientSocket)
    print(dataIn)

    status = 0

    # --- LOGIN SECTION (your teammate can adjust this if needed) ---
    if dataIn.startswith("220"):
        status = 220
        print("Sending username")
        # COMPLETE
        dataIn = sendCommand(clientSocket, "USER " + username + "\r\n")
        print(dataIn)

        print("Sending password")
        if dataIn.startswith("331"):
            status = 331
            # COMPLETE
            dataIn = sendCommand(clientSocket, "PASS " + password + "\r\n")
            print(dataIn)

            if dataIn.startswith("230"):
                status = 230

    # --- AFTER LOGIN: COMMAND LOOP (ls/dir + cd + quit) ---
    if status == 230:
        # It is your choice whether to use ACTIVE or PASV mode. In any event:
        # COMPLETE
        while True:
            userCmd = input("myftp> ").strip()

            # LIST: Used to ask the server to send back a list of all the files in the current remote directory.
            # The list of files is sent over a (new and non-persistent) data connection rather than the control TCP connection.
            if userCmd == "ls" or userCmd == "dir":
                pasvStatus, dataSocket = modePASV(clientSocket)
                if pasvStatus == 227:
                    # COMPLETE
                    reply = sendCommand(clientSocket, "LIST\r\n")
                    print(reply)

                    listing = dataSocket.recv(1024).decode("utf-8")
                    print(listing)

                    dataSocket.close()

                    finalReply = receiveData(clientSocket)
                    print(finalReply)

            # CWD pathname: Used to change the working directory on the server.
            elif userCmd.startswith("cd "):
                pathname = userCmd[3:].strip()
                # COMPLETE
                reply = sendCommand(clientSocket, "CWD " + pathname + "\r\n")
                print(reply)

            # QUIT: end session
            elif userCmd == "quit":
                break

            else:
                print("Unknown command (use ls/dir, cd <path>, quit)")

    print("Disconnecting...")

    quitFTP(clientSocket)
    clientSocket.close()

    sys.exit() #Terminate the program after sending the corresponding data

main()
