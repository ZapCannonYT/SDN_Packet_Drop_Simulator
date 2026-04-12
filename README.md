# SDN Packet Drop Simulator

## Problem Statement
Simulate selective packet dropping using SDN flow rules with Mininet and a Ryu OpenFlow controller. The controller installs a high-priority drop rule for a specific IP address, demonstrating how SDN can programmatically control network traffic at the flow level.

## Topology
h1 (10.0.0.1) --- s1 --- h2 (10.0.0.2)
                   |
              Ryu Controller

## Setup & Execution

### Requirements
- Ubuntu 22.04 (WSL2 or VM)
- Mininet
- Python 3.11 virtual environment
- Ryu controller

### Installation
sudo apt install mininet -y
sudo apt install openvswitch-switch -y
python3.11 -m venv ~/ryu-env
source ~/ryu-env/bin/activate
pip install setuptools==58.0.0
pip install dnspython==2.2.1
pip install eventlet==0.33.3
pip install ryu

### Running

Terminal 1 - Start Ryu controller:
source ~/ryu-env/bin/activate
~/ryu-env/bin/ryu-manager packet_drop.py

Terminal 2 - Start Mininet:
sudo service openvswitch-switch start
sudo mn --controller=remote,ip=127.0.0.1,port=6633

## SDN Logic
- Default rule (priority 0): Send all unmatched packets to controller
- Drop rule (priority 10): Drop all IP packets with source 10.0.0.1 (h1)

The drop rule has higher priority so it matches first, silently discarding h1's traffic before it reaches h2.

## Test Scenarios

### Scenario 1 - Blocked host (h1 to h2)
mininet> h1 ping h2 -c 4
Expected: 100% packet loss (drop rule matches h1's IP)

### Scenario 2 - Return traffic blocked (h2 to h1)
mininet> h2 ping h1 -c 4
Expected: 100% packet loss (h1 cannot reply)

### Flow Table Verification
mininet> sh ovs-ofctl dump-flows s1

## Expected Output
cookie=0x0, table=0, priority=10,ip,nw_src=10.0.0.1 actions=drop
cookie=0x0, table=0, priority=0 actions=CONTROLLER:65535

## Proof of Execution

### Mininet - Ping tests and flow table
![Mininet Output](cn_orange_1.png)

### Ryu Controller - Drop rule installation
![Ryu Controller](cn_orange_2.png)

## References
- Mininet: https://mininet.org
- Ryu SDN Framework: https://ryu-sdn.org
- OpenFlow 1.3 Spec: https://opennetworking.org/wp-content/uploads/2014/10/openflow-spec-v1.3.0.pdf
