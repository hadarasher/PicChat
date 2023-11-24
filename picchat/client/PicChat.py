__author__ = 'HadarA'

import wx
from client import Client
import wx.lib.buttons as buttons
import wx.lib.newevent
import sys
import time
import steg1




APP_SIZE_X = 720
APP_SIZE_Y = 700


class Page_Frame(wx.Frame):
    def __init__(self, parent):
        """
        displays entry frame
        """
        self.frame_name="Login"

        self.client = Client(ip="192.168.0.157", port=5555,frame=self)
        self.client.connect_to_server()

        wx.Frame.__init__(self, parent, -1, "PicChat - Login", size=(APP_SIZE_X, APP_SIZE_Y))

        p = wx.Panel(self, -1)

        #creating background pic
        fgs = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        imageFile = 'login_frame.png'
        img1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)

        self.sb1 = wx.StaticBitmap(p, -1, wx.BitmapFromImage(img1), size=(APP_SIZE_X - 100, APP_SIZE_Y))

        fgs.Add(self.sb1)
        p.SetSizerAndFit(fgs)

        self.shape_button('#000035', "WHITE", (150, 420), (300, 60), 1, "Login", self.sb1, fgs)

        self.usrname = wx.TextCtrl(self.sb1, value="Enter Username", pos=(240, 165), size=(240, 30))
        self.usrname.SetMaxLength(10)
        self.passwrd = wx.TextCtrl(self.sb1, value="Password", style=wx.TE_PASSWORD, pos=(240, 295),
                                   size=(240, 30))
        self.passwrd.SetMaxLength(10)

        self.Bind(wx.EVT_BUTTON, self.CheckData, id=1)  #listens to the button and on click do the action

        self.Fit()
        self.Centre()
        self.Show(True)

    def shape_button(self, color1, color2, pos, size, id, string, where_to, add_to):
        """
        shapes a button and presents it on the screen
        """
        b = buttons.GenButton(where_to, id, string, pos, size)
        b.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD, False))
        b.SetBackgroundColour(color1)
        b.SetForegroundColour(color2)
        add_to.Add(b)

    def CheckData(self, event):
        """
        connecting to server
        abd exchanging public keys
        """

        contacts = self.client.check_login(self.usrname.Value, self.passwrd.Value)

        print "usrname: " + self.usrname.Value + " password: " + self.passwrd.Value
        if contacts == ['0']:
            print "user not found...Try again"


        elif len(contacts) > 0:
            #print "special user"
            #print self.contacts_dialog(self.client)
            next_frame = Contacts_Frame(None, self.client, contacts)
            next_frame.Show()
            self.Close()

        """
        elif code == '1':
            print "regular user"
            next_frame = Contacts_Frame(None, self.client)
            next_frame.Show()
            self.Close(True)"""


class Contacts_Frame(wx.Frame):
    def __init__(self, parent, client, contacts):
        """
        displays a chat frame
        """
        self.frame_name="Contacts"

        self.client = client
        self.client.change_Frame(self)
        self.contacts = contacts




        wx.Frame.__init__(self, parent, -1, "PicChat - Login", size=(APP_SIZE_X, APP_SIZE_Y))

        p = wx.Panel(self, -1)

        #creating background pic
        fgs = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        imageFile = 'contacts_frame.png'
        img1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)

        self.sb1 = wx.StaticBitmap(p, -1, wx.BitmapFromImage(img1), size=(APP_SIZE_X - 100, APP_SIZE_Y))

        fgs.Add(self.sb1)
        p.SetSizerAndFit(fgs)

        self.shape_button('#000035', "WHITE", (150, 258), (300, 60), 1, "Contacts", self.sb1, fgs)
        self.shape_button('#000035', "WHITE", (150, 375), (300, 60), 2, "Exit", self.sb1, fgs)

        self.Bind(wx.EVT_BUTTON, self.OnContacts, id=1)  #listens to the button and on click do the action
        self.Bind(wx.EVT_BUTTON, self.OnExit, id=2)  #listens to the button and on click do the action

        self.Fit()
        self.Centre()
        self.Show(True)

    def shape_button(self, color1, color2, pos, size, id, string, where_to, add_to):
        """
        shapes a button and presents it on the screen
        """
        b = buttons.GenButton(where_to, id, string, pos, size)
        b.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD, False))
        b.SetBackgroundColour(color1)
        b.SetForegroundColour(color2)
        add_to.Add(b)

    def contacts_dialog(self):
        """
        opens contacts list
        """
        #self.client = client

        dialog = wx.SingleChoiceDialog(None, "Choose a friend to chat with!", "contacts", self.contacts)
        if dialog.ShowModal() == wx.ID_OK:
            return dialog.GetStringSelection()  #name of user to chat
            #elif dialog.ShowModal()== wx.ID_CANCEL:
            #return "close contacts"
            #next_frame = Page_Frame(None)#not working
            #next_frame.Show()

    def OnContacts(self, event):
        """
        displays contacts frame and close current frame
        """
        contact = self.contacts_dialog()
        next_frame = Chat_Frame(None, self.client, contact)
        next_frame.Show()
        #self.Close()

    def OnExit(self, event):
        """
        close current frame
        """
        self.Close()


class Chat_Frame(wx.Frame):
    def __init__(self, parent, client, contact):
        """
        displays a chat frame
        """
        wx.Frame.__init__(self, parent, -1, "PicChat - Login", size=(APP_SIZE_X, APP_SIZE_Y))
        self.frame_name="Chat"

        self.client = client
        self.client.change_Frame(self)
        self.contact = contact  #other client
        self.massages_other_side = []
        self.massages_self_side = []

        #self.client.get_new_msgs()

        self.index=0



        self.RecvEvent, EVT_RECV = wx.lib.newevent.NewEvent()
        RecvCommandEvent, EVT_COMMAND_RECV=wx.lib.newevent.NewCommandEvent()
        self.Bind(EVT_RECV, self.show_new_msgs)

        self.client.runlistener()




        p = wx.Panel(self, -1)

        #creating background pic
        fgs = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        imageFile = 'chat_frame.png'
        img1 = wx.Image(imageFile, wx.BITMAP_TYPE_ANY)

        self.sb1 = wx.StaticBitmap(p, -1, wx.BitmapFromImage(img1), size=(APP_SIZE_X - 100, APP_SIZE_Y))

        fgs.Add(self.sb1)
        p.SetSizerAndFit(fgs)
        font = wx.Font(20, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        contact_name = wx.StaticText(self.sb1, -1, self.contact, pos=(260, 95), size=(140, 25))
        contact_name.SetFont(font)
        contact_name.SetForegroundColour((0, 0, 49))
        contact_name.SetBackgroundColour((153, 217, 234))


        self.chat_box=wx.ListCtrl(self.sb1, pos=(25, 130),size=(545, 470),style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.chat_box.InsertColumn(0, '',width=545)

        #self.show_new_msgs()




        self.shape_button('#000035', "WHITE", (425, 625), (150, 60), 1, "send", self.sb1, fgs)
        #self.shape_button('#000035', "WHITE", (30, 625), (150, 60), 2, "search", self.sb1, fgs)

        self.massage = wx.TextCtrl(self.sb1, value="Enter text here", pos=(188, 625), size=(230, 60),style=wx.TE_MULTILINE)
        self.massage.SetMaxLength(50)



        self.Bind(wx.EVT_BUTTON, self.send_data, id=1)  #listens to the button "send" and on click do the action

        self.Fit()
        self.Centre()
        self.Show(True)


        #self.client.get_new_msgs()
        #self.show_new_msgs(None)
        #time.sleep(3)


    def add_line(self):
        if len(self.massage.Value)>0:
            line = "You: "+self.massage.Value
            self.chat_box.InsertStringItem(self.index, line)
            self.index+=1

    def show_new_msgs(self,evt):
        if self.contact in self.client.new_msgs.keys():
            if len(self.client.new_msgs[self.contact])>0:
                for msg in self.client.new_msgs[self.contact]:
                    print str(len(msg))
                    for m in msg:
                        print "the msg is :    "+str(len(m))
                        img=steg1.make_img_file(m)
                        print "search stegg"
                        data=steg1.unhide_msg(img)
                        if len(data)>0:
                            line = self.contact+": "+data
                            self.chat_box.InsertStringItem(self.index, line)
                            self.index+=1
        else: print "after show msg"

    def shape_button(self, color1, color2, pos, size, id, string, where_to, add_to):
        """
        shapes a button and presents it on the screen
        """
        b = buttons.GenButton(where_to, id, string, pos, size)
        b.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD, False))
        b.SetBackgroundColour(color1)
        b.SetForegroundColour(color2)
        add_to.Add(b)

    def send_data(self,event):
        """hide the text in the picture and send  the picture"""
        img=steg1.hide_msg("stg.png",self.massage.Value)
        msg=steg1.get_img_data(img)
        print "got sile data "+str(len(msg))
        #msg=self.massage.Value
        #print "mag  "+ msg
        data="MSG|"+str(self.contact)
        data+="|%s"%(msg,)
        print "got after data "+str(len(data))+" "+data[:20]
        self.client.send_with_size(data)
        self.add_line()


if __name__ == '__main__':


    app = wx.App(0)
    frame = Page_Frame(None)
    app.MainLoop()
