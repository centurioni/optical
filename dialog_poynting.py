import wx
from os import path
from math import *
from functions import *
from ScatteringMatrix import *


def lbox(label,oggetto,pannello):
    sizer = wx.StaticBoxSizer(wx.StaticBox(pannello,-1,label),wx.HORIZONTAL)
    sizer.Add(oggetto,1)
    return sizer

class PoyntingDialog(wx.Dialog):
    def __init__(self,parent):
        wx.Dialog.__init__(self, None, -1, "Energy flux calculator")
        self.parent=parent
        self.multilayer=parent.multilayer
        self.CurDir=parent.CurDir
        self.IndexDir=parent.IndexDir
        self.txt_thickness = wx.TextCtrl(self)
        self.txt_depth = wx.TextCtrl(self)
        self.ch_layer = wx.Choice(self)
        self.Bind(wx.EVT_CHOICE, self.on_ch_layer, self.ch_layer)
        self.btn_flux = wx.Button(self, -1,"Compute")
        self.btn_flux.Bind(wx.EVT_BUTTON, self.on_btn_flux)
        self.btn_absorption = wx.Button(self, -1,"Compute")
        self.btn_absorption.Bind(wx.EVT_BUTTON, self.on_btn_absorption)
        self.btn_clear = wx.Button(self, -1, 'Clear')
        self.btn_clear.Bind(wx.EVT_BUTTON, self.parent.on_btn_clear)

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbox("Select layer",self.ch_layer,self),1,wx.ALL,3)
        sizer.Add(lbox("Thickness (nm)",self.txt_thickness,self),0,wx.ALL,3)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add((-1, -1), 1)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)
        
        mainsizer.Add((20, 20))

        sizer = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Light absorption in selected layer"),wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add((-1, -1), 1)
        sizer2.Add(self.btn_absorption,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(sizer2,0,wx.EXPAND)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)

        mainsizer.Add((20, 20))

        sizer = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Poynting energy flux in selected layer"),wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(lbox("Depth (nm)",self.txt_depth,self),0,wx.ALL,3)
        sizer2.Add((100,1))
        sizer2.Add(self.btn_flux,0,wx.ALIGN_CENTER|wx.ALL,3)
        #sizer2.Add((100,1))
        sizer.Add(sizer2,0,wx.EXPAND)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)

        mainsizer.Add((20, 20))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.btn_clear,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer.Add(wx.Button(self, wx.ID_CANCEL, 'Close'),0,wx.ALIGN_CENTER|wx.ALL,3)
        mainsizer.Add(sizer,0,wx.EXPAND|wx.ALL,3)

        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.txt_thickness.Enable(False)
        self.txt_depth.SetValue("0")

    def on_ch_layer(self,event):
        self.update_fields()

    def load(self,i):
        self.ch_layer.Clear()
        for layer in self.multilayer.layer[1:-1]:
            self.ch_layer.Append(layer.name)
        self.ch_layer.Select(i)
        self.update_fields()

    def update_fields(self):
        i=self.ch_layer.GetSelection()
        layer=self.multilayer.layer[i+1]
        self.txt_thickness.SetValue(layer.thickness)

    def on_btn_flux(self, event):
        self.poynting("F")
        
    def on_btn_absorption(self, event):
        self.poynting("A")

    def poynting(self,flag):
        self.parent.ema()
        self.parent.checkrange()
        start=max(float(self.parent.txt_wave_min.GetValue()),self.multilayer.lmin)
        end=min(float(self.parent.txt_wave_max.GetValue()),self.multilayer.lmax)

        if end > start:
            Fi=float(self.parent.txt_angle.GetValue())
            Fi=pi*Fi/180.0

            lam=[]
            for i in range(self.parent.PlotPoints):
                lam.append(start+i*(end-start)/(self.parent.PlotPoints-1))
            lam[-1]=end#to be sure last point is exactly end

            structure=PrepareList(self.multilayer,lam)
            if flag=="F":
                x=float(self.txt_depth.GetValue())/float(self.txt_thickness.GetValue())
                P=ComputeFlux(structure,lam,Fi,self.ch_layer.GetSelection()+1,x)
                SavePoyntingFlux(lam,P)
            else:
                P=ComputeA(structure,lam,Fi,self.ch_layer.GetSelection()+1)
                SaveLayerAbsorption(lam,P)
            self.parent.axes.plot(lam,100*P)
            self.parent.canvas.draw()
        else:
            dlg = wx.MessageDialog(self, 'No points to plot ! Check wavelength range.',
              'Warning', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
