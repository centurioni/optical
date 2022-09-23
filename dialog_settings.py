import wx
import os

def lbox(label,oggetto,pannello):
    sizer = wx.StaticBoxSizer(wx.StaticBox(pannello,-1,label),wx.HORIZONTAL)
    sizer.Add(oggetto,1)
    return sizer

class SettingsDialog(wx.Dialog):
    def __init__(self,parent):
        wx.Dialog.__init__(self, None, -1, "Settings")
        self.parent=parent
        self.CurDir=parent.CurDir
        self.txt_plot_points = wx.TextCtrl(self)
        self.txt_plot_points.SetToolTip(wx.ToolTip('Number of point calculated by "Compute"'))
        self.txt_Fi = wx.TextCtrl(self)
        self.txt_Fi.SetToolTip(wx.ToolTip('Default incidence angle (deg)'))
        self.txt_st_dev = wx.TextCtrl(self)
        self.txt_st_dev.SetToolTip(wx.ToolTip('Experimental data (R and T) accuracy, needed for ChiSquare calculation, expressed in full scale %'))
        self.txt_structure_dir = wx.TextCtrl(self)
        self.txt_structure_dir.SetToolTip(wx.ToolTip('Default multilayer data directory, relative path'))
        self.txt_index_dir = wx.TextCtrl(self)
        self.txt_index_dir.SetToolTip(wx.ToolTip('Default index data directory, relative path'))
        self.txt_experimental_dir = wx.TextCtrl(self)
        self.txt_experimental_dir.SetToolTip(wx.ToolTip('Default experimental data directory, relative path'))
        #self.btn_browse = wx.Button(self, -1,"Browse")
        #self.btn_browse.Bind(wx.EVT_BUTTON, self.on_btn_browse)
        self.txt_reference = wx.TextCtrl(self)
        self.txt_reference.SetToolTip(wx.ToolTip('Reflectivity reference file, relative path'))

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(lbox("Reference",self.txt_reference,self),0,wx.EXPAND|wx.ALL,3)
        mainsizer.Add(lbox("Points",self.txt_plot_points,self),0,wx.EXPAND|wx.ALL,3)
        mainsizer.Add(lbox("Angle",self.txt_Fi,self),0,wx.EXPAND|wx.ALL,3)
        mainsizer.Add(lbox("R and T accuracy",self.txt_st_dev,self),0,wx.EXPAND|wx.ALL,3)
        mainsizer.Add(lbox("Multilayer dir",self.txt_structure_dir,self),0,wx.EXPAND|wx.ALL,3)
        mainsizer.Add(lbox("Index dir",self.txt_index_dir,self),0,wx.EXPAND|wx.ALL,3)
        #mainsizer.Add((20, 20), 0)
        mainsizer.Add(lbox("Experimental dir",self.txt_experimental_dir,self),0,wx.EXPAND|wx.ALL,3)
        #mainsizer.Add(self.btn_browse,0,wx.ALIGN_CENTER|wx.ALL,3)
        mainsizer.Add((20, 20), 0)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Button(self, wx.ID_CANCEL, 'Cancel'),0,wx.ALL,3)
        sizer.Add(wx.Button(self, wx.ID_OK, 'OK'),0,wx.ALL,3)
        mainsizer.Add(sizer,0,wx.ALL,3)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)

        self.txt_plot_points.SetValue(str(parent.PlotPoints))
        self.txt_Fi.SetValue(parent.txt_angle.GetValue())
        self.txt_st_dev.SetValue(str(parent.StDev*100))
        self.txt_structure_dir.SetValue(os.path.relpath(parent.StructureDir, parent.CurDir))
        self.txt_index_dir.SetValue(os.path.relpath(parent.IndexDir, parent.CurDir))
        self.txt_experimental_dir.SetValue(os.path.relpath(parent.ExpDir, parent.CurDir))
        self.txt_reference.SetValue(os.path.relpath(parent.RefFile, parent.CurDir))

    # def on_btn_browse(self,event):
        # dlg = wx.DirDialog(self, "Choose a directory", self.CurDir+"/")
        # try:
            # if dlg.ShowModal() == wx.ID_OK:
                # dirname = dlg.GetPath()
                # self.txt_experimental_dir.SetValue(dirname)
        # finally:
            # dlg.Destroy()


