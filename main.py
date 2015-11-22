#!/usr/bin/python
import cmd
import locale
import os
import pprint
import shlex
import webbrowser
import platform
import ctypes
ID_NEW = 1
ID_RENAME = 2
ID_CLEAR = 3
ID_DELETE = 4


from dropbox import client, rest, session
from sqlite3 import connect
from mega import Mega
import wx.lib.buttons as buttons
import wx
import wx.lib.agw.gradientbutton as GB
import wx.lib.agw.aquabutton as AB

import glob
import sys
import ntpath
 
#wildcard = "Python source (*.py; *.pyc)|*.py;*.pyc|" \
 #        "All files (*.*)|*.*"
wildcard ="All files (*.*)|*.*"

# XXX Fill in your consumer key and secret below
# You can find these at http://www.dropbox.com/developers/apps
APP_KEY = 'y56kqnsy5cffhzb'
APP_SECRET = '8q2c4e3w6kkdjwv'
ACCESS_TYPE = 'dropbox'  # should be 'dropbox' or 'app_folder' as configured for your app

class LeftPanel(wx.Panel):
       def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour("#83ACAC")
        t = wx.StaticText(self, -1, "SPLIT WINDOW ", (40,15))
        font = wx.Font(20,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)
        t.SetFont(font)
        self.pos=200
        self.var=0
        self.flist=[]
        self.cur=0
        self.lfolder=[]
        self.top=0
        self.bremain=0
        self.done=0
        self.t=[]
        self.ind=0
        
        #-----------------------------------------------------merge-split-----------
        openf = GB.GradientButton(self,label="Select File",pos=(20, 100))
        openf.Bind(wx.EVT_BUTTON, self.onOpenFile)
        self.fval = wx.TextCtrl(self, -1, "",pos=(200, 100),size=(400,30))
        #split = AB.AquaButton(self, label="split",pos=(300, 400),size=(180,110))
        # big size=(180,110)
        split = GB.GradientButton(self, label="copy",pos=(300, 400),size=(90,40))
        split.Bind(wx.EVT_BUTTON, self.split)
        
        dirDlgBtn = GB.GradientButton(self, label="select drive",pos=(20,200))
        dirDlgBtn.Bind(wx.EVT_BUTTON, self.onDir)
        

       def folderadd(self):
        
        self.pos=self.pos+40
        
        self.lfolder.append(self.folder)
        self.top=self.top+1

        if self.done==1:
         for i in range(len(self.t)):
          self.t[i].SetLabel("")
         self.done=0
         self.t.append(wx.StaticText(self, -1, "Drive  "+self.folder+" is added", pos=(100,self.pos)))
        else:
          self.t.append(wx.StaticText(self, -1, "Drive  "+self.folder+" is added...", pos=(100,self.pos)))
        
        self.t[self.ind].SetForegroundColour((255,255,255)) # set text color
        self.ind=self.ind+1

       def fileadd(self):
        self.fval=wx.TextCtrl(self, -1, self.paths,pos=(200, 100),size=(400,30))
    
       

       def foldradd(self):
        self.folval=wx.TextCtrl(self, -1, self.paths,pos=(200, 100),size=(400,30))
        
        self.top=self.top+1
        self.lfolder.append(self.folder)
        self.pos=self.pos+40
        
        self.t.append(wx.StaticText(self, -1, "Drive  "+self.folder+" is added...", pos=(100,self.pos))) 
        self.t[self.ind].SetForegroundColour((255,255,255)) # set text color
        self.ind=self.ind+1

#------------------------split with get space----------------------

       def get_free(self,folder):
    
         if platform.system() == 'Windows':
           free_bytes = ctypes.c_ulonglong(0)
           ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
           return free_bytes.value
         else:
           st = os.statvfs(folder)
           
           return st.f_bavail * st.f_frsize

       def split(self,event):
        #for path in self.paths:
        self.pos=250
        for i in range(len(self.t)): 
         self.t[i].SetLabel("")
        file0=self.fval.GetValue()
        base=ntpath.basename(file0)
        f=open(file0,"rb")
        b = os.path.getsize(file0)
        bremain=b
        size=0
        cdfs=0
        i=0
        while bremain>0:
          if self.cur<self.top:
                
             cdfs=self.get_free(self.lfolder[self.cur]) - 30
             
             if cdfs>0:
                if cdfs>=bremain:
                   size=bremain
                    
                else:
                   size=cdfs
                
                f1=open(self.lfolder[self.cur]+"/" + base +"."+ str(self.cur).zfill(5) + ".scloud","wb")
                self.t.append(wx.StaticText(self, -1, "Copied to"+self.lfolder[self.cur], pos=(100,self.pos)))
                self.t[self.ind].SetForegroundColour("green")
                self.ind=self.ind+1
                self.pos=self.pos+40 
                x=f.read(size)
                f1.write(x)
                f1.close()
                
                bremain=bremain - size
                
                self.cur=self.cur+1
          else:
                
                self.onDiradd()
                
                
          
            
        f.close()
        if (bremain==0): 
         dial=wx.MessageDialog(None, 'Finished copying', 'copy', wx.OK)
         dial.ShowModal()     
        self.cur=0
        self.top=0
        self.lfolder=[]
        self.done=1
        self.pos=200
        

        
       
             
            
       def onOpenFile(self, event):
        """
        Create and show the Open FileDialog
        """
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            x = dlg.GetPaths()
            self.paths=x[0]
            self.fileadd()    
        dlg.Destroy()

       def onDir(self, event):
        """
        Show the DirDialog and print the user's choice to stdout
        """
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.folder=dlg.GetPath()
            self.folderadd()
        dlg.Destroy()

       def onDiradd(self):
        """
        Show the DirDialog and print the user's choice to stdout
        """
        self.top=1 
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.folder=dlg.GetPath()
            self.foldradd()
        dlg.Destroy()  
      
            
     #----------------------------------------------------------------------
               


class RightPanel(wx.Panel):
       def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.SetBackgroundColour("#83ACAC")
        t = wx.StaticText(self, -1, "MERGE WINDOW ", (40,20))
        font = wx.Font(20,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)
        t.SetFont(font)
        self.folval=wx.TextCtrl(self, -1,'',pos=(200, 100),size=(400,30))
        #bground=wx.Image("e:\new.jpg",wx.BITMAP_TYPE_ANY)
        #bground.Rescale
        #bgroungbitmap=wx.StaticBitmap(self,-1,wx.BitmapFromImage(bground))

     #   imageFile="e:\new.jpg"
      #  image1= wx.Image(imageFile,wx.BITMAP_TYPE_ANY).ConvertToBitmap()
       # self.button1=wx.BitmapButton(self,id=-1,bitmap=image1) 
        #big size=(180,110)    
        merge = GB.GradientButton(self, label="merge",pos=(100, 400),size=(90,40))
           #self.text_folder = wx.TextCtrl(panel, -1, "",pos=(20, 200))
        merge.Bind(wx.EVT_BUTTON, self.merge)

        dirDlgBtn = GB.GradientButton(self, label="select folder",pos=(50,100))
        dirDlgBtn.Bind(wx.EVT_BUTTON, self.onDir)

       def merge(self,event):
           if platform.system() == 'Windows':
            self.folder=self.folval.GetValue()+"\\"
           else:
            self.folder=self.folval.GetValue()+"/" 
           files=glob.glob(self.folder + "*.scloud")
	   files.sort()
           
           j=files[0].split('.')
           f1=j[0]
           for o in j[1:-2]:
             f1=f1+'.'+o
           of=open(f1,"wb")
           cur=f1
           for file1 in files:
              f=open(file1,"rb")
              x=f.read(os.path.getsize(file1))
              f.close()
              j=file1.split('.')
              f1=j[0]
              for o in j[1:-2]:
                 f1=f1+'.'+o
              if(cur!=f1):
                 cur=f1
                 of.close()
                 of=open(f1,"wb")
              os.remove(file1)
              of.write(x)
           of.close()
           dial=wx.MessageDialog(None, 'Finished merging', 'merge', wx.OK)
           dial.ShowModal() 
         
       def onDir(self, event):
        """
        Show the DirDialog and print the user's choice to stdout
        """
        dlg = wx.DirDialog(self, "Choose a directory:",
                           style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            self.folder=dlg.GetPath()
        dlg.Destroy() 
        self.foldadd()

       def foldadd(self):
        self.folval=wx.TextCtrl(self, -1, self.folder,pos=(200, 100),size=(400,30))
 
class FlashDrive(wx.Panel):
       def __init__(self, parent):
           wx.Panel.__init__(self, parent)
           self.SetBackgroundColour("#400000") 
           
   
           
           #panel = wx.Panel(self, -1)
	   self.rightPanel = RightPanel(self, -1)
	   leftPanel = LeftPanel(self, -1)
	   hbox = wx.BoxSizer()
	   hbox.Add(leftPanel, 1, wx.EXPAND | wx.ALL, 5)
	   hbox.Add(self.rightPanel, 1, wx.EXPAND | wx.ALL, 5)
	   self.SetSizer(hbox)
            
     #----------------------------------------------------------------------
class ListBox(wx.Frame):
 def __init__(self, parent, id, title):
  wx.Frame.__init__(self, parent, id, title, size=(350, 220))
  
  panel = wx.Panel(self, -1)
  hbox = wx.BoxSizer(wx.HORIZONTAL)
  self.listbox = wx.ListBox(panel, -1)
  hbox.Add(self.listbox, 1, wx.EXPAND | wx.ALL, 20)
  btnPanel = wx.Panel(panel, -1)
  vbox = wx.BoxSizer(wx.VERTICAL)
  download = wx.Button(btnPanel, ID_NEW, 'Download', size=(90, 30))
  #new = wx.Button(btnPanel, ID_NEW, 'New', size=(90, 30))
  self.Bind(wx.EVT_BUTTON, self.NewItem, id=ID_NEW)
  #self.Bind(wx.EVT_BUTTON, self.NewItem, id=ID_NEW)

  #self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnRename)
  vbox.Add((-1, 20))
  vbox.Add(download)
  #vbox.Add(new, 0, wx.TOP, 5)
#-----------------data base display-------------------
  if platform.system() == 'Windows':
   con=connect("c:\python27\master_cloud.db")
  else:
   con=connect("/home/koshik/master_cloud.db")
  cur=con.cursor()
  cur.execute('select fname from main')
  t=cur.fetchall()
  for text in t:
    self.listbox.Append(text[0])
#---------------------------------------------------------
  btnPanel.SetSizer(vbox)
  hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
  panel.SetSizer(hbox)
  self.Centre()
  self.Show(True)
 #def NewItem(self, event):
   
 def NewItem(self, event):
  term = DropboxTerm(APP_KEY, APP_SECRET)
  meg=Megacloud() 
  sel = self.listbox.GetSelection()
  text = self.listbox.GetString(sel)
  if platform.system() == 'Windows':
   con=connect("c:\python27\master_cloud.db")
  else:
   con=connect("/home/koshik/master_cloud.db") 
  cur=con.cursor()
  cur.execute('select fid from main where fname="%s"' % text)
  t=cur.fetchone()  
  
  cur.execute('select splits from split where fid="%d" and cloud="dropbox"' % t[0] )
  t1=cur.fetchall()
  cur.execute('select splits from split where fid="%d" and cloud="mega"' % t[0] )
  t2=cur.fetchall()
  for s in t1:
    n="/"+s[0]
    print n
    term.do_get(n,s[0])
  for s in t2:
    n=s[0]
    print n
    meg.do_get(s[0])
  self.mergec()
 def mergec(self):
           if platform.system() == 'Windows':
            self.folder="c:\python27\\"
           else:
            self.folder="/home/koshik/" 
           files=glob.glob(self.folder + "*.scloud")
	   files.sort()
           
           j=files[0].split('.')
           f1=j[0]
           for o in j[1:-2]:
             f1=f1+'.'+o
           of=open(f1,"wb")
           cur=f1
           for file1 in files:
              f=open(file1,"rb")
              x=f.read(os.path.getsize(file1))
              f.close()
              j=file1.split('.')
              f1=j[0]
              for o in j[1:-2]:
                 f1=f1+'.'+o
              if(cur!=f1):
                 cur=f1
                 of.close()
                 of=open(f1,"wb")
              os.remove(file1)
              of.write(x)
           of.close()
           dial=wx.MessageDialog(None, 'Finished downloading', 'download', wx.OK)
           dial.ShowModal()
   
  
  #self.listbox.Delete(sel)
  #self.listbox.Insert(renamed, sel)
 def OnDelete(self, event):
  sel = self.listbox.GetSelection()
  if sel != -1:
   self.listbox.Delete(sel)
 def OnClear(self, event):
  self.listbox.Clear()
              
class Cloud(wx.Panel):
       def __init__(self, parent):
           
           self.paths=""
           wx.Panel.__init__(self, parent)
           self.SetBackgroundColour("#400000") 
           self.SetBackgroundColour("#83ACAC")
           
           t1 = wx.StaticText(self, -1, "Select a file to upload ", (40,20))
           t2 = wx.StaticText(self, -1, "Select a file to download ", (700,360))   
           t1.SetForegroundColour((255,255,255))
           t2.SetForegroundColour((255,255,255)) 
           font = wx.Font(15,wx.FONTFAMILY_MODERN,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)
           t1.SetFont(font)
           t2.SetFont(font) 
           bmpu = wx.Bitmap("Cloudupload.png", wx.BITMAP_TYPE_ANY)
           bmpup = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpu,
                                  size=(bmpu.GetWidth()+10, bmpu.GetHeight()+10),pos=(30,50))
           #genBmapBtn1 = buttons.GenBitmapButton(self, bitmap=bmpu)
           bmpup.Bind(wx.EVT_BUTTON, self.do_put) 
           bmpd = wx.Bitmap("Clouddownload.png", wx.BITMAP_TYPE_ANY)
           bmpdown = wx.BitmapButton(self, id=wx.ID_ANY, bitmap=bmpd,
                                  size=(bmpd.GetWidth()+10, bmpd.GetHeight()+10),pos=(700,400))
           #+++genBmapBtn2 = buttons.GenBitmapButton(self, bitmap=bmpd)
           bmpdown.Bind(wx.EVT_BUTTON, self.do_get)
           

           
         
       
         
     
         
       def do_get(self,event):
        ListBox(None, -1, 'Download')  

       def do_put(self,event):
        """
        Copy local file to Dropbox

        Examples:
        Dropbox> put ~/test.txt dropbox-copy-test.txt

        """
        term = DropboxTerm(APP_KEY, APP_SECRET)
        meg = Megacloud()
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            x = dlg.GetPaths()
            self.paths=x[0]
                
        dlg.Destroy()
        #term.from_path=self.paths
        #term.to_path='/'+ntpath.basename(term.from_path) 

      #---------------------------------split code--------------------
        
        file0=self.paths
        if file0!='':
        
         base=ntpath.basename(file0)
         f=open(file0,"rb")
         b = os.path.getsize(file0)
         bremain=b
         size=102400
	 i=0
	 self.filel=[]
         while bremain>0:
	   i+=1
           if bremain<size:
		size=bremain        
           f1=open(file0 +"."+ str(i).zfill(5) + ".scloud","wb")
           self.filel.append(file0 +"."+ str(i).zfill(5) + ".scloud")
           x=f.read(size)
           f1.write(x)
           f1.close()
	   bremain-=size
           
         f.close()
         self.filel1=[]
         self.filel2=[]
         r=0
         for files in self.filel:
          r=r+1
          if r%2==0:       
            self.filel1.append(files)
          else:
            self.filel2.append(files)
       
         if platform.system() == 'Windows':
           con=connect("c:\python27\master_cloud.db")
         else:
           con=connect("/home/koshik/master_cloud.db")
         cur=con.cursor() 
         cur.execute("select max(fid) from main")
         t=cur.fetchone()
         temp=t[0]
         temp=temp+1
           
         
         e=cur.execute('insert into main(fid,fname) values(?,?)',(temp,base)) 
         for i in self.filel1:
            cur.execute('insert into split(fid,splits,cloud) values(?,?,?)',(temp,ntpath.basename(i),"dropbox")) 
         
         for i in self.filel2:
            cur.execute('insert into split(fid,splits,cloud) values(?,?,?)',(temp,ntpath.basename(i),"mega"))
         con.commit()
         con.close()                  
         term.do_put(self.filel1)
         meg.do_put(self.filel2)
         dial=wx.MessageDialog(None, 'Finished uploading', 'upload', wx.OK)
         dial.ShowModal()
            
             
        #openfn = wx.Button(self,label="upload",pos=(40, 80))
           
        #openfn.Bind(wx.EVT_BUTTON, term.do_put)
        

       

'''
       def onOpenFile(self, event):
        """
        Create and show the Open FileDialog
        """
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            x = dlg.GetPaths()
            self.paths=x[0]
                
        dlg.Destroy()
   '''    
class Megacloud:
    def do_put(self,filel):
      mega = Mega()
      m = mega.login('vinay_rghvn@yahoo.co.in','raghavan')
      self.filel=filel
      for i in self.filel:
       try:
        file1 = m.upload(i)
       except:
        file1 = m.upload(i)
       os.remove(i)
    def do_get(self,filel):
      mega = Mega()
      m = mega.login('vinay_rghvn@yahoo.co.in','raghavan')
      self.file=filel
      try:
        file1=m.find(self.file)
        m.download(file1)
      except:
        file1=m.find(self.file)
        m.download(file1)
class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,"smart cloud",size=wx.DisplaySize())
        # Here we create a panel and a notebook on the panel
        
        p = wx.Panel(self)
        nb = wx.Notebook(p)
        
           # create the page windows as children of the notebook
        fd = FlashDrive(nb)
        cd = Cloud(nb)
        
  
           # add the pages to the notebook with the label to show on the tab
        nb.AddPage(fd, "Flash Drive")
        nb.AddPage(cd, "Cloud Drive")
        
   
           # finally, put the notebook in a sizer for the panel to manage
           # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        #self.SetBackgroundColour("yellow")
        #term = DropboxTerm(APP_KEY, APP_SECRET)
     
        
        # Setting up the menu.
        loginmenu= wx.Menu()
  
        # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided 
        dropbox=loginmenu.Append(wx.ID_EXIT, "&dropbox","dropbox")
        mega=loginmenu.Append(-1, "&mega"," mega cloud")
        google_drive=loginmenu.Append(-1, "&google drive"," google drive")
        #loginmenu.AppendSeparator()
        exit=loginmenu.Append(wx.ID_EXIT,"&Exit"," Terminate the program")
   
           # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(loginmenu,"&login") # Adding the "filemenu" to the
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        #self.Bind(wx.EVT_MENU, term.do_login,dropbox)
        #self.Bind(wx.EVT_MENU, self.OnExit,exit)

        login= wx.Button(p, label="login",pos=(20, 50))
        #login.Bind(wx.EVT_BUTTON, term.do_login)



    #def OnExit(self,e):
     #    self.Close(True)

    
   
        
        
class DropboxTerm(cmd.Cmd):
    def __init__(self, app_key, app_secret):
        cmd.Cmd.__init__(self)
        
        self.sess = StoredSession(app_key, app_secret, access_type=ACCESS_TYPE)
        self.api_client = client.DropboxClient(self.sess)
        self.current_path = ''
        #self.prompt = "Dropbox> "

        self.sess.load_creds()
       

   
    def do_ls(self):
        """list files in current remote directory"""
        resp = self.api_client.metadata(self.current_path)

        if 'contents' in resp:
            for f in resp['contents']:
                name = os.path.basename(f['path'])
                encoding = locale.getdefaultlocale()[1]
                self.stdout.write(('%s\n' % name).encode(encoding))

    
    def do_cd(self, path):
        """change current working directory"""
        if path == "..":
            self.current_path = "/".join(self.current_path.split("/")[0:-1])
        else:
            self.current_path += "/" + path

    
    def do_login(self,event):
        """log in to a Dropbox account"""
        try:
            self.sess.link()
        except rest.ErrorResponse, e:
            self.stdout.write('Error: %s\n' % str(e))

    
    def do_logout(self):
        """log out of the current Dropbox account"""
        self.sess.unlink()
        self.current_path = ''

    
    def do_cat(self, path):
        """display the contents of a file"""
        f, metadata = self.api_client.get_file_and_metadata(self.current_path + "/" + path)
        self.stdout.write(f.read())
        self.stdout.write("\n")

    
    def do_mkdir(self, path):
        """create a new directory"""
        self.api_client.file_create_folder(self.current_path + "/" + path)

    
    def do_rm(self, path):
        """delete a file or directory"""
        self.api_client.file_delete(self.current_path + "/" + path)

    
    def do_mv(self, from_path, to_path):
        """move/rename a file or directory"""
        self.api_client.file_move(self.current_path + "/" + from_path,
                                  self.current_path + "/" + to_path)

    
    def do_account_info(self):
        """display account information"""
        f = self.api_client.account_info()
        pprint.PrettyPrinter(indent=2).pprint(f)

  
    def do_exit(self):
        """exit"""
        return True

    
    def do_get(self, from_path, to_path):
        """
        Copy file from Dropbox to local file and print out out the metadata.
        print from_path
        print to_path  
        Examples:
        Dropbox> get file.txt ~/dropbox-file.txt
        """
        to_file = open(os.path.expanduser(to_path), "wb")
        
        f= self.api_client.get_file(from_path)
        #print 'Metadata:', metadata
        to_file.write(f.read())

    
    def do_thumbnail(self, from_path, to_path, size='large', format='JPEG'):
        """
        Copy an image file's thumbnail to a local file and print out the
        file's metadata.

        Examples:
        Dropbox> thumbnail file.txt ~/dropbox-file.txt medium PNG
        """
        to_file = open(os.path.expanduser(to_path), "wb")

        f, metadata = self.api_client.thumbnail_and_metadata(
                self.current_path + "/" + from_path, size, format)
        #print 'Metadata:', metadata
        to_file.write(f.read())

    
    def do_put(self,filel):
        """
        Copy local file to Dropbox

        Examples:
        Dropbox> put ~/test.txt dropbox-copy-test.txt
        """
        self.filel=filel
        for i in self.filel:

          self.to_path='/'+ntpath.basename(i) 
          self.from_path=i
          self.from_file = open(os.path.expanduser(self.from_path), "rb")
   
          #self.api_client.put_file(self.current_path + "/" + self.to_path, self.from_file)
        
          self.api_client.put_file(self.to_path, self.from_file)
          self.from_file.close()
          os.remove(i)


    
    def do_search(self, string):
        """Search Dropbox for filenames containing the given string."""
        results = self.api_client.search(self.current_path, string)
        for r in results:
            self.stdout.write("%s\n" % r['path'])

  
    def do_help(self):
        # Find every "do_" attribute with a non-empty docstring and print
        # out the docstring.
        all_names = dir(self)
        cmd_names = []
        for name in all_names:
            if name[:3] == 'do_':
                cmd_names.append(name[3:])
        cmd_names.sort()
        for cmd_name in cmd_names:
            f = getattr(self, 'do_' + cmd_name)
            if f.__doc__:
                self.stdout.write('%s: %s\n' % (cmd_name, f.__doc__))

    # the following are for command line magic and aren't Dropbox-related
    def emptyline(self):
        pass

    def do_EOF(self, line):
        self.stdout.write('\n')
        return True

    def parseline(self, line):
        parts = shlex.split(line)
        if len(parts) == 0:
            return None, None, line
        else:
            return parts[0], parts[1:], line


class StoredSession(session.DropboxSession):
    """a wrapper around DropboxSession that stores a token to a file on disk"""
    TOKEN_FILE = "/home/koshik/token_store.txt"

    def load_creds(self):
        try:
            stored_creds = open(self.TOKEN_FILE).read()
            self.set_token(*stored_creds.split('|'))
            print "[loaded access token]"
        except IOError:
            pass # don't worry if it's not there

    def write_creds(self, token):
        f = open(self.TOKEN_FILE, 'w')
        f.write("|".join([token.key, token.secret]))
        f.close()

    def delete_creds(self):
        os.unlink(self.TOKEN_FILE)

    def link(self):
        request_token = self.obtain_request_token()
        url = self.build_authorize_url(request_token)
        webbrowser.open_new_tab(url)
        
        raw_input()

        self.obtain_access_token(request_token)
        self.write_creds(self.token)

    def unlink(self):
        self.delete_creds()
        session.DropboxSession.unlink(self)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()
