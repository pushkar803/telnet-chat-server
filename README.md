# telnet-chat-server

Start telnet chat server as follows

```
python chatserver.py
```

Start client
```
#telnet domain port
telnet localhost 8888
telnet 10.3.32.2 8888
```

After successfull connection it will enter username that will be used further in chats

Broadcast messages
```
#broadcast $MSG
broadcast hello
```

Send private message to specific user
```
#@username $MSG
@pushkar hi
```
