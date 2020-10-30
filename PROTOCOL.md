# Reverse Engineering a Network Protocol

## Deconstructing messages

### Packet breakdown

33 - 38: client `bryan` logging in.

126 - 133: client `ben` logging in.

206 - 213: client `bryan` asking `WHOISIN`

257 - 262: client `ben` broadcasting: "ben broadcast"

448 - 453: client `bryan` broadcasting: "bryan broadcast"

517 - 520: client `bryan` to `ben`: "bryan to ben private message"

600 - 603: client `ben` to `bryan`: "ben to bryan private message"

643 - 646: client `bryan` to `ben`: "short"

711 - 714: client `bryan` to `ben`: "this is a very long sentence, and i wonder if there will be any data fragmentation due to this."

804 - 811: client `bryan` logging out.

844 - 851: client `bryan` logging in.

1028 - 1037: client `amanda` logging in.

1100 - 1109: client `amanda` logging out.

1148 - 1155: client `bryan` logging out.

1190 - 1191: client `ben` force quit.

1224 - 1239: client `bryan` and `ben` logging in.

1386 - 1387 client `ben` force quit.

1395 - 1396 client `bryan` force quit.

### Client behaviour

#### Logging in

##### 33 - 38

33, 34, 35 set up the TCP handshake - SYN, SYN ACK, ACK.

36, 37, 38 are the TCP Window Update, PSH ACK, ACK.

All other logging in packets are similar.

The server receives the name of the client upon logging in. Therefore, the data must be somewhere within the packet transfers.

If we look at packet 37, there is a 6 byte data packet:

```
Data: 627279616e0a
Decoded: bryan\n
```

Which is the username `bryan\n` in ASCII.

Client `bryan` is on Port 52308.

> The 2nd packet after a handshake is made will push the username of the client to the server.

##### 126 - 131

To confirm this again, we can check the log in packet for ben at 126 + 4 = 130:

```
Data: 62656e0a
Decoded: ben\n
```

Which is the username `ben\n` in ASCII.

Client `ben` is on Port 52316.



##### 132 - 133

Packets 132 to 133 are additional packets sent in addition to the log in packets, probably due to discovering clients in the chatroom.

132 contains some data sent to client `bryan`:

```
Data: 32323a32363a313220202a2a2a2062656e20686173206a6f696e656420746865206368617420726f6f6d2e202a2a2a200a0a
Decoded: 22:26:12  *** ben has joined the chat room. *** \n
```

The server notifies all other connected clients about new users.

#### WHOISIN

##### 206 - 213

206: `bryan` issues a `WHOISIN` command which contains 6 bytes to the server:

```
Data: 75736572730a
Decoded: users\n
```

207, 208: The server ACK, then sends:

```
Data: 4c697374206f662074686520757365727320636f6e6e65637465642061742032323a32363a35300a0a
Decoded: List of the users connected at 22:26:50\n
```

209: `bryan` ACK

210: The server sends:

```
Data: 312920627279616e2073696e636520467269204f63742030322032323a32343a35312053475420323032300a0a
Decoded: 1) bryan since Fri Oct 02 22:24:51 SGT 2020\n
```

211: `bryan` ACK

212: The server sends:

```
Data: 32292062656e2073696e636520467269204f63742030322032323a32363a31322053475420323032300a0a
Decoded: 2) ben since Fri Oct 02 22:26:12 SGT 2020
```

213: `bryan` ACK

#### Broadcasting messages

##### 257 - 262

`ben` broadcasting: "ben broadcast".

257: `ben` sends:

```
Data: 6d736762656e2062726f6164636173740a
Decoded: msgben broadcast\n
```

261: The server sends to all clients:

```
Data: 32323a32373a32382062656e3a2062656e2062726f6164636173740a0a
Decoded: 22:27:28 ben: ben broadcast\n
```

261: The server sends to all clients:

```
Data: 32323a32373a32382062656e3a2062656e2062726f6164636173740a0a
Decoded: 22:27:28 ben: ben broadcast\n
```

#### Private messages

##### 517 - 520

client `bryan` to `ben`: "bryan to ben private message".

517: `bryan` sends to the server:

```
Data: 6d73674062656e20627279616e20746f2062656e2070726976617465206d6573736167650a
Decoded: msg@ben bryan to ben private message
```

We can assume that this message is all that is required to initiate a private message.

#### Logging out

##### 804 - 811

`bryan` logging out.

804: `bryan` sends to the server:

```
Data: 657869740a
Decoded: exit\n
```



## Server behaviour

#### Starting the server

When starting, add to the logs:

```
{hh:mm:ss} Server waiting for Clients on port {port}.
```

#### Logging in

##### Locally

When a user logs on, they will establish a connection, then send:

```
{username}\n
```

Use this to label the connection, and store the connection as a client.

Then, print:

```
{hh:mm:ss} *** {username} has joined the chat room. ***
{hh:mm:ss} Server waiting for Clients on port {port}.
```

##### Remote

Once a client connects, send their username to all other clients:

```
{hh:mm:ss} *** {username} has joined the chat room. ***\n\n
```

#### WHOISIN

##### Locally

Nothing.

##### Remote

The client sends:

```
users\n
```

Then, respond with:

```
List of the users connected at 23:10:11

1) bryan since Fri Oct 30 23:10:19 SGT 2020

2) ben since Fri Oct 30 23:10:21 SGT 2020


```

