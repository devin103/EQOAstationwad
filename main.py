import struct as struct
import ipaddress

print("Please enter IP Address")
print("Formating considerations: *xxx.xxx.xxx.xxx*")
NewIP = input("Enter here: ")
print(len(NewIP))
NewIPLen = len(NewIP) + 7


#Verify IP Address is valid
try:
  ipaddress.ip_address(NewIP)

except:
  input("Invalid IP Address...")
  quit()

print("Adding IP: {} To file".format(NewIP))
print("")

#Open station.wad
f = open('station.wad', 'rb')
fnew = open('stationNew.wad', 'wb+')

#Write the first 76 bytes to the new File
fnew.write(f.read(76))

#Loop over reading the four files
for i in range(4):
  #Seek to first file offset
  f.seek(0x10 * (i + 1))
  offset = 0x10 * ( i + 1)

  #Get first file offset
  FileOffset = struct.unpack('<L', f.read(4))[0]
  FileLength = struct.unpack('<L', f.read(4))[0]

  print("Offset data is at: {}".format(hex(offset)))
  print("File Offset is at: {}".format(hex(FileOffset)))
  print("File Length is: {}".format(FileLength))

  f.seek(FileOffset)
  
  fnew.seek(0, 2)
  fnew.write(f.read(256))

  #Just keep looping through till we find what we need
  while True:
    
    #Check string length
    strLen = struct.unpack('>L', f.read(4))[0]
    f.seek(f.tell() - 4)
    fnew.write(f.read(4))
    
    #Get string
    string = f.read(strLen)
    f.seek(f.tell() - strLen)
    fnew.write(f.read(strLen))

    #This is the string we are looking for
    if string == b'stationdata/servers/stationLiveHosts.txt':
      print("Found Station Hosts File...")
      break
    
    else:
      #Check string length
      strLen = struct.unpack(">L", f.read(4))[0]
      f.seek(f.tell() - 4)
      fnew.write(f.read(4))
    
      #Get string
      string = f.read(strLen)
      f.seek(f.tell() - strLen)
      fnew.write(f.read(strLen))

  #Gets old IP Length 
  ipLen = struct.unpack(">L", f.read(4))[0]

  fnew.write(struct.pack('>L', NewIPLen))
  fnew.write(NewIP.encode('utf-8'))
  fnew.write(b'\x3a\x39\x37\x33\x35\x0D\x0A')
  f.read(ipLen)

  #Loop over the last 2 chunks of the "file" and write it to new file
  for j in range(2):

    #Check string length
    strLen = struct.unpack(">L", f.read(4))[0]
    f.seek(f.tell() - 4)
    fnew.write(f.read(4))
      
    #Get string
    string = f.read(strLen)
    f.seek(f.tell() - strLen)
    fnew.write(f.read(strLen))

  #subtract new ip length against old ip length, then add it to the offset
  # Say new ip is 12, old ip is 10, offset is 0x4C and i = 0
  #new offset = 0x4C + ( 0 * (10 - 12))
  # new offset is still 0x4c
  # Say new ip is 12, old ip is 10, offset is 0x4C and i = 1
  #new offset = 0x4C + ( 1 * (10 - 12))
  #new offset is now 0x4A
  
  fnew.seek(0x10 * (i + 1))
  offSet = FileOffset + (i * (NewIPLen - ipLen))
  fnew.write(struct.pack('<L', offSet))
  print("Writing offset: {}".format(hex(offSet)))

  #Write new file length
  fileLength = FileLength + (NewIPLen - ipLen)
  fnew.write(struct.pack('<L', fileLength))
  print("Writing file length: {}".format(fileLength))
  print("")

f.close()
fnew.close()
print("Done...")
input("Remember to change the stationNew.wad to station.wad before using in patches or on memory cards...")