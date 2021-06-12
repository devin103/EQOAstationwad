# EQOAstationwad

This file asks for an ip address input, and parses the station.wad file for EQOA Frontiers and replaces all the ip addresses, using the proper format needed. 
This can allow server's to patch over this file to client's and direct them to the appropriate account login server.
This utilizes python 3 built in libraries, so should be fairly simple to use.

A new file is generated, stationNew.wad, which would need to be changed to station.wad before attempting to pack it into a ps2 memory card or patching it to client's.
