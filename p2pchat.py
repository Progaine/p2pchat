import socket
import threading
import datetime

def p2pchat():
	ip_address = '255.255.255.255'
	serverPort = 8007

	user_name = input('Enter your name: ')
	threading.Thread(target=sender, args=(user_name, ip_address, serverPort)).start()
	threading.Thread(target=receiver, args=(serverPort,)).start()

def sender(user_name, ip_address, port):
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	application_message = build_message(user_name, "JOIN", "")
	application_message = application_message.encode("utf-8")

	clientSocket.sendto(application_message,(ip_address, port))

	while True:
		user_message = input("")

		if user_message == "/leave":
			application_message = build_message(user_name, "LEAVE", "")
		
		else:
			application_message = build_message(user_name, "TALK", user_message)

		application_message = application_message.encode("utf-8")

		clientSocket.sendto(application_message,(ip_address, port))

def receiver(port):
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverSocket.bind(("", port))

	while True:
		application_message, clientAddress = serverSocket.recvfrom(2048)
		application_message = application_message.decode("utf-8")

		user_name, command, user_message = parse_message(application_message)

		messageToPrint = ""

		if command == "JOIN":
			messageToPrint = "{} {} joined!".format(datetime.datetime.now(), user_name)

		elif command == "TALK":
			messageToPrint = "{} [{}]: {}".format(datetime.datetime.now(), user_name, user_message)

		elif command == "LEAVE":
			messageToPrint = "{} {} left!".format(datetime.datetime.now(), user_name)

		print(messageToPrint)

def build_message(name, command, message):
	return "user:" + name + "\ncommand:" + command + "\nmessage:" + message + "\n\n"

def parse_message(message):
	user = message.split("\n")[0].split("user:")[1]
	command = message.split("\n")[1].split("command:")[1]
	message = message.split("\n")[2].split("message:")[1]
	return (user, command, message)

p2pchat()