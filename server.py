import random
import socket
import subprocess
import linecache
global pick_new

class RootServers(object):                                                                     # object for storing user data
    def __init__(self, name, addr, RTT, Flag):                                           # constructor
        self.name = name
        self.addr = (addr,53)
        self.RTT = RTT
        self.Flag = Flag

list_of_RootServers = [RootServers("c.root-servers.net","192.33.4.12",0,False),RootServers("d.root-servers.net","199.7.91.13",0,False), RootServers("e.root-servers.net","192.203.230.10",0,False), RootServers("f.root-servers.net","192.5.5.241",0, False), RootServers("k.root-servers.net","193.0.14.129",0, False), RootServers("h.root-servers.net","198.97.190.53",0, False), RootServers("i.root-servers.net","192.36.148.17",0, False), RootServers("j.root-servers.net","192.58.128.30",0, False)]

list_of_IP_RootServers = []

for x in list_of_RootServers:
    list_of_IP_RootServers += x.addr

def RoundTripTime():

    for y in list_of_RootServers:

        command = subprocess.Popen(["ping -c 1 " + y.addr[0]], shell=True, stdout=subprocess.PIPE)

        Ping = command.communicate()
        Ping = Ping[0].decode('utf-8')

        PingTime = ''

        for x in Ping[Ping.find("time=")+6:]:
            PingTime += x
            if x == " ":
                break

        y.RTT = float(PingTime)

def Pick_and_Mark():
    global pick_new
    pick_new = False
    for x in list_of_RootServers:
        print(x.RTT)
    RTTless = PickServer(len(list_of_RootServers))
    print(f"Picked : {RTTless}")


    for x in range(len(list_of_RootServers)):
        if list_of_RootServers[x].RTT == RTTless:
            index = x
            list_of_RootServers[x].Flag = True
            list_of_RootServers[x].RTT = 100000



    return list_of_RootServers[index].addr


def set_bit (x,n):                                                                                      # Function that sets the RD bit to 0
    return x & 0 << n

def GetAnswer(IP_nameserver):

    sock.sendto(ReqNoRQ, IP_nameserver)
    print(IP_nameserver)

    newdata,addr = sock.recvfrom(4096)

    answer_records = int(str(bin(newdata[7])),2)


    return answer_records


def GetIP(IP_nameserver):
    global pick_new
    sock.sendto(ReqNoRQ, IP_nameserver)
    newdata, addr = sock.recvfrom(4096)

    authority_records = int(str(bin(newdata[9])), 2)  # Grab number of authority records from bytestream
    answer_records = int(str(bin(newdata[7])), 2)
    additional_records = int(str(bin(newdata[11])), 2)  # Grab number of aditional records from bytestream

    print(answer_records)
    print(authority_records)
    if authority_records >= additional_records and answer_records == 0:
        return Pick_and_Mark()
    additional_records = int(str(bin(newdata[11])), 2)  # Grab number of aditional records from bytestream
    i = 1
    for byte in newdata[12:]:
        if int(str(bin(byte)), 2) == 0:
            break
        i += 1
    QueryField = i + 4


    if int(str(bin(newdata[QueryField + 12 + 1])), 2) == 0:
        name = True
    else:
        name = False
    i = 1
    x = 1
    flag = True

    if name == False:
        for byte in newdata[QueryField + 12:]:

            if int(str(bin(byte)), 2) == 192:
                i = 1
            if int(str(bin(byte)), 2) != 2 and i == 4:
                flag = False
            if flag == False:

                break
            i += 1
            x += 1
        authority_records_bytes = x - 4
    else:
        authority_records_bytes = 16 * authority_records + 15



    start_of_additional_records = 12 + QueryField + authority_records_bytes
    end_of_additional_records = start_of_additional_records + (authority_records * 16) + (
            authority_records * 28)

    IP_adresses = newdata[start_of_additional_records:end_of_additional_records]

    list_of_ip = []
    IP_dump = ''

    i = 1
    flag = True

    for byte in IP_adresses:
        if int(str(bin(byte)), 2) != 1 and i == 4:
            flag = False

        if flag == False:
            if i == 28:
                i = 0
                flag = True
            i += 1

        else:

            if i >= 13 and i <= 16:
                IP_dump += str(int(str(bin(byte)), 2)) + '.'

            if i % 16 == 0:
                IP_dump = IP_dump[:-1]
                list_of_ip.append((IP_dump, 53))
                IP_dump = ''
                i = 0
            i += 1

    print(IP_nameserver)
    randome = random.choice(list_of_ip)
    return randome




def ResultOfQuery(IP_nameserver):                                                                                # Function that grabs the response of a succesfull query
    sock.sendto(ReqNoRQ, IP_nameserver)
    newdata, addr = sock.recvfrom(4096)
    i = 0
    # for byte in newdata:
    #     print(f"Byte : {i}    = {bin(byte)[2:]}")
    #     i+=1

    return newdata


def PickServer(x):
    if x == 1:
       return list_of_RootServers[0].RTT

    return min(list_of_RootServers[x-1].RTT,PickServer(x-1))


def ReqQuery(IP_nameserver):                                                                               # Function to Recursively Query Name Servers until we find an IP address of a domain
    if pick_new == True:
        IP_nameserver = Pick_and_Mark()

    answer = GetAnswer(IP_nameserver)

    if answer > 0:                                    # If the returned errorcode from ErrorCode function equals 0 that means that the query has succesfully retrieved and IP address from a Name Server
        return ResultOfQuery(IP_nameserver)
    else:
        IP_nameserver = GetIP(IP_nameserver)
        return ReqQuery(IP_nameserver)



def BuildReqNoRecursiveQuery(data):                                                                    # Function that changes the RD bit to 0 so the Recursive Query isnt performed by another Name Server

        data = bytearray(data)
        data[2] = set_bit(data[2],0)
        data = bytes(data)

        return data



def Handle():
    global ReqNoRQ
    while True:
        RoundTripTime()
        data, addr = sock.recvfrom(512)
        ReqNoRQ = BuildReqNoRecursiveQuery(data)
        response = ReqQuery(Pick_and_Mark())

        sock.sendto(response,addr)





###########################################################################################################################################################################################

global ReqNoRQ


PORT = 53
SERVER = ''
ADDR = (SERVER, PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                                   # specify type of address we are looking for (IPV4)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                                 # override TIME-WAIT state after shutdown
sock.bind(ADDR)


Handle()
