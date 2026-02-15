# Help: https://www.eventhelix.com/networking/ftp/
# Help: https://www.eventhelix.com/networking/ftp/FTP_Port_21.pdf
# Help: https://realpython.com/python-sockets/
# Help: PASV mode may be easier in the long run. Active mode works 
# Reading: https://unix.stackexchange.com/questions/93566/ls-command-in-ftp-not-working
# Reading: https://stackoverflow.com/questions/14498331/what-should-be-the-ftp-response-to-pasv-command

# Import socket module
from socket import *
import sys # To terminate the program

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

    username = input("Enter the username: ")
    password = input("Enter the password: ")

    clientSocket = socket(AF_INET, SOCK_STREAM) # TCP socket
    # COMPLETE

    HOST = sys.argv[1] # COMPLETE
    PORT = 21 # COMPLETE
    clientSocket.connect((HOST, PORT)) # COMPLETE

    dataIn = receiveData(clientSocket)
    print(dataIn)

    status = 0
    if dataIn.startswith("220"):
        status = 220
        # Send 'user'
        reply = sendCommand(clientSocket, "USER " + username + "\r\n")
        print(reply)
        if reply.startswith("331"):
            # Send 'pass'
            reply = sendCommand(clientSocket, "PASS " + password + "\r\n")
            print(reply)
            if reply.startswith("230"):
                status = 230
                print("Login successful.")
            else:
                print("Login failed.")

    if status == 230:
        # COMPLETE
        while True:
            userCmd = input("myftp> ").strip()

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

            elif userCmd.startswith("cd "):
                pathname = userCmd[3:].strip()
                # COMPLETE
                reply = sendCommand(clientSocket, "CWD " + pathname + "\r\n")
                print(reply)

            
            # RETR
            elif userCmd.startswith("get "):
                parts = userCmd.split()
                if len(parts) < 2:
                    print("Usage: get <remote-file> [local-file]")
                    continue
                remoteFile = parts[1]
                localFile = parts[2] if len(parts) >= 3 else os.path.basename(remoteFile)
                pasvStatus, dataSocket = modePASV(clientSocket)
                if pasvStatus != 227:
                    print("ERROR: PASV failed; cannot RETR.")
                    continue
                reply = sendCommand(clientSocket, "RETR " + remoteFile + "\r\n")
                print(reply)
                # Expect 150 or 125 before data transfer
                if not (reply.startswith("150") or reply.startswith("125")):
                    dataSocket.close()
                    print("ERROR: RETR not accepted by server.")
                    continue
                with open(localFile, "wb") as f:
                    while True:
                        chunk = dataSocket.recv(4096)
                        if not chunk:
                            break
                        f.write(chunk)
                dataSocket.close()
                finalReply = receiveData(clientSocket)  # typically 226
                print(finalReply)
                print("Downloaded '{}' -> '{}'".format(remoteFile, localFile))

            # STOR
            elif userCmd.startswith("put "):
                parts = userCmd.split()
                if len(parts) < 2:
                    print("Usage: put <local-file> [remote-file]")
                    continue
                localFile = parts[1]
                remoteFile = parts[2] if len(parts) >= 3 else os.path.basename(localFile)
                if not os.path.isfile(localFile):
                    print("ERROR: Local file not found: {}".format(localFile))
                    continue
                pasvStatus, dataSocket = modePASV(clientSocket)
                if pasvStatus != 227:
                    print("ERROR: PASV failed; cannot STOR.")
                    continue
                reply = sendCommand(clientSocket, "STOR " + remoteFile + "\r\n")
                print(reply)
                # Expect 150 or 125 before data transfer
                if not (reply.startswith("150") or reply.startswith("125")):
                    dataSocket.close()
                    print("ERROR: STOR not accepted by server.")
                    continue
                with open(localFile, "rb") as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        dataSocket.sendall(chunk)
                dataSocket.close()
                finalReply = receiveData(clientSocket)  # typically 226
                print(finalReply)
                print("Uploaded '{}' -> '{}'".format(localFile, remoteFile))

            elif userCmd == "quit":
                break

            else:
                print("Unknown command")
    
    print("Disconnecting...")
    quitFTP(clientSocket)
    clientSocket.close()
    sys.exit(0)

main()

