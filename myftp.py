# Help: https://www.eventhelix.com/networking/ftp/
# Help: https://www.eventhelix.com/networking/ftp/FTP_Port_21.pdf
# Help: https://realpython.com/python-sockets/
# Help: PASV mode may be easier in the long run. Active mode works 
# Reading: https://unix.stackexchange.com/questions/93566/ls-command-in-ftp-not-working
# Reading: https://stackoverflow.com/questions/14498331/what-should-be-the-ftp-response-to-pasv-command

# Import socket module
from socket import *
import sys # To terminate the program
import os

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

# Passive mode method
def modePASV(clientSocket):
    command = "PASV" + "\r\n"
    clientSocket.sendall(command.encode("utf-8"))
    data = clientSocket.recv(1024).decode("utf-8")
    print(data)

    start = data.find("(") + 1
    end = data.find(")")
    nums = data[start:end].split(",")

    ip = nums[0] + "." + nums[1] + "." + nums[2] + "." + nums[3]
    port = int(nums[4]) * 256 + int(nums[5])

    dataSocket = socket(AF_INET, SOCK_STREAM)
    dataSocket.connect((ip, port))
    return dataSocket

def handleLS(clientSocket):
    dataSocket = modePASV(clientSocket)
    reply = sendCommand(clientSocket, "LIST\r\n")
    print(reply)
    listing = dataSocket.recv(1024).decode("utf-8")
    print(listing)
    dataSocket.close()
    finalReply = receiveData(clientSocket)
    print(finalReply)

def handleCD(clientSocket, pathname):
    reply = sendCommand(clientSocket, "CWD " + pathname + "\r\n")
    print(reply)

def handleDelete(clientSocket, filename):
    reply = sendCommand(clientSocket, "DELE " + filename + "\r\n")
    print(reply)

def handleGet(clientSocket, filename):
    dataSocket = modePASV(clientSocket)
    reply = sendCommand(clientSocket, "RETR " + filename + "\r\n")
    print(reply)
    fileData = dataSocket.recv(1024)
    with open(filename, "wb") as file:
        file.write(fileData)
    print(f"File '{filename}' downloaded successfully.")
    dataSocket.close()
    finalReply = receiveData(clientSocket)
    print(finalReply)

def handlePut(clientSocket, filename):
    dataSocket = modePASV(clientSocket)
    reply = sendCommand(clientSocket, "STOR " + filename + "\r\n")
    print(reply)
    with open(filename, "rb") as file:
        fileData = file.read(1024)
        dataSocket.sendall(fileData)
    print(f"File '{filename}' uploaded successfully.")
    dataSocket.close()
    finalReply = receiveData(clientSocket)
    print(finalReply)

def main():
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((sys.argv[1], 21))
    print(receiveData(clientSocket))

    print(sendCommand(clientSocket, "USER " + input("Username: ") + "\r\n"))
    print(sendCommand(clientSocket, "PASS " + input("Password: ") + "\r\n"))

    while True:
        cmd = input("myftp> ").strip()
        
        if cmd == "ls" or cmd == "dir":
            handleLS(clientSocket)
        elif cmd.startswith("cd "):
            handleCD(clientSocket, cmd[3:].strip())
        elif cmd.startswith("delete "):
            handleDelete(clientSocket, cmd[7:].strip())
        elif cmd.startswith("get "):
            handleGet(clientSocket, cmd[4:].strip())
        elif cmd.startswith("put "):
            handlePut(clientSocket, cmd[4:].strip())
        elif cmd == "quit":
            break

    quitFTP(clientSocket)
    clientSocket.close()

main()
