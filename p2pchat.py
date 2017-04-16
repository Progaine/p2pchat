import socket
import threading
import datetime

def p2pchat():
	ip_address = '255.255.255.255'
	serverPort = 8007

	user_name = input('Enter your name: ')
	threading.Thread(target=receiver, args=(user_name, ip_address, serverPort)).start()
	threading.Thread(target=sender, args=(user_name, ip_address, serverPort)).start()

def sender(user_name, ip_address, port):
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	application_message = build_message(user_name, "JOIN", "")

	clientSocket.sendto(application_message,(ip_address, port))

	while True:
		user_message = input("")

		if user_message == "/leave":
			application_message = build_message(user_name, "LEAVE", "")
			clientSocket.sendto(application_message,(ip_address, port))

			application_message = build_message(user_name, "QUIT", "")
			clientSocket.sendto(application_message,("localhost", port))
		elif user_message == "/who":
			application_message = build_message(user_name, "WHO", "")
			clientSocket.sendto(application_message,("localhost", port))
		elif user_message[:8] == "/private":
			user_name = user_message[9:]
			user_message = input("Private message to " + user_name + ": ")
			application_message = build_message(user_name, "PRIVATE-TALK", user_message)
			clientSocket.sendto(application_message,("localhost", port))
		else:
			application_message = build_message(user_name, "TALK", user_message)	
			clientSocket.sendto(application_message,(ip_address, port))

def receiver(my_name, ip_address, port):
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	serverSocket.bind(("", port))
	connected_users = dict()

	while True:
		application_message, clientAddress = serverSocket.recvfrom(2048)

		user_name, command, user_message = parse_message(application_message)

		messageToPrint = ""

		if command == "JOIN":
			messageToPrint = "{} {} joined!".format(datetime.datetime.now(), user_name)
			connected_users[user_name] = clientAddress[0]
			application_message = build_message(my_name, "PING", "")
			serverSocket.sendto(application_message, (ip_address, port))
		elif command == "TALK":
			messageToPrint = "{} [{}]: {}".format(datetime.datetime.now(), user_name, user_message)
		elif command == "LEAVE":
			messageToPrint = "{} {} left!".format(datetime.datetime.now(), user_name)
			connected_users.pop(user_name, None)
		elif command == "QUIT":
			messageToPrint = "Bye now!"
		elif command == "WHO":
			messageToPrint = "{} Connected users: {}".format(datetime.datetime.now(), list(connected_users))
		elif command == "PING":
			if user_name not in connected_users:
				connected_users[user_name] = clientAddress[0]
		elif command == "PRIVATE-TALK":
			if clientAddress[0] == "127.0.0.1":
				application_message = build_message(my_name, "PRIVATE-TALK", user_message)
				serverSocket.sendto(application_message, (connected_users[user_name], port))
			else:
				messageToPrint = "{} [{}] (PRIVATE): {}".format(datetime.datetime.now(), user_name, user_message)

		print(messageToPrint)

def build_message(name, command, message):
	return ("user:" + name + "\ncommand:" + command + "\nmessage:" + message + "\n\n").encode("utf-8")

def parse_message(message):
	message = message.decode("utf-8")
	user = message.split("\n")[0].split("user:")[1]
	command = message.split("\n")[1].split("command:")[1]
	message = message.split("\n")[2].split("message:")[1]
	return (user, command, message)

p2pchat()