## File organization overview

- `algo.py`: logic for the core algorithms (OSPF and RIP)
- `host.py`: different kinds of servers that send and receives messages
- `topo.py`: mininet api calls to setup the hosts
- `log_helper.py`: helper functions that make colored log possible (very helpful)
- `commands.sh`: helper shell functions to shorten commands and speed things up. Not needed for grading

## The setup (`topo.py`)

Here is how the virtual network nodes are linked together in mininet. Every node in my setup is a mininet "host". All nodes are connected to a single switch, thus making them all reachable from one another in mininet. All nodes have static ip and incremental mac addresses.

To "connect" or "disconnect" nodes in my setup, ARP entries are set on each machine: for "connect", an ARP entry is set; for "disconnect" an invalid ARP entry is set, making the nodes unreachable. (see function `connect` and `disconnect` in `topo.py`)



## Different types of servers (`host.py`)

There are 3 server/node types:
- `Host`: aka end system as referred in the assignment handout
- `Router`
- `Monitor`: the monitor node that connects to all routers

Each has their corresponding request handler: `HostHandler` `RouterHandler` `MonitorHandler`

In `topo.py`, `Host`s are assigned with ip starting `10.0.0.1`; `Router`s are assigned with ip starting `10.0.0.101`. The code does not rely on this convention, this just makes debugging easier.

`Monitor` is assigned with ip `10.0.0.255`. Since there is only one monitor node, this is hard coded in the code. (`monitor_ip` in `host.py`)


## How the node works (`host.py`)

All communication are done over UDP. All UDP ports are 1111.

Each node should have a long running process, that receives data from UDP. Upon receiving data, it will act accordingly – discards it, forwards it, re-calculates forwarding table, send some message to another node, etc.

We cannot directly interact with that process (since listening on UDP is blocking). To trigger actions, we need to start a new process, which will send the message and exit – any response it might get is handled by the long running process.

See "How to run" section for how to set this up.


## Debugging

The code is thoroughly logged using python logging library. You should be able to see colored logs in each of the terminal window.

Sending packets, forwarding packets, dropping packets, routing exchanges are all logged in the console.


## Testing (`algo.py`)

The core algorithm are tested outside of the mininet. Simply run the file itself, `python algo.py` and it will run 5 non-trial test cases. The complex OSPF setup is from tutorial. If no error occurs then they all passed.


## Various Design Decisions

1. Due to how I use ARP to connect or disconnect the nodes, it's not particular easy to simulate network change. To achieve that, the ARP entries need to be modified and perhaps there needs to be a timer running in the background to capture that change and then update the routing entries accordingly.

2. The code assumes the communication channel is reliable. No messages are retransmitted if lost. If the monitor is waiting for a lost forwarding table packet, then it will hang forever.

3. To enable RIP, we must use `c/host.py rip-on` from the monitor node.

3. There is a monitor node connected to router even if we are using RIP. Using the monitor node is the only way to print the routing tables.

4. There is no timer to do RIP. If no routers' forwarding table are updated (i.e. when they already have the forwarding table containing all neighbors), then a RIP must be triggered manually. Running it manually makes it easier to debug and avoids being interrupted when debugging.


## How to run
First, `mkdir c`, then copy code into `/home/mininet/c/`. All files will live in this directory.
```
chmod +x /home/mininet/c/host.py
```

Now running this should give:
```
root@mininet-vm:/home/mininet# c/host.py
@301: DEBUG    Found neighbors: [...]
@304: ERROR    Available commands: ...
```

To start the long running process, run:
```
root@mininet-vm:/home/mininet# c/host.py start &
```
This puts the process in the background. It will still print output to the same shell. We can continue to execute commands in the same terminal. To kill that process, run `fg` then `ctrl-c`.

Start the long running process in each node by running the same command. The script will figure out whether it's node type (host, router, or monitor) by looking at neighbor count.

## Available actions
Friendly note: for IP, you can input `10` and it will auto-prefix making it `10.0.0.10`.

### In host
- broadcast: `c/host.py broadcast <ttl>`
- send message: `c/host.py send <dst_ip> <ttl>`

### In router
- broadcast: `c/host.py broadcast <ttl>`

### In monitor
- Tell all routers to print routing table: `c/host.py print all`
- Tell router to print its routing table: `c/host.py print <router_ip>`
- Execute one OSPF update: `c/host.py trigger-ospf`
- Tell router to do a RIP broadcast (as if the forwarding table has just changed): `c/host.py trigger-rip <router_ip>`
- Tell all routers to use RIP: `c/host.py rip-on`
- Tell all routers to not use RIP: `c/host.py rip-off`


