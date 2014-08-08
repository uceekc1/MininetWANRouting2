from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of

from pox.openflow.of_json import *

log = core.getLogger()

def _timer_func ():
    for connection in core.openflow._connections.values():
        #connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
        connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
    log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

# handler to display flow statistics received in JSON format
# structure of event.stats is defined by ofp_flow_stats()
def _handle_flowstats_received (event):
    stats = flow_stats_to_list(event.stats)
    log.debug("FlowStatsReceived from %s: %s",
      dpidToStr(event.connection.dpid), stats)

  # Get number of bytes/packets in flows for web traffic only
    web_bytes = 0
    web_flows = 0
    web_packet = 0
    for f in event.stats:
        print f
        if f.match.tp_dst == 80 or f.match.tp_src == 80:
            web_bytes += f.byte_count
            web_packet += f.packet_count
            web_flows += 1
    log.info("Web traffic from %s: %s bytes (%s packets) over %s flows",
      dpidToStr(event.connection.dpid), web_bytes, web_packet, web_flows)

# handler to display port statistics received in JSON format
def _handle_portstats_received (event):
    stats = flow_stats_to_list(event.stats)
    # Get the total bytes number on switch 1
    bytes  = 0
    #if dpidToStr(event.connection.dpid) == '00-00-00-00-00-01':
    for f in event.stats:
        bytes += f.tx_dropped
    print event.connection.dpid, bytes

    #print "states received from", dpidToStr(event.connection.dpid)
    log.debug("PortStatsReceived from %s: %s",
      dpidToStr(event.connection.dpid), stats)
    
# main functiont to launch the module
def launch ():
    from pox.lib.recoco import Timer
    print bytes
  # attach handsers to listners
    #core.openflow.addListenerByName("FlowStatsReceived",
    #  _handle_flowstats_received)
    core.openflow.addListenerByName("PortStatsReceived",
      _handle_portstats_received)
    
  # timer set to execute every five seconds
    Timer(1, _timer_func, recurring=True)
   
