from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4

class PacketDropSimulator(app_manager.RyuApp):
    """
    SDN Packet Drop Simulator using Ryu and OpenFlow 1.3.
    Installs a high-priority drop rule for a specific source IP (h1).
    All other traffic is forwarded to the controller for flooding.
    """
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PacketDropSimulator, self).__init__(*args, **kwargs)
        # IP address whose traffic will be dropped
        self.drop_ip = '10.0.0.1'

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Called when a switch connects to the controller.
        Installs two flow rules:
        1. Default rule (priority 0): send all packets to controller
        2. Drop rule (priority 10): drop all packets from drop_ip
        """
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Default rule: send unmatched packets to controller (priority 0)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # Drop rule: drop all IP packets from drop_ip (priority 10, higher)
        # Empty actions list = drop in OpenFlow
        match_drop = parser.OFPMatch(eth_type=0x0800,
                                     ipv4_src=self.drop_ip)
        self.add_flow(datapath, 10, match_drop, [])

        self.logger.info("Switch connected. Drop rule installed for %s", self.drop_ip)

    def add_flow(self, datapath, priority, match, actions):
        """
        Helper to build and send a FlowMod message to the switch.
        idle_timeout=0 and hard_timeout=0 means the rule persists permanently.
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            idle_timeout=0,   # no idle timeout
            hard_timeout=0    # no hard timeout - rule persists permanently
        )
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
        Handles packets sent to the controller (matched by default rule).
        Logs packet info and floods to all ports.
        """
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        dst = eth.dst
        src = eth.src

        self.logger.info("Packet in: src=%s dst=%s port=%s", src, dst, in_port)

        # Flood packet to all ports except the incoming port
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )
        datapath.send_msg(out)
