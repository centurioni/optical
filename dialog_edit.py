import wx
from os import path

def lbox(label,oggetto,pannello):
    sizer = wx.StaticBoxSizer(wx.StaticBox(pannello,-1,label),wx.HORIZONTAL)
    sizer.Add(oggetto,1)
    return sizer

class EditDialog(wx.Dialog):
    def __init__(self,parent):
        wx.Dialog.__init__(self, None, -1, "Edit multilayer")
        self.parent=parent
        self.multilayer=parent.multilayer
        self.CurDir=parent.CurDir
        self.IndexDir=parent.IndexDir
        self.btn_insert = wx.Button(self, -1, 'Insert')
        self.btn_insert.Bind(wx.EVT_BUTTON, self.on_btn_insert)
        self.btn_remove = wx.Button(self, -1, 'Remove')
        self.btn_remove.Bind(wx.EVT_BUTTON, self.on_btn_remove)
        self.txt_name = wx.TextCtrl(self)
        self.txt_thickness = wx.TextCtrl(self)
        self.txt_roughness = wx.TextCtrl(self)
        self.ch_layer = wx.Choice(self)
        self.Bind(wx.EVT_CHOICE, self.on_ch_layer, self.ch_layer)
        self.CheckBox_incoherent = wx.CheckBox(self,-1,label="Incoherent")
        self.txt_fr1 = wx.TextCtrl(self)
        self.txt_file1 = wx.TextCtrl(self)
        self.btn_file1 = wx.Button(self, -1,"Browse")
        self.btn_file1.Bind(wx.EVT_BUTTON, self.on_btn_file1)
        self.txt_fr2 = wx.TextCtrl(self)
        self.txt_file2 = wx.TextCtrl(self)
        self.btn_file2 = wx.Button(self, -1,"Browse")
        self.btn_file2.Bind(wx.EVT_BUTTON, self.on_btn_file2)
        self.txt_fr3 = wx.TextCtrl(self)
        self.txt_file3 = wx.TextCtrl(self)
        self.btn_file3 = wx.Button(self, -1,"Browse")
        self.btn_file3.Bind(wx.EVT_BUTTON, self.on_btn_file3)
        self.txt_multi_name = wx.TextCtrl(self)
        
        self.txt_name.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_thickness.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_roughness.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_fr1.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_fr2.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_fr3.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_file1.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_file2.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_file3.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.txt_multi_name.Bind(wx.EVT_KILL_FOCUS, self.update_multilayer)
        self.Bind(wx.EVT_CHECKBOX, self.update_multilayer, self.CheckBox_incoherent)

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbox("Select layer",self.ch_layer,self),1,wx.ALL,3)
        sizer.Add(self.btn_insert,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_remove,0,wx.ALIGN_CENTER|wx.ALL,3)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbox("Name",self.txt_name,self),0,wx.ALL,3)
        sizer.Add(lbox("Thickness (nm)",self.txt_thickness,self),0,wx.ALL,3)
        sizer.Add(lbox("Roughness (nm)",self.txt_roughness,self),0,wx.ALL,3)
        sizer.Add(self.CheckBox_incoherent,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)
        
        mainsizer.Add((20, 20))

        sizer = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Bruggeman Effective Medium Approximation"),wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(lbox("Fraction 1",self.txt_fr1,self),0,wx.ALL,3)
        sizer2.Add(lbox("File 1",self.txt_file1,self),1,wx.ALL,3)
        sizer2.Add(self.btn_file1,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(sizer2,0,wx.EXPAND)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(lbox("Fraction 2",self.txt_fr2,self),0,wx.ALL,3)
        sizer2.Add(lbox("File 2",self.txt_file2,self),1,wx.ALL,3)
        sizer2.Add(self.btn_file2,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(sizer2,0,wx.EXPAND)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(lbox("Fraction 3",self.txt_fr3,self),0,wx.ALL,3)
        sizer2.Add(lbox("File 3",self.txt_file3,self),1,wx.ALL,3)
        sizer2.Add(self.btn_file3,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(sizer2,0,wx.EXPAND)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)

        mainsizer.Add((20, 20))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbox("Multilayer name",self.txt_multi_name,self),1,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer.Add(wx.Button(self, wx.ID_OK, 'OK'),0,wx.ALIGN_CENTER|wx.ALL,3)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)

        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.txt_fr2.Enable(False)

    def on_btn_insert(self, event):
        i=self.ch_layer.GetSelection()
        layer=self.multilayer.layer[i]
        self.multilayer.insert(layer)
        self.load(i+1)
        self.parent.dlg_thick.load()

    def on_btn_remove(self, event):
        i=self.ch_layer.GetSelection()
        self.multilayer.remove(self.multilayer.layer[i])
        self.load(i)
        self.parent.dlg_thick.load()

    def on_ch_layer(self,event):
        self.update_fields()

    def load(self,i):
        self.ch_layer.Clear()
        for layer in self.multilayer.layer:
            self.ch_layer.Append(layer.name)
        self.ch_layer.Select(i)
        self.update_fields()

    def update_fields(self):
        i=self.ch_layer.GetSelection()
        layer=self.multilayer.layer[i]
        self.txt_name.SetValue(layer.name)
        self.txt_thickness.SetValue(layer.thickness)
        self.txt_roughness.SetValue(layer.roughness)
        self.CheckBox_incoherent.SetValue(int(layer.incoherent))
        self.txt_fr1.SetValue(layer.fr1)
        self.txt_fr2.SetValue(layer.fr2)
        self.txt_fr3.SetValue(layer.fr3)
        self.txt_file1.SetValue(layer.file1)
        self.txt_file2.SetValue(layer.file2)
        self.txt_file3.SetValue(layer.file3)
        self.txt_multi_name.SetValue(self.multilayer.name)

        if i==0 or i==len(self.multilayer.layer)-1:
            self.btn_remove.Enable(False)
            self.txt_thickness.Enable(False)
            self.CheckBox_incoherent.Enable(False)
        else:
            self.btn_remove.Enable(True)
            self.txt_thickness.Enable(True)
            self.CheckBox_incoherent.Enable(True)
        
        if i==len(self.multilayer.layer)-1:
            self.btn_insert.Enable(False)
        else:
            self.btn_insert.Enable(True)
        
        if i==0:
            self.txt_roughness.Enable(False)
        else:
            self.txt_roughness.Enable(True)

    def update_multilayer(self,event):
        self.CheckFractions()
        i=self.ch_layer.GetSelection()
        layer=self.multilayer.layer[i]
        layer.name=self.txt_name.GetValue()
        layer.thickness=self.txt_thickness.GetValue()
        layer.roughness=self.txt_roughness.GetValue()
        layer.incoherent=str(int(self.CheckBox_incoherent.GetValue()))
        layer.fr1=self.txt_fr1.GetValue()
        layer.fr2=self.txt_fr2.GetValue()
        layer.fr3=self.txt_fr3.GetValue()
        layer.file1=self.txt_file1.GetValue()
        layer.file2=self.txt_file2.GetValue()
        layer.file3=self.txt_file3.GetValue()
        self.multilayer.name=self.txt_multi_name.GetValue()
        self.ch_layer.SetString(self.ch_layer.GetSelection(),layer.name)
        try:event.Skip()#serve sotto windows per gestire correttamente wx.EVT_KILL_FOCUS
        except:pass

    def CheckFractions(self):
        try:fr1=int(self.txt_fr1.GetValue())
        except:fr1=100
        try:fr3=int(self.txt_fr3.GetValue())
        except:fr3=0

        if not(0 <= fr1 <= 100):fr1=100
        fr2=100-fr1-fr3
        if fr2<0:fr2=0
        if fr2>100:fr2=100
        fr3=100-fr1-fr2

        self.txt_fr1.SetValue(str(fr1))
        self.txt_fr2.SetValue(str(fr2))
        self.txt_fr3.SetValue(str(fr3))

    def on_btn_file1(self, event):
        dlg = wx.FileDialog(self, "Choose a file", self.IndexDir, "", "*.in3", wx.FD_OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                l=len(path.commonprefix([filename,self.CurDir]))
                if l>0:
                    filename=filename[l+1:]
                self.txt_file1.SetValue(filename)
                self.update_multilayer(self)
        finally:
            dlg.Destroy()

    def on_btn_file2(self, event):
        dlg = wx.FileDialog(self, "Choose a file", self.IndexDir, "", "*.in3", wx.FD_OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                l=len(path.commonprefix([filename,self.CurDir]))
                if l>0:
                    filename=filename[l+1:]
                self.txt_file2.SetValue(filename)
                self.update_multilayer(self)
        finally:
            dlg.Destroy()

    def on_btn_file3(self, event):
        dlg = wx.FileDialog(self, "Choose a file", self.IndexDir, "", "*.in3", wx.FD_OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                l=len(path.commonprefix([filename,self.CurDir]))
                if l>0:
                    filename=filename[l+1:]
                self.txt_file3.SetValue(filename)
                self.update_multilayer(self)
        finally:
            dlg.Destroy()
