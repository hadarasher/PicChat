__author__ = 'HadarA'

import socket
import steg1
import threading
import wx

EWOULDBLOCK = 10035

SIZE_HEADER_FORMAT = "00000000|"
size_header_size = len(SIZE_HEADER_FORMAT)

DEBUG = True




class Client():
    def __init__(self, ip, port,frame):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        #self.state = State_enum.start
        self.kind = 1  #reg
        self.username = None
        self.new_msgs = {}
        self.frame=frame
        self.listener=None

    def get_sock(self):
        """
        returns client's socket
        """
        return self.sock

    def connect_to_server(self):
        """
        connects to server
        """
        try:
            self.sock.connect((self.ip, self.port))
            print "connected to server"
        except socket.error as e:
            "problem connecting to server ,", e

        except Exception as err:
            "problem to connect to server ,", err

    def send_data(self, data):
        self.sock.settimeout(5)

        try:
            self.sock.send(data)
            print "sent >>>>>" + data


        except socket.error as e:
            if e.errno == EWOULDBLOCK or str(e) == "timed out":
                pass

        except Exception as general_err:
            print "General Error - ", general_err.args

    def send_with_size(self, data):
        global SIZE_HEADER_FORMAT
        global size_header_size
        data = str(len(data)).zfill(size_header_size - 1) + "|" + data
        print "before send"
        self.sock.send(data)
        if DEBUG and len(data) < 100:
            print "\nSent>>>" + data
        elif DEBUG:
            print "\nSent>>>" + data[:100]

    def recv_data(self):
        self.sock.settimeout(5)
        try:
            data = self.sock.recv(1024)
            if data != None and len(data) > 0:
                print "recv<<<<<  " + data

                return data
            return ""


        except socket.error as e:
            if e.errno == EWOULDBLOCK or str(e) == "timed out":
                pass


        except Exception as general_err:
            print "General Error - ", general_err.args

    def recv_by_size(self):
        global SIZE_HEADER_FORMAT
        global size_header_size
        str_size = ""
        data_len = 0
        while len(str_size) < size_header_size:
            str_size += self.sock.recv(size_header_size - len(str_size))
            if str_size == "":
                break
        data = ""
        if str_size != "":
            data_len = int(str_size[:size_header_size - 1])
            while len(data) < data_len:
                data += self.sock.recv(data_len - len(data))
                if data == "":
                    break
        if DEBUG and str_size != "" and len(data) < 100:
            print "\nRecv(%s)>>>%s" % (str_size, data)
        elif DEBUG:
            print "\nRecv(%s)>>>%s" % (str_size, data[:100])
        if data_len != len(data):
            data = ""
        return data

    def check_login(self, usrname, passwrd):
        """
        gets username and password and send it to server to check if they are on the lists.
        returns correct or wrong
        """
        self.send_with_size("HELLO|" + usrname + "|" + passwrd + "|" + str(8 + len(usrname) + len(passwrd)))
        data = self.recv_by_size().split("|")
        if data != "":
            print "data: " + str(data)
            print "act: "+data[0]
            if data[0] == "INCORRECT":
                return ['0']
            elif data[0] == "CONTACTS":
                contacts = data[2].split('~')
                return contacts
        return ""

    def get_new_msgs(self):
        self.sock.settimeout(0.1)
        try:
            data = self.recv_by_size()
            if data != None and len(data) > 0:
                data = data.split("|")
                print "new msg: " + str(data)
                if data[0] == "MSG":
                    #msg=data[1].split("$")
                    #print str(msg)
                    #if data[1]!="NONE":

                    if data[1] in self.new_msgs:
                        self.new_msgs[data[1]].append([data[2]])
                    else:
                        self.new_msgs[data[1]] = [[data[2]]]
        except socket.error as e:
            if e.errno == EWOULDBLOCK or str(e) == "timed out":
                pass


        except Exception as general_err:
            print "get_new_msgs General Error - ", general_err.args

    def change_Frame(self,frame):
        self.frame=frame

    def listen(self):
        while True:
            try:
                self.sock.settimeout(1)
                data = self.recv_by_size()
                if data != "":
                    index0=data.find("|")
                    data0=data[:index0]
                    print "act is: "+data0
                    #print "new msg: " + str(data)
                    if data0 == "MSG":
                        #msg=data[1].split("$")
                        index1=data.find("|",index0+1)
                        data1=data[index0:index1][1:]
                        print str(len(data1))
                        data2=data[index1:][1:]
                        print "data1 is: "+data1
                        if data1 in self.new_msgs.keys():
                            self.new_msgs[data1].append([data2])
                        else:
                            self.new_msgs[data1] = [[data2]]
                        #enter data to dict by user
                        evt = self.frame.RecvEvent()
                        wx.PostEvent(self.frame, evt)

                else:
                    #self.msg.Append("No Connection")
                    break
            except socket.error as e:
                if e.errno == 10035 or str(e) == "timed out":
                    continue
                print "Listner exit sock exception"
                break
            except Exception as e:
                print e.args
                print "Listner exit"
                break

    def runlistener(self):
        self.listener=threading.Thread(target=self.listen)
        self.listener.start()

    def get_all_contacts(self):
        """
        returns a list of all usrs form the same kind without itself
        """
        if self.kind == 1:
            user = reg_users
        else:  # self.kind == 2:
            user = spcl_users

        contacts = []

        for c in user.keys():
            if c != self.username:
                contacts.append(c)

        return contacts

    def get_users(self, kind):  #for server
        """
        reads from file the users by kind and saves in a list
        """
        users = {}
        if kind == 1:
            file_name = "reg_users.txt"
        else:  #kind is special
            file_name = "spcl_users.txt"
        with open(file_name) as f:
            usrs = f.read().split('|\n')
            for u in usrs:
                u = u.split('~')  #0-username, 1-password
                users[u[0]] = u[1]
        return users



