POX and Mininet are both put into the same Mininet virtual machine. 

Where to put POX: It doesn't matter
Where to put Mininet: home/mininet/mininet/custom

First run POX: type in: ./pox.py routing py
Then run Mininet: sudo python Wide_Area_Network.py

After starting up the Mininet, wait for 10 seconds, the network would do a Pingall itself, after that, you can type in h1 ping h3, or h1 ping h4 to test the link failure and recovery. And 10 seconds after the network does pingall, a link failure between s1 and s2 would happen, after 8 seconds, the link recovers itself. and after 8 seconds, the another link fails, and it recovers itself after 8 seconds. 

