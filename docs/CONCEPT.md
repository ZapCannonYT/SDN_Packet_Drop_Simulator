# SDN Packet Drop Simulator - Concept

## What is Software Defined Networking (SDN)?

Traditional networks combine two responsibilities inside every network device:

- **Control Plane** – Decides where packets should go.
- **Data Plane** – Actually forwards packets.

Each switch independently makes forwarding decisions using its own routing or forwarding tables.

Software Defined Networking (SDN) separates these two responsibilities.

- The **controller** makes all forwarding decisions.
- The **switch** simply follows the controller's instructions.

This separation makes the network programmable and easier to manage.

---

## SDN Architecture

```
+---------------------------+
|      Applications         |
| (Firewall, QoS, Routing)  |
+------------+--------------+
             |
      Northbound APIs
             |
+------------v--------------+
|      SDN Controller       |
|         (Ryu)             |
+------------+--------------+
             |
      OpenFlow Protocol
             |
+------------v--------------+
|      OpenFlow Switch      |
|   (Open vSwitch in MN)    |
+------------+--------------+
             |
        End Hosts
```

---

## What is OpenFlow?

OpenFlow is the communication protocol between an SDN controller and an OpenFlow-enabled switch.

The controller sends:

- Flow rules
- Packet forwarding instructions
- Drop rules
- Statistics requests

The switch executes these rules.

---

## What is a Flow?

A flow is a group of packets that share common characteristics.

Examples:

- Source IP
- Destination IP
- Source MAC
- Destination MAC
- TCP Port
- UDP Port
- VLAN ID

Example:

```
Match:
Source IP = 10.0.0.1

Action:
DROP
```

Every packet matching this condition is discarded.

---

## Flow Tables

Each OpenFlow switch contains one or more flow tables.

Each flow entry contains:

| Field | Description |
|--------|-------------|
| Match | Packet fields to inspect |
| Priority | Higher value matched first |
| Action | Forward, Drop, Modify, Send to Controller |
| Counters | Packet statistics |
| Timeout | Rule lifetime |

Example:

```
Priority: 10

Match:
IPv4 Source = 10.0.0.1

Action:
DROP
```

---

## Rule Priority

Flow entries are matched in descending priority.

Example:

Priority 10

```
Match:
IPv4 Source = 10.0.0.1

Action:
DROP
```

Priority 0

```
Match:
ANY

Action:
Send to Controller
```

The switch checks Priority 10 first.

Since it matches, the packet is dropped.

The lower-priority rule is never evaluated.

---

## Why use a Drop Rule?

Packet drop rules are commonly used for:

- Firewalls
- Access Control Lists (ACLs)
- DDoS mitigation
- Traffic engineering
- Security policy enforcement

Instead of configuring every switch manually, the SDN controller installs the rules automatically.

---

## Project Workflow

1. Switch connects to Ryu.
2. Ryu installs two flow entries.
3. h1 sends a packet.
4. Switch matches the high-priority drop rule.
5. Packet is discarded.
6. h2 never receives the packet.

Packets from other hosts continue to be handled normally.

---

## Why this Project?

This project demonstrates one of the simplest SDN applications:

- Dynamic flow installation
- Rule priorities
- OpenFlow communication
- Centralized network control

Although simple, the same mechanism is used in production SDN networks for security, routing, and traffic management.
