from pox.core import core
import pox.openflow.libopenflow_01 as of
#from pox.openflow.discovery import Discovery
from pox.lib.util import dpidToStr
import networkx as nx
import matplotlib.pyplot as plt
from pox.lib.packet import *
import pox.lib.packet as pkt
from pox.lib.addresses import *
from pox.lib.revent import *
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST 
#import sys
#sys.path.append("/mininet/custom")
import sys
sys.path.append('/home/mininet/mininet/custom')
from Wide_Area_Network import *


class MiniNetwork:
    #one topology of the mininet is one Graph object
    #switches = []#All the switches in this network
    #hosts = []#All the hosts in this network
    #srcSwitchdstIPportNumMac = {}#With the source switch and destination IP, return nextHop port number.
    #NextHopIP_PortNum = {} #Next Hop Name and which port number to send to
    def __init__(self,graph,links): #Try to get all the combination of switches and destination hosts. 
        self.switches = [] 
        self.hosts = []
        self.srcSwitchdstIPportNumMac = {}
        self.NextHopIP_PortNum = {}
        self.HipMac = {}
        self.graph = graph
        self.links = links
        temp = self.graph.nodes()
        temp.sort()
		for node in temp:
	    	if 'h' in node:
				self.hosts.append(node)
	    	elif 's' in node:
		        self.switches.append(node)
    	for switch in self.switches:
            for host in self.hosts:
                ipSeries = nx.dijkstra_path(graph,switch,host)
                nextHop = ipSeries[1]
		#print self.links.getNextHopPort((switch,nextHop))
                self.srcSwitchdstIPportNumMac[(switch,host)] = self.links.getNextHopPort((switch,nextHop)) 
                
    def GetPortNumAndMacAddr(self, sourceSwitch, dstIPaddr):
        return self.srcSwitchdstIPportNumMac[(sourceSwitch,dstIPaddr)]

arpTable = {} # store {Host IP address : Host MAC address} , for MAC learning.
    
for list in SwitchIntfsWithHost.values():
    for dstIPAddr in list:
    	arpTable[dstIPAddr] = EthAddr("96:d7:9d:87:60:10")

def getKey(value):   #from the IP address, get the hosts/switches name according to File.
    for name,ip in nodes.iteritems():
        if ip[0] == value:
            return name
            
def getValue(key):
    return nodes.get(key)    

# Even a simple usage of the logger is much nicer than print!
log = core.getLogger()

# This table maps (router,IP.dstip) pairs to the port on 'router' at
# which we last saw a packet *from* 'IP address'.

network1 = MiniNetwork(G,link1)
linkTopo = {} #{brokenLink:relevant topology}
for i in range(len(linkBwSwitches)):
    print linkBwSwitches[i]
    original = linkAndWeight[linkBwSwitches[i]]
    linkAndWeight[linkBwSwitches[i]] = max_link_weight
    G2 = nx.Graph()
    print linkAndWeight
for key,value in linkAndWeight.iteritems():
	G2.add_weighted_edges_from([(key[0],key[1],int(value))])
    linkTopo[linkBwSwitches[i]] = MiniNetwork(G2,link1)
    linkAndWeight[linkBwSwitches[i]] = original
#network2 = MiniNetwork(G2,link1) #s1 and s2 break, pop(2)
#networkList = []
#networkList.append(network2)
#linkTopo = {}
#for i in range(len(linkAndWeightNoHosts)):
#    if (i == 0):
#    	linkTopo[linkAndWeightNoHosts[i][0]] = networkList[i]
print linkTopo
def _handle_ConnectionUp(event):
    currSwitch = Dpid_To_Ip[event.dpid]
    for host in network1.hosts:
        pair = network1.GetPortNumAndMacAddr(currSwitch,host)
        portNum = pair[0]
        MacAddr = pair[1]
        msg = of.ofp_flow_mod()
        msg.match.dl_type = 0x800
        msg.match.nw_dst = IPAddr(getValue(host)[0])
        msg.actions.append(of.ofp_action_dl_addr.set_dst(EthAddr(MacAddr)))
        msg.actions.append(of.ofp_action_output(port = portNum))
        event.connection.send(msg)
       
def _handle_PortStatus(event):
    #print event.dpid, event.port
    #print event.added, event.deleted, event.modified
    #print event.dpid, event.port, type(event.ofp.desc.state),type(of.OFPPC_PORT_DOWN) 
    if event.ofp.desc.state == 1 and of.OFPPC_PORT_DOWN == 1: #a link goes down
	    downSwitch = 's' + str(event.dpid)
	    downPort = event.port
	    brokenLink = DpidPortLink[(downSwitch, downPort)]
	#print linkTopo[brokenLink]
	    if brokenLink not in linkTopo:
	        return 
	    print "Warning: port failure happening on port" + str(event.port) + " on switch " + str(event.dpid) + " -- Updating flow rules."
        msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
        for connection in core.openflow.connections:
            connection.send(msg)
        for connection in core.openflow.connections:
            currSwitch = Dpid_To_Ip[connection.dpid]
            for host in linkTopo[brokenLink].hosts:
                portNum = linkTopo[brokenLink].GetPortNumAndMacAddr(currSwitch,host)#get the destination IP address of the host, get its MAC address from the arpTable.
                MacAddr = arpTable[getValue(host)[0]]
                msg = of.ofp_flow_mod()
                msg.match.dl_type = 0x800
                msg.match.nw_dst = IPAddr(getValue(host)[0])
                msg.actions.append(of.ofp_action_dl_addr.set_dst(EthAddr(MacAddr)))
                msg.actions.append(of.ofp_action_output(port = portNum))
                connection.send(msg)

    elif event.ofp.desc.state == 0 and of.OFPPC_PORT_DOWN == 1: #the link recovers itself
            #print event.dpid, event.port 
        print "Warning: port failure from port " + str(event.port) + " on switch " + str(event.dpid) + " is recovered! -- resume to normal flow rules"
        msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
        for connection in core.openflow.connections:
            connection.send(msg)
        for connection in core.openflow.connections:
            currSwitch = Dpid_To_Ip[connection.dpid]
            for host in network1.hosts:
                portNum = network1.GetPortNumAndMacAddr(currSwitch,host)
                MacAddr = arpTable[getValue(host)[0]]
                msg = of.ofp_flow_mod()
                msg.match.dl_type = 0x800
                msg.match.nw_dst = IPAddr(getValue(host)[0])
                msg.actions.append(of.ofp_action_dl_addr.set_dst(EthAddr(MacAddr)))
                msg.actions.append(of.ofp_action_output(port = portNum))
                connection.send(msg)

lost_packets = {}

def _send_paused_traffic(dpid,ipaddr,port):
    if (dpid,ipaddr) in lost_packets:
	    bucket = lost_packets[(dpid,ipaddr)]
	    del lost_packets[(dpid,ipaddr)]
	    for buffer_id,in_port in bucket:
	        po = of.ofp_packet_out(buffer_id = buffer_id, in_port = in_port)
	        po.actions.append(of.ofp_action_dl_addr.set_dst(arpTable[ipaddr]))
	        po.actions.append(of.ofp_action_output(port = port))
	        core.openflow.sendToDPID(dpid,po)
    
def _handle_PacketIn (event): # after receive the PacketIn message, handle it. get the information about the packet, get the
    #Learn the desintation IP address and fill up routing table, according to my store of edge list, get the port number
    #I need to handle the ARP request from each subnet first.
    packet = event.parsed
    #print packet.src
    if packet.type ==  ethernet.IPV6_TYPE:
	    return
    srcSwitch = "s" + str(event.dpid)
    print srcSwitch
    print packet.type,event.port
    #match = of.ofp_match.from_packet(packet)
    if isinstance(packet.next, arp):  #This solves the problem of turning every ARP into IP packets
        a = packet.next
        #destinationIP = a.protodst
	    #dstIPtest = getKey(destinationIP)
	    #test = network1.GetPortNumAndMacAddr(srcSwitch, dstIPtest)
	    if a.prototype == arp.PROTO_TYPE_IP:
	        if a.hwtype == arp.HW_TYPE_ETHERNET:
		        if a.protosrc != 0:
		            arpTable[str(a.protosrc)] = packet.src
		            print arpTable
		            _send_paused_traffic(event.dpid,str(a.protosrc),event.port)
        	        if a.opcode == a.REQUEST:
			            if str(a.protodst) in arpTable:
            		        r = pkt.arp()
            		        r.hwtype = a.hwtype
            		        r.prototype = a.prototype
            		        r.hwlen = a.hwlen
            		        r.protolen = a.protolen
            		        r.opcode = a.REPLY
            		        r.hwdst = a.hwsrc
            #r.hwsrc = switchMac[a.protodst]
            		        r.hwsrc = arpTable[str(a.protodst)]
            		        r.protodst = a.protosrc
            #print a.protodst.toRaw
            #print (r.protodst.toStr == "192.168.70.2")
            #if(r.protodst == IPAddr("192.168.70.2")):
            #if(r.protodst == IPAddr("192.168.10.1")):
            #r.hwsrc = EthAddr("52:fa:e1:4c:d1:6c")
            		        r.protosrc = a.protodst #a.protodst is the destination IP addresses
            		        e = pkt.ethernet(type=packet.type, src=r.hwsrc, dst=a.hwsrc)
            		        e.payload = r
            		        msg = of.ofp_packet_out()
            		        msg.data = e.pack()
            		        msg.actions.append(of.ofp_action_output(port = of.OFPP_IN_PORT))
            		        msg.in_port = event.port
            		        event.connection.send(msg)
			            else:
			                msg = of.ofp_packet_out(in_port = event.port, action = of.ofp_action_output(port = of.OFPP_IN_PORT))
			                event.connection.send(msg)
	#destinationIP = a.protodst
	#dstIPtest = getKey(destinationIP)
	#print dstIPtest
	#test = network1.GetPortNumAndMacAddr(srcSwitch,dstIPtest)
	#msg = of.ofp_packet_out(action = of.ofp_action_output(port = of.OFPP_FLOOD))
	#event.connection.send(msg)
    elif isinstance(packet.next, ipv4): #begin to receive IP packets, from each switch, controller needs to make the right move to send the packet into the right port. 
   	    arpTable[str(packet.next.srcip)] = packet.src
        dstIp = packet.next.dstip #get the packet's destination IP address
        desHost = getKey(dstIp)
	#print srcSwitch
	    port = network1.GetPortNumAndMacAddr(srcSwitch,desHost)
	#print pair
	#_send_paused_traffic(event.dpid, str(packet.next.srcip), event.port)
	    if str(dstIp) in arpTable:
	        #desHost = getKey(dstIp)
            #pair = network1.GetPortNumAndMacAddr(srcSwitch,desHost)
	        NextPort = port
	        DstMAC = arpTable[str(dstIp)]
            msg = of.ofp_flow_mod()
            msg.match.dl_type = 0x800
            msg.match.nw_dst = dstIp #destination IP address
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_dl_addr.set_dst(DstMAC))
            msg.actions.append(of.ofp_action_output(port = NextPort))
            event.connection.send(msg)
	    else:
	        if (event.dpid,str(dstIp)) not in lost_packets:
		        lost_packets[(event.dpid,str(dstIp))] = []
	        bucket = lost_packets[(event.dpid,str(dstIp))]
	        entry = (event.ofp.buffer_id,event.port)
	        bucket.append(entry)
	        while len(bucket) > 5: del bucket[0]


	        if srcSwitch in SwitchNameWithConnectingHosts:
		        if str(dstIp) in SwitchNameWithConnectingHosts[srcSwitch]:
	    #ARPnextPort = pair[0]
	    #print ARPnextPort
	    	        r = arp()
	    	        r.hwtype = r.HW_TYPE_ETHERNET
	    	        r.prototype = r.PROTO_TYPE_IP
	    	        r.hwlen = 6
	    	        r.protolen = r.protolen
	    	        r.opcode = r.REQUEST
   	    	        r.hwdst = ETHER_BROADCAST
	    	        r.protodst = dstIp
	    	        r.hwsrc = packet.src
	    	        r.protosrc = packet.next.srcip
	    	        e = ethernet(type = ethernet.ARP_TYPE, src = packet.src, dst = ETHER_BROADCAST)
	    	        e.set_payload(r)
	    	        msg = of.ofp_packet_out()
	    	        msg.data = e.pack()
	    	        msg.actions.append(of.ofp_action_output(port = port))
	    	        msg.in_port = event.port
	     	        event.connection.send(msg)
		        else:
		            NextPortNum = pair[0]
		            msg = of.ofp_flow_mod()
		            msg.match.dl_type = 0x800
		            msg.match.nw_dst = dstIp
		            msg.data = event.ofp
		            msg.actions.append(of.ofp_action_output(port = port))
	   	            event.connection.send(msg)
            else:
		        NextPortNum2 = pair[0]
		        msg = of.ofp_flow_mod()
		        msg.match.dl_type = 0x800
	  	        msg.match.nw_dst = dstIp
		        msg.data = event.ofp
		        msg.actions.append(of.ofp_action_output(port = port))
		        event.connection.send(msg)

def launch ():
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    #core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PortStatus", _handle_PortStatus)

if __name__ == '__main__':
    setLogLevel( 'info' )
    net = emptyNet()
