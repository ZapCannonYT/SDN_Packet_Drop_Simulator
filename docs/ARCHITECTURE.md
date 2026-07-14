# Project Architecture

## Overall Architecture

```
                     +--------------------+
                     |   Ryu Controller   |
                     |    packet_drop.py  |
                     +---------+----------+
                               |
                      OpenFlow 1.3
                               |
                     +---------v----------+
                     | Open vSwitch (s1)  |
                     +----+----------+----+
                          |          |
                     h1              h2
                 10.0.0.1       10.0.0.2
```

---

## Components

### 1. Mininet

Mininet creates the virtual network.

It provides:

- Virtual hosts
- Virtual switch
- Virtual Ethernet links

Topology:

```
h1 ---- s1 ---- h2
```

---

### 2. Open vSwitch

Open vSwitch (OVS) acts as an OpenFlow-enabled switch.

Responsibilities:

- Receives packets
- Matches flow entries
- Executes actions
- Communicates with Ryu

---

### 3. Ryu Controller

Ryu acts as the SDN controller.

Responsibilities:

- Accept switch connections
- Install flow entries
- Process Packet-In messages
- Send Packet-Out messages

---

## Flow Installation Sequence

```
Switch boots
      |
      |
Connects to Controller
      |
      |
EventOFPSwitchFeatures
      |
      |
Install Default Flow
(priority 0)
      |
      |
Install Drop Rule
(priority 10)
      |
      |
Switch Ready
```

---

## Packet Processing

### Packet from h1

```
h1
 |
 |
 v
Open vSwitch
 |
 |
Match:
IPv4 Source = 10.0.0.1
 |
 |
DROP
```

The packet never reaches h2.

---

### Packet from h2

```
h2
 |
 |
 v
Open vSwitch
 |
 |
No Drop Rule Match
 |
 |
Send Packet-In
 |
 |
Ryu Controller
 |
 |
Packet-Out
 |
 |
Flood
```

---

## Flow Table

After the controller starts:

| Priority | Match | Action |
|----------|-------|--------|
| 10 | IPv4 Source = 10.0.0.1 | DROP |
| 0 | Any Packet | CONTROLLER |

---

## Event Flow

```
Switch Connects
       |
       v
Switch Features Event
       |
       v
Install Flow Rules
       |
       v
Packet Arrives
       |
       v
Flow Lookup
       |
       +------------------+
       |                  |
 Match Drop Rule?         No
       |                  |
      Yes                 |
       |                  |
      DROP         Send Packet-In
                          |
                          v
                  Controller Processes
                          |
                          v
                      Packet-Out
                          |
                          v
                        FLOOD
```

---

## Why This Design?

This architecture demonstrates the core SDN principle:

- The switch performs simple forwarding.
- The controller defines network behavior.
- Policies can be changed without modifying the switch itself.

This separation of the control plane and data plane is the defining characteristic of Software Defined Networking.
