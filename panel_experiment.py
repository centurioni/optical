import wx
#from USB4000_fake import *
#import wx.lib.plot as plot
import plot
from functions import *

def lbox(label,oggetto,pannello):
    sizer = wx.StaticBoxSizer(wx.StaticBox(pannello,-1,label),wx.HORIZONTAL)
    sizer.Add(oggetto,1)
    return sizer

class ExperimentPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent.GetParent().GetParent()
        panel1 = wx.Panel(self)#Primo pannello
        panel2 = wx.Panel(self)#,size=(600,450))

        self.CheckBox_online = wx.CheckBox(panel1,-1,label='Online')
        self.Bind(wx.EVT_CHECKBOX, self.on_CheckBox_online, self.CheckBox_online)
        self.RadioBox_show = wx.RadioBox(panel1, -1,label='Show ...', choices=["Counts", "R", "T"],style=wx.VERTICAL)
        self.Bind(wx.EVT_RADIOBOX, self.on_RadioBox_show, self.RadioBox_show)
        self.txt_int_time = wx.TextCtrl(panel1)
        self.txt_avg = wx.TextCtrl(panel1)
        self.txt_boxcar = wx.TextCtrl(panel1)
        self.btn_apply = wx.Button(panel1, -1, 'Apply')
        self.btn_apply.Bind(wx.EVT_BUTTON, self.on_btn_apply)
        self.btn_ref = wx.Button(panel1, -1, 'Light ref')
        self.btn_ref.Bind(wx.EVT_BUTTON, self.on_btn_ref)
        self.btn_dark = wx.Button(panel1, -1, 'Dark ref')
        self.btn_dark.Bind(wx.EVT_BUTTON, self.on_btn_dark)
        self.btn_store = wx.Button(panel1, -1, 'Store')
        self.btn_store.SetToolTip(wx.ToolTip('Store current data (R or T) on experiment'))
        self.btn_store.Bind(wx.EVT_BUTTON, self.on_btn_store)
        self.btn_save = wx.Button(panel1, -1, 'Quick Save')
        self.btn_save.SetToolTip(wx.ToolTip('Store current data (R or T) and save experiment on a file'))
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_btn_save)

        sizer = wx.BoxSizer(wx.VERTICAL)#Dispongo gli oggetti col sizer
        sizer.Add((-1, -1), 1)
        sizer.Add(self.CheckBox_online, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer.Add(self.RadioBox_show, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer.Add(lbox("Int time (ms)",self.txt_int_time,panel1),0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(lbox("Average",self.txt_avg,panel1),0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(lbox("Boxcar",self.txt_boxcar,panel1),0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_apply, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer.Add(self.btn_ref, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_dark, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_store, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_save, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        panel1.SetSizer(sizer)#Metto gli oggetti cosi' disposti sul panel1

        self.plot_spectrometer = plot.PlotCanvas(panel2)
        self.plot_spectrometer.SetEnableGrid(True)
        self.plot_spectrometer.SetEnableZoom(True)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.plot_spectrometer, 1, wx.EXPAND | wx.ALL)
        panel2.SetSizer(sizer)

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)#Dispongo i pannelli su un altro sizer
        mainsizer.Add(panel1,0,wx.EXPAND)
        mainsizer.Add(panel2,1,wx.EXPAND)
        self.SetSizer(mainsizer)#Metto i pannelli cosi' disposti sul mainpanel

        self.CheckBox_online.SetValue(True)
        self.dark=[]
        self.light=[]
        self.percent=[]
        self.counts=[]
        self.parent.spectrometer.int_time=int(self.parent.settings["int_time"])
        self.parent.spectrometer.avg=int(self.parent.settings["avg"])
        self.parent.spectrometer.boxcar=int(self.parent.settings["boxcar"])
        self.on_btn_apply(None)
        self.on_CheckBox_online(None)
        self.run=True
        wx.CallLater(200, self.update)

    def update(self):
        if self.run:
            while self.parent.spectrometer.lock:
                pass
            self.counts=self.parent.spectrometer.counts[:]
            if self.RadioBox_show.GetSelection() == 0:
                line = plot.PolyLine(self.counts, colour='red', width=1)
                gc = plot.PlotGraphics([line], '', 'nm', 'counts')
                self.plot_spectrometer.Draw(gc, yAxis= (0,self.parent.spectrometer.maxcount*1.1))
            elif self.RadioBox_show.GetSelection() == 1:
                del self.percent[:]
                for i in range(len(self.counts)):
                    try:
                        r=Interpol(self.parent.ref,self.counts[i][0])
                        p=r*(self.counts[i][1]-self.dark[i][1])/(self.light[i][1]-self.dark[i][1])
                        self.percent.append([self.counts[i][0],p])#*r
                    except:
                        pass
                line = plot.PolyLine(self.percent, colour='green', width=2)
                gc = plot.PlotGraphics([line], "",'nm', '%')
                self.plot_spectrometer.Draw(gc, yAxis= (0,110))
            else:
                del self.percent[:]
                for i in range(len(self.counts)):
                    try:
                        p=100*(self.counts[i][1]-self.dark[i][1])/(self.light[i][1]-self.dark[i][1])
                        self.percent.append([self.counts[i][0],p])#*r
                    except:
                        pass
                line = plot.PolyLine(self.percent, colour='blue', width=2)
                gc = plot.PlotGraphics([line], "",'nm', '%')
                self.plot_spectrometer.Draw(gc, yAxis= (0,110))
        wx.CallLater(200, self.update)

    def on_btn_store(self, event):
        if len(self.parent.experiment.data) == len(self.percent):
            for i in range(len(self.percent)):
                if self.RadioBox_show.GetSelection() == 1:self.parent.experiment.data[i].R = self.percent[i][1]/100.0
                if self.RadioBox_show.GetSelection() == 2:self.parent.experiment.data[i].T = self.percent[i][1]/100.0
        else:
            self.parent.experiment.clear()
            for i in range(len(self.percent)):
                if self.RadioBox_show.GetSelection() == 1:self.parent.experiment.add(data(lam=self.percent[i][0],T=0.0,R=self.percent[i][1]/100.0))
                if self.RadioBox_show.GetSelection() == 2:self.parent.experiment.add(data(lam=self.percent[i][0],R=0.0,T=self.percent[i][1]/100.0))
        self.parent.experiment.lmin=self.percent[0][0]
        self.parent.experiment.lmax=self.percent[-1][0]
        self.parent.on_btn_clear(None)
        self.parent.UpdateButtons()
        self.parent.experiment.saved=False
        self.parent.nb.SetSelection(0)

    def on_btn_save(self,event):
        self.on_btn_store(None)
        self.parent.on_menu_save_experiment_as(None)

    def update_btn_experimental(self):
        if len(self.dark) == 0 or len(self.light) == 0:
            self.btn_store.Enable(False)
            self.btn_save.Enable(False)
            self.RadioBox_show.SetSelection(0)
            self.RadioBox_show.Enable(False)
        else:
            self.RadioBox_show.Enable(True)
            if self.RadioBox_show.GetSelection() <> 0:
                self.btn_store.Enable(True)
                self.btn_save.Enable(True)
            else:
                self.btn_store.Enable(False)
                self.btn_save.Enable(False)

    def on_CheckBox_online(self,event):
        try:
            if self.parent.spectrometer.run:
                if self.CheckBox_online.GetValue():
                    self.run=True
                    self.btn_dark.Enable(True)
                    self.btn_ref.Enable(True)
                    self.update_btn_experimental()
                else:
                    self.run=False
                    self.btn_store.Enable(False)
                    self.btn_save.Enable(False)
                    self.btn_dark.Enable(False)
                    self.btn_ref.Enable(False)
                    self.RadioBox_show.Enable(False)
        except:pass

    def on_RadioBox_show(self, event):
        self.update_btn_experimental()

    def on_btn_dark(self, event):
        while self.parent.spectrometer.lock:
            pass
        self.dark=self.parent.spectrometer.counts[:]
        self.update_btn_experimental()

    def on_btn_ref(self, event):
        while self.parent.spectrometer.lock:
            pass
        self.light=self.parent.spectrometer.counts[:]
        self.update_btn_experimental()

    def on_btn_apply(self, event):
        try:int_time=int(self.txt_int_time.GetValue())
        except:int_time=self.parent.spectrometer.int_time
        try:avg=int(self.txt_avg.GetValue())
        except:avg=self.parent.spectrometer.avg
        try:boxcar=int(self.txt_boxcar.GetValue())
        except:boxcar=self.parent.spectrometer.boxcar
        if not self.parent.spectrometer.int_time_min <= int_time <= self.parent.spectrometer.int_time_max:int_time=self.parent.spectrometer.int_time
        if not 1 <= avg <= 1000:avg=self.parent.spectrometer.avg
        if not 0 <= boxcar <= 100:boxcar=self.parent.spectrometer.boxcar
        self.parent.spectrometer.int_time=int_time
        self.parent.spectrometer.avg=avg
        self.parent.spectrometer.boxcar=boxcar
        self.txt_int_time.SetValue(str(int_time))
        self.txt_avg.SetValue(str(avg))
        self.txt_boxcar.SetValue(str(boxcar))
        self.parent.settings["int_time"]=str(int_time)
        self.parent.settings["avg"]=str(avg)
        self.parent.settings["boxcar"]=str(boxcar)
        del self.dark[:]
        del self.light[:]
        self.update_btn_experimental()
        SaveConf(self.parent.settings)
        #SaveIntTime(int_time,avg,boxcar)
