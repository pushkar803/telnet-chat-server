from twisted.internet import protocol, reactor
from twisted.protocols import basic

# telnet localhost 1234


class TelnetServerProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.username = None

    def connectionMade(self):
        self.sendLine(b"Welcome to the Twisted Telnet Server!")
        self.sendLine(b"Please enter your username:")

    def lineReceived(self, line):
        line = line.decode('utf-8').strip()
        if self.username is None:
            self.handle_login(line)
        else:
            self.handle_command(line)

    def handle_login(self, username):
        if self.factory.is_username_taken(username):
            self.sendLine(
                b"Username is already taken. Please enter another username:")
        else:
            self.username = username
            self.factory.add_client(self)
            self.sendLine(b"Welcome, " + self.username.encode('utf-8') + b"!")
            self.sendLine(
                b"Type 'quit' to disconnect, 'list' to view connected clients,")
            self.sendLine(b"'broadcast message' to send a broadcast message,")
            self.sendLine(
                b"and '@username message' to send a private message.")
            self.sendLine(b"Enter your command:")

    def handle_command(self, command):
        if command == "quit":
            self.sendLine(b"Goodbye, " + self.username.encode('utf-8') + b"!")
            self.transport.loseConnection()
            self.factory.remove_client(self)
        elif command == "list":
            clients = self.factory.get_client_list()
            if clients:
                client_list = b"\n".join(clients)
                self.sendLine(b"Connected clients:")
                self.sendLine(client_list)
            else:
                self.sendLine(b"No other clients connected.")
        elif command.startswith("broadcast "):
            message = command[10:]
            self.factory.broadcast_message(self.username, message)
        elif command.startswith("@"):
            self.handle_private_message(command)
        else:
            self.sendLine(b"You entered: " + command.encode('utf-8'))
            self.sendLine(b"Enter your command:")

    def handle_private_message(self, command):
        parts = command.split(" ", 1)
        if len(parts) > 1:
            recipient = parts[0][1:]
            message = parts[1]
            self.factory.send_private_message(
                self.username, recipient, message)
        else:
            self.sendLine(
                b"Invalid private message format. Usage: '@username message'")
            self.sendLine(b"Enter your command:")


class TelnetServerFactory(protocol.ServerFactory):
    def __init__(self):
        self.clients = {}

    def is_username_taken(self, username):
        return username in self.clients

    def add_client(self, client):
        self.clients[client.username] = client

    def remove_client(self, client):
        del self.clients[client.username]

    def get_client_list(self):
        return [client.username.encode('utf-8') for client in self.clients.values()]

    def broadcast_message(self, sender, message):
        for client in self.clients.values():
            if client.username != sender:
                client.sendLine(b"<" + sender.encode('utf-8') +
                                b"> " + message.encode('utf-8'))

    def send_private_message(self, sender, recipient, message):
        if recipient in self.clients:
            self.clients[recipient].sendLine(
                b"(private from " + sender.encode('utf-8') + b") " + message.encode('utf-8'))
        else:
            sender_client = self.clients[sender]
            sender_client.sendLine(
                b"User '" + recipient.encode('utf-8') + b"' is not connected.")

    def buildProtocol(self, addr):
        return TelnetServerProtocol(self)


if __name__ == "__main__":
    factory = TelnetServerFactory()
    reactor.listenTCP(8888, factory)
    reactor.run()
