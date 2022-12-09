#
# Make all overlays available on all nodes by
# starting a service on each of the worker and lettting
# it connect to all the overlays. So this way the network
# gets extended to that node.
#
# This is a big hack, unfortunately.
#

import os
import time

total_workers = 10
total_overlays = 10
for i in range (total_workers):
  for j in range (total_overlays):
    command = "docker service rm dummy" + str (i) + str (j)

    os.system (command)
    
