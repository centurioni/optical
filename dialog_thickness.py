import wx

from functions import *
from ScatteringMatrix import *

def lbox(label,oggetto,pannello):
    sizer = wx.StaticBoxSizer(wx.StaticBox(pannello,-1,label),wx.HORIZONTAL)
    sizer.Add(oggetto,1)
    return sizer

class ThicknessDialog(wx.Dialog):
    def __init__(self,parent):
        wx.Dialog.__init__(self, None, -1, "Thickness determination")
        self.parent=parent
        #self.SetTitle("Thickness determination: experimental R and T accuracy = +- "+str(self.parent.StDev*100)+"% of full scale")
        self.ch_layer = wx.Choice(self)
        self.Bind(wx.EVT_CHOICE, self.on_ch_layer, self.ch_layer)
        self.txt_thickness = wx.TextCtrl(self,style=wx.TE_PROCESS_ENTER)
        self.txt_thickness.Bind(wx.EVT_KILL_FOCUS, self.update_thickness)
        self.Bind(wx.EVT_TEXT_ENTER, self.update_thickness, self.txt_thickness)
        self.ch_link_layer = wx.Choice(self)
        self.Bind(wx.EVT_CHOICE, self.on_ch_link_layer, self.ch_link_layer)
        self.txt_density = wx.TextCtrl(self,-1,"1")
        self.txt_thickness_from = wx.TextCtrl(self)
        self.txt_thickness_to = wx.TextCtrl(self)
        self.RadioBox_tipo = wx.RadioBox(self, -1,label='Fit on ...', choices=["Reflectance", "Transmittance", "Both"],style=wx.VERTICAL)
        self.spin_button = wx.SpinButton(self)
        self.Bind(wx.EVT_SPIN, self.on_spin_button, self.spin_button)
        self.btn_fit = wx.Button(self, -1, 'Fit')
        self.btn_fit.Bind(wx.EVT_BUTTON, self.on_btn_fit)
        self.btn_clear = wx.Button(self, -1, 'Clear')
        self.btn_clear.Bind(wx.EVT_BUTTON, self.parent.on_btn_clear)

        self.list_ctrl = wx.ListCtrl(self,style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, 'Thickness')
        self.list_ctrl.InsertColumn(1, 'Chi R')
        self.list_ctrl.InsertColumn(2, 'Chi T')
        self.list_ctrl.InsertColumn(3, 'Chi RT')

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbox("Select layer",self.ch_layer,self),0,wx.ALL,3)
        sizer.Add(lbox("Thickness (nm)",self.txt_thickness,self),0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer2.Add(sizer,0,wx.EXPAND|wx.ALL,3)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(lbox("Link to layer",self.ch_link_layer,self),0,wx.ALL,3)
        sizer.Add(lbox("Rel. density",self.txt_density,self),0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer2.Add(sizer,0,wx.EXPAND|wx.ALL,3)
        
        sizer2.Add((20, 20))

        sizer = wx.StaticBoxSizer(wx.StaticBox(self,-1,"Search range (nm)"),wx.HORIZONTAL)
        sizer.Add(lbox("From",self.txt_thickness_from,self),0,wx.ALL,3)
        sizer.Add(lbox("To",self.txt_thickness_to,self),0,wx.ALL,3)
        sizer.Add(self.spin_button,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer2.Add(sizer,0,wx.ALL,3)

        sizer2.Add((20, 20))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.RadioBox_tipo,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer3 = wx.BoxSizer(wx.VERTICAL)
        sizer3.Add(self.btn_fit,0,wx.ALL,3)
        sizer3.Add(self.btn_clear,0,wx.ALL,3)
        sizer3.Add(wx.Button(self, wx.ID_OK, 'Close'),0,wx.ALL,3)
        sizer.Add(sizer3,0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer2.Add(sizer,0,wx.EXPAND|wx.ALL,3)

        mainsizer.Add(sizer2,0)
        mainsizer.Add(self.list_ctrl,1,wx.EXPAND|wx.ALL,3)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.fitlayer=None
        self.txt_thickness_from.Enable(False)
        self.txt_thickness_to.Enable(False)

    def load(self):
        self.ch_layer.Clear()
        self.ch_link_layer.Clear()
        self.ch_link_layer.Append("None")
        for layer in self.parent.multilayer.layer[1:-1]:
            self.ch_layer.Append(layer.name)
            self.ch_link_layer.Append(layer.name)
        self.ch_layer.Select(0)
        self.ch_link_layer.Select(0)
        self.update_fields()

    def update_fields(self):
        self.fitlayer=self.parent.multilayer.layer[self.ch_layer.GetSelection()+1]
#        self.linklayer=self.multilayer.layer[self.ch_link_layer.GetSelection()]
        self.txt_thickness.SetValue(self.fitlayer.thickness)
        thickness=float(self.fitlayer.thickness)
        self.txt_thickness_to.SetValue(str(thickness+0.2*2**self.spin_button.GetValue()))
        self.txt_thickness_from.SetValue(str(thickness-0.2*2**self.spin_button.GetValue()))
        if self.ch_layer.GetSelection()+1 == self.ch_link_layer.GetSelection():self.ch_link_layer.Select(0)
        if self.ch_link_layer.GetSelection()==0:
            self.txt_density.Enable(False)
        else:
            self.txt_density.Enable(True)
        try:self.ch_layer.SetString(self.ch_layer.GetSelection(),self.fitlayer.name)
        except:pass

    def update_thickness(self,event):
        try:event.Skip()#serve sotto windows per gestire correttamente wx.EVT_KILL_FOCUS
        except:pass
        self.fitlayer.thickness=self.txt_thickness.GetValue()
        self.update_fields()

    def on_ch_layer(self,event):
        self.update_fields()

    def on_ch_link_layer(self,event):
        self.update_fields()

    def on_spin_button(self,event):
        self.update_fields()

    def on_btn_fit(self,event):
        layer=self.ch_layer.GetSelection()+1
        layerLink=self.ch_link_layer.GetSelection()
        Density=float(self.txt_density.GetValue())
        dlambda=0.1*2**self.spin_button.GetValue()
        fiton=self.RadioBox_tipo.GetSelection()

        self.parent.checkrange()
        start=max(float(self.parent.txt_wave_min.GetValue()),self.parent.multilayer.lmin)
        end=min(float(self.parent.txt_wave_max.GetValue()),self.parent.multilayer.lmax)

        Fi=float(self.parent.txt_angle.GetValue())
        Fi=pi*Fi/180.0

        lam,Re,Te=[],[],[]
        for d in self.parent.experiment.data:
            if start<= d.lam <= end:
                lam.append(d.lam)
                Re.append(d.R)
                Te.append(d.T)

        structure=PrepareList(self.parent.multilayer,lam)
        if layerLink!=0:
            TotalThick = structure[layer][0]*Density+structure[layerLink][0]

        while dlambda >= 0.025:#
            structure[layer][0] = structure[layer][0]-0.01
            if layerLink!=0:
                structure[layerLink][0]=TotalThick-structure[layer][0]*Density
            R,T=ComputeRT(structure,lam,Fi)
            Chi_R,Chi_T,Chi_RT=Chi(R,T,Re,Te,self.parent.StDev)
            if fiton == 0:#Reflectance
                Chi1=Chi_R
            elif fiton == 1:#Transmittance
                Chi1=Chi_T
            else:
                Chi1=Chi_RT
            structure[layer][0] = structure[layer][0]+0.01
            if layerLink!=0:
                structure[layerLink][0]=TotalThick-structure[layer][0]*Density
            R,T=ComputeRT(structure,lam,Fi)
            Chi_R,Chi_T,Chi_RT=Chi(R,T,Re,Te,self.parent.StDev)
            if fiton == 0:#Reflectance
                Chi2=Chi_R
            elif fiton == 1:#Transmittance
                Chi2=Chi_T
            else:
                Chi2=Chi_RT
            if Chi2-Chi1!=0:
                sign =(Chi2 - Chi1)/abs(Chi2 - Chi1)
            else:
                sign=0
            structure[layer][0]=structure[layer][0]-dlambda*sign
            dlambda=dlambda/2

        if layerLink!=0:
            structure[layerLink][0]=float("%0.1f" %TotalThick-structure[layer][0]*Density)
        structure[layer][0] =float("%0.1f" %structure[layer][0])
        
        R,T=ComputeRT(structure,lam,Fi)
        Chi_R,Chi_T,Chi_RT=Chi(R,T,Re,Te,self.parent.StDev)
        self.parent.multilayer.layer[layer].thickness="%0.1f" %structure[layer][0]
        self.parent.multilayer.layer[layerLink].thickness="%0.1f" %structure[layerLink][0]
        if self.parent.CheckBox_A.GetValue():self.parent.axes.plot(lam,100*(1-R-T))
        if self.parent.CheckBox_T.GetValue():self.parent.axes.plot(lam,100*T)
        if self.parent.CheckBox_R.GetValue():self.parent.axes.plot(lam,100*R)
        self.parent.canvas.draw()
        self.update_fields()

        self.list_ctrl.Append([str(structure[layer][0]),"%0.1e" %Chi_R,"%0.1e" %Chi_T,"%0.1e" %Chi_RT])
        self.list_ctrl.Focus(self.list_ctrl.GetItemCount()-1)

    def show_chi(self):
        self.parent.checkrange()
        start=float(self.parent.txt_wave_min.GetValue())
        end=float(self.parent.txt_wave_max.GetValue())
        Fi=float(self.parent.txt_angle.GetValue())
        Fi=pi*Fi/180.0

        lam,Re,Te=[],[],[]
        for d in self.parent.experiment.data:
            if start<= d.lam <= end:
                lam.append(d.lam)
                Re.append(d.R)
                Te.append(d.T)

        structure=PrepareList(self.parent.multilayer,lam)
        R,T=ComputeRT(structure,lam,Fi)
        Chi_R,Chi_T,Chi_RT=Chi(R,T,Re,Te,self.parent.StDev)
        if self.parent.CheckBox_A.GetValue():self.parent.axes.plot(lam,100*(1-R-T))
        if self.parent.CheckBox_T.GetValue():self.parent.axes.plot(lam,100*T)
        if self.parent.CheckBox_R.GetValue():self.parent.axes.plot(lam,100*R)
        self.parent.canvas.draw()
        self.update_fields()

        self.list_ctrl.Append(["####","%0.1e" %Chi_R,"%0.1e" %Chi_T,"%0.1e" %Chi_RT])
        self.list_ctrl.Focus(self.list_ctrl.GetItemCount()-1)
