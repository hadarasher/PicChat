__author__ = 'HadarA'

import socket
import threading
from sys import argv
import time
#from Crypto_DH import Crypto_DH as dh

#socket errors
EWOULDBLOCK = 10035
EINPROGRESS = 10036
EALREADY = 10037
ECONNRESET = 10054
ENOTCONN = 10057
ESHUTDOWN = 10058
WSAECONNABORTED = 10053

SIZE_HEADER_FORMAT = "00000000|"
size_header_size = len(SIZE_HEADER_FORMAT)
DEBUG=True

change_total_clients = threading.Lock()
reg_usrs = {}
spcl_usrs = {}
reg_contacts=""
spcl_contacts=""
async_msgs={}


to_close_after_send=False

def make_contacts_lists_str():
    """
    make lists of contact by type from dictionaries
    """
    global reg_usrs
    global spcl_usrs
    global reg_contacts
    global spcl_contacts
    global async_msgs

    for key in reg_usrs.keys():
        #reg_contacts.append(key)
        reg_contacts+="~"+key
    reg_contacts=reg_contacts[1:]

    for key in spcl_usrs.keys():
        #spcl_contacts.append(key)
        async_msgs[key]=[] #for  keeping asyc msgs to be sent when contact is connected
        spcl_contacts+="~"+key
    spcl_contacts=spcl_contacts[1:]

    print spcl_contacts


def read_users_from_file():
    """
    read names and password of all users from the same kind.
    """
    global reg_usrs
    global spcl_usrs

    with open("spcl_users.txt", "r") as f:
        f = f.read()
        usrs = f.split("|\n")

        for i in usrs:
            i = i.split('~')
            spcl_usrs[i[0]]=i[1]
    with open("reg_users.txt", "r") as f:
        f = f.read()
        usrs = f.split("|\n")

        for i in usrs:
            i = i.split("~")
            reg_usrs[i[0]] = i[1]

    make_contacts_lists_str()

def check_if_user_exist(username,password):
    return spcl_usrs[username]==password

class ClientThread(threading.Thread):
    global all_socks
    global total_clients

    def __init__(self, ip, port, sock, tid):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = sock
        self.tid = tid
        self.type=0#reg
        self.contact_name="unknown"


    def send_data(self, data):
        self.conn.settimeout(5)

        try:
            self.conn.send(data)
            print "sent >>>>>" + data


        except socket.error as e:
            if e.errno == EWOULDBLOCK or str(e) == "timed out":
                pass

        except Exception as general_err:
            print "General Error - ", general_err.args

    def send_with_size (self,data):
        data = str(len(data)).zfill(size_header_size - 1) + "|" + data
        self.conn.send(data)
        if DEBUG and len(data) < 100:
              print "\nSent>>>"+data
        elif DEBUG:
            print "\nSent>>>"+data[:100]

    def recv_data(self):
        self.conn.settimeout(10)
        try:
            data = self.conn.recv(4096)
            if len(data)>0:
                print "recv<<<<<  " + data

                return data

        except socket.error as e:
            if e.errno == EWOULDBLOCK or str(e) == "timed out":
                pass


        except Exception as general_err:
            print "General Error - ", general_err.args

    def recv_by_size (self):
        str_size = ""
        data_len = 0
        while len(str_size) < size_header_size:
            str_size += self.conn.recv(size_header_size - len(str_size))
            if str_size == "":
                break
        data  = ""
        if str_size != "":
            data_len = int(str_size[:size_header_size - 1])
            while len(data) < data_len:
                data += self.conn.recv(data_len - len(data))
                if data == "":
                    break
        if DEBUG and str_size !="" and len(data) < 100 :
            print "\nRecv(%s)>>>%s"%(str_size, data)
        elif DEBUG:
            print "\nRecv(%s)>>>%s"%(str_size, data[:100])
        if data_len != len(data):
            data=""
        return data


    def run(self):
        global reg_usrs
        global spcl_usrs
        global reg_contacts
        global spcl_contacts

        global async_msgs

        global total_clients
        global change_total_clients
        global father_going_to_close
        global  to_close_after_send

        father_going_to_close = False
        with change_total_clients:
            total_clients += 1

        print "New Thread, New connection from : " + self.ip + " on port: " + str(self.port)
        self.conn.settimeout(10)

        while True:
            try:


                data = self.recv_by_size()
                if data ==  "" :
                    print "\nSeems Client disconnected. So now exit main loop"
                    break

                #else:


                data0=data.find("|")
                print data[:data0]


                if data[:data0]=="HELLO":
                    index1=data.find("|",data0+1)
                    index2=data.find("|",index1+1)
                    print "indexxx ",index1,index2
                    data1=data[data0:index1][1:]
                    data2=data[index1:index2][1:]
                    print "data1: "+data1
                    print "data2: "+data2
                    if spcl_usrs[data1]==data2:
                        print "user exists"
                        self.contact_name=data1
                        self.send_with_size("CONTACTS|2|"+spcl_contacts)
                        if self.contact_name in async_msgs.keys():
                            if len(async_msgs[self.contact_name])>0:
                                for msg in async_msgs[self.contact_name]:
                                    #msg=msg.split("$")
                                    print "hhhhhhh"+data1
                                    print "ssssss"+self.contact_name
                                    self.send_with_size("MSG|"+data1+"|"+msg)
                                    time.sleep(5)
                                async_msgs[self.contact_name]=[]
                            #else:
                                #self.send_with_size("MSG|NONE")

                elif data[:data0]=="MSG":
                    index1=data.find("|",data0+1)
                    print "indexxx ",index1
                    data1=data[data0:index1][1:]
                    data2=data[index1:][1:]
                    print "data1: "+data1
                    if data1 in async_msgs.keys():

                        async_msgs[self.contact_name].append(data2)
                        print "sent from "+self.contact_name+" to: "+data1
                        print "done"




                if to_close_after_send:
                    break

            except socket.error as e:
                if e.errno == ECONNRESET:  #'Connection reset by peer'
                    print "Error %s - Seems Client Disconnect. try Accept new Client " % e.errno
                    break
                elif e.errno == EWOULDBLOCK or str(e) == "timed out":  # if we use conn.settimeout(x)
                    if father_going_to_close:
                        print "Father Going To Die"
                        self.conn.close()
                        break
                    print ",",
                    continue
                else:
                    print "Unhandled Socket error at recv. Server will exit %s " % e
                    break
            except Exception as general_err:
                print "General Error - ", general_err.args
                break

        print "Client disconnected..."
        print "Before close son socket - total clients = %d (%d)" % (how_many_clients(), total_clients)
        with change_total_clients:
            total_clients -= 1

        self.conn.close()


def how_many_clients():
    return threading.activeCount() - 1


def main(ip, port):
    global reg_usrs
    global spcl_usrs

    read_users_from_file()

    sock = socket.socket()
    sock.bind(('0.0.0.0', port))

    print "after bind to " + ip + " port: " + str(port)

    sock.listen(20)
    print "after listen"

    global total_clients
    total_clients = 0
    threads = []
    tid = 0
    global all_socks
    all_socks = {}

    cnt = 0
    while True:
        try:
            if total_clients <= 10:
                sock.settimeout(10)
                (conn, (ip, port)) = sock.accept()
                print "\n new client\n"
                tid += 1

                new_thread = ClientThread(ip, port, conn, tid)
                new_thread.start()

                print "Clients = %d (%d) " % (how_many_clients(), total_clients)
                threads.append(new_thread)
            else:
                print "can't accept more clients"
                break

        except socket.error as e:
            if e.errno == EWOULDBLOCK or str(e) == "timed out":  # if we use conn.settimeout(x)
                cnt += 1
                print "#\n" if cnt % 10 == 0 else ',',
                continue

        except Exception as err:
            print "General Error at Main Accept loop - ", err.args
            break

        except KeyboardInterrupt:
            print "\nGot ^C Main\n"
            father_going_to_close = True

    print "Server Says: Bye Bye ...."
    for t in threads:
        t.join()

    sock.close()


if __name__ == '__main__':
    try:
        if len(argv) < 2:
            print "Enter <ip> <port>"
            exit()
        else:
            ip = argv[1]
            port = int(argv[2])
            main(ip, port)

    except KeyboardInterrupt:
        print "\nGot ^C Main\n"
        father_going_to_close = True

