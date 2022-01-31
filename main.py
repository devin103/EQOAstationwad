import struct as struct
import ipaddress
import zlib
import os
import gzip
import shutil

debug = False
def crc(fileName):
    prev = 0
    for eachLine in open(fileName,"rb"):
        prev = zlib.crc32(eachLine, prev)
    return (prev & 0xFFFFFFFF)

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)
        
if(debug):
  print('Creating Patch folders')
createFolder('./patch/eqoa/')
createFolder('./patch/web/eqoa/motd/')
if(debug):
  print('Created...')
if(debug):
  print("Creating station.wad and eqahost.txt")

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
fnew = open('./patch/eqoa/station.wad', 'wb+')

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
  if(debug):
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
      if(debug):
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
  if(debug):
    print("Writing offset: {}".format(hex(offSet)))

  #Write new file length
  fileLength = FileLength + (NewIPLen - ipLen)
  fnew.write(struct.pack('<L', fileLength))
  if(debug):
    print("Writing file length: {}".format(fileLength))
    print("")

f.close()
fnew.close()

#Create eqahosts.txt
fnew = open('./patch/eqoa/eqahosts.txt', 'w+')
fnew.write(NewIP+":10070")
fnew.close()

# Creates a folder in the current directory called data
if(debug):
  print("Done...") 

if(debug):
  print("Creating xml file")
fxml = open('./patch/eqoa/eqoa-frontierslive-update.xml', 'w+')
fxml.write("<VerantPatcher Version=\"1.0\">\n")
fxml.write("\t<Product Name=\"EverQuest Online Adventures: Frontiers Live\" Server=\"patch.everquestonlineadventures.com\" Port=\"7000\" UseCRC=\"true\" GzPath=\"/m2/http-docs/patch/eqoa/frontierslive\" AccessPath=\"patch/eqoa/frontierslive\" Version=\"38\">\n")
fxml.write("\t\t<Distribution Name=\"Frontiers Live Distribution\" Title=\"EQOA Frontiers Live Patch Files\" FilePath=\"/m2/http-docs/patch/eqoa-release/frontierslive\" GzPath=\"/m2/http-docs/patch/eqoa/frontierslive\">\n")
fxml.write("\t\t\t<Directory LocalPath=\"::HomeDirectory::\" Name=\".\" RemotePath=\"patch/eqoa/frontierslive\">\n")
fxml.write("\t\t\t\t<Directory Name=\"BASLUS-20744EQONLINE\">\n")
fxml.write("\t\t\t\t\t<File LocalName=\"eqahosts.txt\" TimeStamp=\"2003:12:13: 3: 7:37\" Name=\"eqahosts.txt.gz\" TotalSize={} DownloadSize={} CRC= {}/>\n".format(os.path.getsize('./patch/eqoa/eqahosts.txt'), os.path.getsize('./patch/eqoa/eqahosts.txt'), crc('./patch/eqoa/eqahosts.txt')))
fxml.write("\t\t\t\t\t<File LocalName=\"station.wad\" TimeStamp=\"2003:12:13: 3: 7:37\" Name=\"station.wad.gz\" TotalSize={} DownloadSize={} CRC={}/>\n".format(os.path.getsize('./patch/eqoa/station.wad'), os.path.getsize('./patch/eqoa/station.wad'), crc('./patch/eqoa/station.wad')))
fxml.write("\t\t\t\t</Directory>\n")
fxml.write("\t\t\t</Directory>\n")
fxml.write("\t\t</Distribution>\n")
fxml.write("\t</Product>\n")
fxml.write("</VerantPatcher>\n")
fxml.close()
if(debug):
  print("Xml created.")
  print("Zipping files")
with open('./patch/eqoa/station.wad', 'rb') as f_in:
    with gzip.open('./patch/eqoa/station.wad.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
with open('./patch/eqoa/eqahosts.txt', 'rb') as f_in:
    with gzip.open('./patch/eqoa/eqahosts.txt.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
        
#Remove old files
os.remove('./patch/eqoa/station.wad')
os.remove('./patch/eqoa/eqahosts.txt')

if(debug):
  print("Done zipping files")

print("Remember to change the stationNew.wad to station.wad before using in patches or on memory cards...")