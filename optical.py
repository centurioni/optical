# This Python file uses the following encoding: utf-8

#Optical 
version="1.14-rc"
year=2022
#Copyright (C) 2005-2022  Emanuele Centurioni
#E-mail: centurioni@bo.imm.cnr.it

spectro=False#set True to enable OceanOptics driver and spectra acquisition interface

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure
if spectro:from OceanOptics import *#remove comment to use spectrometer

import wx
from functions import *
from ScatteringMatrix import *
from dialog_edit import EditDialog
from dialog_poynting import PoyntingDialog
from dialog_thickness import ThicknessDialog
from dialog_settings import SettingsDialog
if spectro:from panel_experiment import ExperimentPanel

def lbox(label,oggetto,pannello):
    sizer = wx.StaticBoxSizer(wx.StaticBox(pannello,-1,label),wx.HORIZONTAL)
    sizer.Add(oggetto,1)
    return sizer

class MainFrame(wx.Frame):#Frame principale che contiene tutto
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Optical 1.0")
        if osname=="nt":self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)#necessario sotto windows
        self.menubar = wx.MenuBar()#Crea la barra del  menu
        menu_file = wx.Menu()
        menu_new_multilayer = menu_file.Append(-1, "New multilayer", "Creating an empty multilayer")
        self.Bind(wx.EVT_MENU, self.on_menu_new_multilayer, menu_new_multilayer)
        menu_open_multilayer = menu_file.Append(-1, "Open multilayer", "Open an existing multilayer file")
        self.Bind(wx.EVT_MENU, self.on_menu_open_multilayer, menu_open_multilayer)
        menu_edit_multilayer = menu_file.Append(-1, "Edit multilayer", "Edit the current multilayer")
        self.Bind(wx.EVT_MENU, self.on_menu_edit_multilayer, menu_edit_multilayer)
        menu_save_multilayer = menu_file.Append(-1, "Save multilayer", "Save the current multilayer")
        self.Bind(wx.EVT_MENU, self.on_menu_save_multilayer, menu_save_multilayer)
        menu_save_multilayer_as = menu_file.Append(-1, "Save multilayer as", "Save the current multilayer as")
        self.Bind(wx.EVT_MENU, self.on_menu_save_multilayer_as, menu_save_multilayer_as)
        menu_file.AppendSeparator()
        self.menu_new_experiment = menu_file.Append(-1, "New experiment", "Creating an empty experiment")
        self.Bind(wx.EVT_MENU, self.on_menu_new_experiment, self.menu_new_experiment)
        self.menu_load_experiment = menu_file.Append(-1, "Load experiment", "Load both reflectivity and transmittance data from file")
        self.Bind(wx.EVT_MENU, self.on_menu_load_experiment, self.menu_load_experiment)
        self.menu_load_R = menu_file.Append(-1, "Load R", "Load reflectivity data from file and merge to experiment")
        self.Bind(wx.EVT_MENU, self.on_menu_load_R, self.menu_load_R)
        self.menu_load_T = menu_file.Append(-1, "Load T", "Load transmittance data from file and merge to experiment")
        self.Bind(wx.EVT_MENU, self.on_menu_load_T, self.menu_load_T)

#        menu_save_experiment = menu_file.Append(-1, "Save experiment", "Save experimental data")
#        self.Bind(wx.EVT_MENU, self.on_menu_save_experiment, menu_save_experiment)
        self.menu_save_experiment_as = menu_file.Append(-1, "Save experiment as", "Save experimental data as")
        self.Bind(wx.EVT_MENU, self.on_menu_save_experiment_as, self.menu_save_experiment_as)
        menu_file.AppendSeparator()
        menu_exit = menu_file.Append(-1, "Exit", "Exit")
        self.Bind(wx.EVT_MENU, self.on_close, menu_exit)

        menu_pref = wx.Menu()
        menu_settings = menu_pref.Append(-1, "Settings", "Configure Optical")
        self.Bind(wx.EVT_MENU, self.on_menu_settings, menu_settings)
        #menu_wave = menu_pref.Append(-1, "Wavelength range", "Limit the wavelength range of computed data")

        menu_help = wx.Menu()
        menu_about = menu_help.Append(-1, "About", "About this program")
        self.Bind(wx.EVT_MENU, self.on_menu_about, menu_about)

        self.menubar.Append(menu_file, "File")
        self.menubar.Append(menu_pref, "Preferences")
        self.menubar.Append(menu_help, "Help")
        self.SetMenuBar(self.menubar)

        self.statusBar = wx.StatusBar(self, -1)#Crea la barra di stato
        self.statusBar.SetFieldsCount(1)
        self.SetStatusBar(self.statusBar)

        rootpanel = wx.Panel(self)
        self.nb = wx.Notebook(rootpanel)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change, self.nb)

### simulation panel
        simpanel = wx.Panel(self.nb)
        #simpanel.SetBackgroundColour('YELLOW')
        panel1 = wx.Panel(simpanel)#Primo pannello
        panel2 = wx.Panel(simpanel)#Secondo pannello

        self.CheckBox_A = wx.CheckBox(panel1,-1,label='Show A')
        self.CheckBox_T = wx.CheckBox(panel1,-1,label='Show T')
        self.CheckBox_R = wx.CheckBox(panel1,-1,label='Show R')
        self.txt_angle = wx.TextCtrl(panel1, -1, '0')#Crea un oggetto testo associato al panel1, solo il primo argomento e' obbligatorio
        self.btn_alpha = wx.Button(panel1, -1, 'Alpha')
        self.btn_alpha.Bind(wx.EVT_BUTTON, self.on_btn_alpha)
        self.btn_poynting = wx.Button(panel1, -1, 'Poynting')
        self.btn_poynting.Bind(wx.EVT_BUTTON, self.on_btn_poynting)
        self.btn_energy_profile = wx.Button(panel1, -1, 'E Profile')
        self.btn_energy_profile.Bind(wx.EVT_BUTTON, self.on_btn_energy_profile)
        self.btn_thick_det = wx.Button(panel1, -1, 'Thick det')#Oggetto pulsante associato al panel 1
        self.btn_thick_det.Bind(wx.EVT_BUTTON, self.on_btn_thick_det)
        self.btn_chi_test = wx.Button(panel1, -1, 'Chi test')
        self.btn_chi_test.Bind(wx.EVT_BUTTON, self.on_btn_chi_test)
        self.btn_compute = wx.Button(panel1, -1, 'Compute')
        self.btn_compute.Bind(wx.EVT_BUTTON, self.on_btn_compute)
        self.btn_clear = wx.Button(panel1, -1, 'Clear')
        self.btn_clear.Bind(wx.EVT_BUTTON, self.on_btn_clear)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.txt_wave_min = wx.TextCtrl(panel2,-1,"200")
        self.txt_wave_max = wx.TextCtrl(panel2,-1,"1100")
        self.CheckBox_W = wx.CheckBox(panel2,-1,label='Autorange')

        sizer = wx.BoxSizer(wx.VERTICAL)#Dispongo gli oggetti col sizer
        sizer.Add((-1, -1), 1)
        sizer.Add(lbox("Angle (deg)",self.txt_angle,panel1),0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer.Add(self.CheckBox_A, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.CheckBox_T, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.CheckBox_R, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        sizer.Add(self.btn_alpha, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_poynting, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_energy_profile, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_thick_det, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_chi_test, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_compute, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add(self.btn_clear, 0,wx.ALIGN_CENTER|wx.ALL,3)
        sizer.Add((-1, -1), 1)
        panel1.SetSizer(sizer)#Metto gli oggetti cosi' disposti sul panel1

        self.figure = Figure()#Elementi per il grafico
        #self.figure = Figure((10.0, 8.0))#se la voglio di un'altra dimensione rispetto allo standard
        self.canvas = FigureCanvas(panel2, -1, self.figure)#Il grafico appartiene al panel 2
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)
        
        self.toolbar = NavigationToolbar(self.canvas)

        self.canvas.mpl_connect('motion_notify_event',self.update_coords)

        sizer = wx.BoxSizer(wx.VERTICAL)#Dispongo il grafico ed il ToolBar col sizer
        #sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL,4)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.toolbar, 0,wx.ALIGN_CENTER)
        sizer2.Add((-1, -1), 1)
        sizer2.Add(self.CheckBox_W,0,wx.ALIGN_CENTER,wx.ALL,3)
        sizer2.Add(lbox("Min (nm)",self.txt_wave_min,panel2),0,wx.ALL,3)
        sizer2.Add(lbox("Max (nm)",self.txt_wave_max,panel2),0,wx.ALL,3)
        #sizer2.Add((-1, -1), 1)
        sizer.Add(sizer2,0,wx.EXPAND)
        panel2.SetSizer(sizer)#Metto gli oggetti cosi' disposti sul panel2

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)#Dispongo i pannelli su un altro sizer
        mainsizer.Add(panel1,0,wx.EXPAND)
        mainsizer.Add(panel2,1,wx.EXPAND)
        simpanel.SetSizer(mainsizer)#Metto i pannelli cosi' disposti sul mainpanel
#        mainsizer.Fit(nb)#adatto le dimensioni

        self.nb.AddPage(simpanel, "Experiment and Simulation")
        self.settings=LoadConf()

        if spectro:
            try:
            #if True:
                #self.spectrometer=USB4000()
                #self.spectrometer=ADC1000USB()
                self.spectrometer=FakeSpectrometer()
                self.thread1 = Thread(target=ocean,args=[self.spectrometer])
                self.spectrometer.run=True
                self.thread1.start()
                self.exppanel = ExperimentPanel(self.nb)
                #self.exppanel2 = ExperimentPanel(self.nb)
                self.nb.AddPage(self.exppanel, "Spectrometer")
                #self.nb.AddPage(self.exppanel2, "Spectrometer2")
                self.nb.SetSelection(1)
            except:
            #if False:
                dlg = wx.MessageDialog(self, "Spectrometer not found !", "Warning", wx.OK)
                dlg.ShowModal()
                dlg.Destroy()

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        rootpanel.SetSizer(sizer)
        sizer.Fit(self)#adatto le dimensioni
        #self.nb.SetSelection(1)

        self.StructureDir="structures"
        self.IndexDir="n"
        self.ExpDir="experiments"
        self.StDev=1.0
        self.PlotPoints=400
        Fi=0
        self.wavelength_profile=500
        self.points_profile=100

        self.CurDir=getcwd()
        self.loadconf()

        self.multilayer=multilayer()
        self.multilayer.add(layer(name="TopLayer",file1="n/air.in3",fr1="100"))
        self.multilayer.add(layer(name="BottomLayer",file1="n/air.in3",fr1="100"))
        EMA(self.multilayer)
        self.experiment=experiment()
        self.experiment_buffer=experiment()
        self.dlg_edit = EditDialog(self)
        self.dlg_edit.load(0)
        self.dlg_poynting = PoyntingDialog(self)
        self.dlg_poynting.load(0)

        self.dlg_thick = ThicknessDialog(self)
        self.dlg_thick.load()

        self.CheckBox_W.SetValue(True)
        self.CheckBox_T.SetValue(True)
        self.CheckBox_R.SetValue(True)
        self.on_btn_clear(None)
        self.UpdateButtons()
        
    def on_tab_change(self, event):
        if self.nb.GetSelection()==1: 
            self.menu_new_experiment.Enable(False)
            self.menu_load_experiment.Enable(False)
            self.menu_load_R.Enable(False)
            self.menu_load_T.Enable(False)
            self.menu_save_experiment_as.Enable(False)
        else:
            self.menu_new_experiment.Enable(True)
            self.menu_load_experiment.Enable(True)
            self.menu_load_R.Enable(True)
            self.menu_load_T.Enable(True)
            self.menu_save_experiment_as.Enable(True)

    def on_menu_new_multilayer(self, event):
        if self.CheckIfMultiSaved():
            self.multilayer.clear()
            self.multilayer.add(layer(name="TopLayer",file1="n/air.in3",fr1="100"))
            self.multilayer.add(layer(name="BottomLayer",file1="n/air.in3",fr1="100"))
            self.dlg_edit.load(0)
            self.dlg_poynting.load(0)
            self.dlg_thick.load()
            self.ema()
            self.UpdateButtons()

    def on_menu_open_multilayer(self, event):
        if self.CheckIfMultiSaved():
            dlg = wx.FileDialog(self, "Open Multilayer",self.StructureDir, path.split(self.multilayer.filename)[1], "str files (*.str)|*.str|" "All files (*.*)|*.*", wx.FD_OPEN)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    self.multilayer.clear()
                    self.multilayer.filename = dlg.GetPath()
                    OpenMultilayer(self.multilayer)
                    self.dlg_edit.load(0)
                    self.dlg_poynting.load(0)
                    self.dlg_thick.load()
                    self.ema()
                    self.UpdateButtons()

            except:
                dlg = wx.MessageDialog(self, "Generic problem",
                  'Caption', wx.OK | wx.ICON_INFORMATION)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
            dlg.Destroy()

    def on_menu_edit_multilayer(self, event):
        self.dlg_edit.update_fields()
        self.multilayer.saved=False
        self.dlg_edit.ShowModal()
        #self.dlg_thick.load()
        self.ema()
        self.UpdateButtons()
        self.dlg_poynting.load(0)

    def on_menu_save_multilayer(self, event):
        if self.multilayer.filename != "Untitled":
            SaveMultilayer(self.multilayer)
        else:
            self.on_menu_save_as_multilayer(None)

    def on_menu_save_multilayer_as(self, event):
        if len(self.multilayer.layer) > 1:
            dlg = wx.FileDialog(self, "Save Multilayer As", self.StructureDir, "", "str files (*.str)|*.str|" "All files (*.*)|*.*", wx.FD_SAVE)
            retcode = dlg.ShowModal()
            filename = dlg.GetPath()
            dlg.Destroy()
            if filename[-4:] != ".str": filename = filename + ".str"
            if retcode == wx.ID_OK:
                if FileExists(filename):
                    dlg = wx.MessageDialog(self, "File already exists: do you want to overwrite ?", "Warning !", wx.OK|wx.CANCEL)
                    retcode = dlg.ShowModal()
                    dlg.Destroy()
                    if retcode == wx.ID_OK:
                        self.multilayer.filename=filename
                        SaveMultilayer(self.multilayer)
                else:
                    self.multilayer.filename=filename
                    SaveMultilayer(self.multilayer)
        self.UpdateButtons()

    def on_menu_new_experiment(self, event):
        if self.CheckIfExpSaved():
            self.experiment.clear()
            self.on_btn_clear(None)
            self.UpdateButtons()

    def on_menu_load_experiment(self, event):
        if self.CheckIfExpSaved():
            wildcard = "*.dat|*.dat|" "*.txt|*.txt"
            dlg = wx.FileDialog(self, "Open Experiment", self.ExpDir, "", wildcard, wx.FD_OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.experiment.clear()
                self.experiment.filename=dlg.GetPath()
                if LoadExperiment(self.experiment)=="":
                    dlg = wx.MessageDialog(self, "Single dataset found: data loaded as Transmittance !", "Warning !", wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    for d in self.experiment.data:
                        d.R=0
                self.on_btn_clear(None)
                self.ExpDir=path.split(self.experiment.filename)[0]
            dlg.Destroy()
            self.UpdateButtons()

    def on_menu_load_R(self, event):
        if self.CheckIfExpSaved():
            wildcard = "*.dat|*.dat|" "*.txt|*.txt"
            dlg = wx.FileDialog(self, "Open Experiment", self.ExpDir, "", wildcard, wx.FD_OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.experiment_buffer.clear()
                self.experiment_buffer.filename=dlg.GetPath()
                LoadExperiment(self.experiment_buffer)
                self.ExpDir=path.split(self.experiment_buffer.filename)[0]
                if len(self.experiment.data) == 0:
                    self.experiment.add(data(lam=1E-100,R=0.0,T=0.0))
                    self.experiment.add(data(lam=1E100,R=0.0,T=0.0))
                    self.experiment.lmin=self.experiment.data[0].lam
                    self.experiment.lmax=self.experiment.data[-1].lam
                lmin=max(self.experiment.lmin,self.experiment_buffer.lmin)
                lmax=min(self.experiment.lmax,self.experiment_buffer.lmax)
                lR,lT=[],[]
                expR,expT=[],[]
                for d in self.experiment_buffer.data:
                    lR.append(round(d.lam,3))
                    expR.append([d.lam,d.R])
                for d in self.experiment.data:
                    lT.append(round(d.lam,3))
                    expT.append([d.lam,d.T])
                lRT=sortRemoveDupes(lR+lT)
                del self.experiment.data[:]
                for l in lRT:
                    if lmin <= l <= lmax:
                        self.experiment.add(data(lam=l,R=Interpol(expR,l),T=Interpol(expT,l)))
                self.experiment.lmin=self.experiment.data[0].lam
                self.experiment.lmax=self.experiment.data[-1].lam
                self.experiment.saved=False
                self.on_btn_clear(None)
            dlg.Destroy()
            self.UpdateButtons()

    def on_menu_load_T(self, event):
        if self.CheckIfExpSaved():
            wildcard = "*.dat|*.dat|" "*.txt|*.txt"
            dlg = wx.FileDialog(self, "Open Experiment", self.ExpDir, "", wildcard, wx.FD_OPEN)
            if dlg.ShowModal() == wx.ID_OK:
                self.experiment_buffer.clear()
                self.experiment_buffer.filename=dlg.GetPath()
                LoadExperiment(self.experiment_buffer)
                self.ExpDir=path.split(self.experiment_buffer.filename)[0]
                if len(self.experiment.data) == 0:
                    self.experiment.add(data(lam=1E-100,R=0.0,T=0.0))
                    self.experiment.add(data(lam=1E100,R=0.0,T=0.0))
                    self.experiment.lmin=self.experiment.data[0].lam
                    self.experiment.lmax=self.experiment.data[-1].lam
                lmin=max(self.experiment.lmin,self.experiment_buffer.lmin)
                lmax=min(self.experiment.lmax,self.experiment_buffer.lmax)
                lR,lT=[],[]
                expR,expT=[],[]
                for d in self.experiment.data:
                    lR.append(round(d.lam,3))
                    expR.append([d.lam,d.R])
                for d in self.experiment_buffer.data:
                    lT.append(round(d.lam,3))
                    expT.append([d.lam,d.T])
                lRT=sortRemoveDupes(lR+lT)
                del self.experiment.data[:]
                for l in lRT:
                    if lmin <= l <= lmax:
                        self.experiment.add(data(lam=l,R=Interpol(expR,l),T=Interpol(expT,l)))
                self.experiment.lmin=self.experiment.data[0].lam
                self.experiment.lmax=self.experiment.data[-1].lam
                self.experiment.saved=False
                self.on_btn_clear(None)
            dlg.Destroy()
            self.UpdateButtons()

    def on_menu_save_experiment(self, event):
        if self.experiment.filename != "Untitled":
            SaveExperiment(self.experiment)
        else:
            self.on_menu_save_experiment_as(None)

    def on_menu_save_experiment_as(self, event):
        #if self.nb.GetSelection() == 1: self.exppanel.on_btn_save(None)
        if len(self.experiment.data) > 0:
            dlg = wx.FileDialog(self, "Save Experiment As", self.ExpDir, "", "data files (*.dat)|*.dat", wx.FD_SAVE)
            retcode = dlg.ShowModal()
            filename = dlg.GetPath()
            dlg.Destroy()
            if filename[-4:] != ".dat": filename = filename + ".dat"
            if retcode == wx.ID_OK:
                if FileExists(filename):
                    dlg = wx.MessageDialog(self, "File already exists: do you want to overwrite ?", "Warning !", wx.OK|wx.CANCEL)
                    retcode = dlg.ShowModal()
                    dlg.Destroy()
                    if retcode == wx.ID_OK:
                        self.experiment.filename=filename
                        SaveExperiment(self.experiment,float(self.txt_wave_min.GetValue()),float(self.txt_wave_max.GetValue()))
                        self.ExpDir=path.split(self.experiment.filename)[0]
                else:
                    self.experiment.filename=filename
                    SaveExperiment(self.experiment,float(self.txt_wave_min.GetValue()),float(self.txt_wave_max.GetValue()))
                    self.ExpDir=path.split(self.experiment.filename)[0]
        self.UpdateButtons()

    def on_menu_settings(self, event):
        dlg = SettingsDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.settings["PlotPoints"]=dlg.txt_plot_points.GetValue()
            self.settings["StDev"]=dlg.txt_st_dev.GetValue()
            self.settings["Fi"]=dlg.txt_Fi.GetValue()
            self.settings["StructureDir"]=dlg.txt_structure_dir.GetValue()
            self.settings["IndexDir"]=dlg.txt_index_dir.GetValue()
            self.settings["ExpDir"]=dlg.txt_experimental_dir.GetValue()
            self.settings["RefFile"]=dlg.txt_reference.GetValue()
            SaveConf(self.settings)
            self.loadconf()
        dlg.Destroy()

    def on_menu_about(self, event):
        msg=[]
        msg.append("Optical")
        msg.append("Copyright (C) 2005-"+str(year)+" Emanuele Centurioni")
        msg.append("version "+version)
        msg.append("E-mail: centurioni@bo.imm.cnr.it")
        msg.append("")
        msg.append("This program is free software: you can redistribute it and/or")
        msg.append("modify it under the terms of the GNU General Public License")
        msg.append("as published by the Free Software Foundation, either version")
        msg.append("3 of the License, or (at your option) any later version.")
        msg.append("")
        msg.append("This program is distributed in the hope that it will be")
        msg.append("useful, but WITHOUT ANY WARRANTY; without even the implied")
        msg.append("warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.")
        msg.append("See the GNU General Public License for more details.")
        msg.append("")
        msg.append("You should have received a copy of the GNU General Public")
        msg.append("License along with this program.")
        msg.append("If not, see <http://www.gnu.org/licenses/>.")

        testo=""
        for m in msg:testo+=m+"\n"

        dlg = wx.MessageDialog(self, testo, "About", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def on_btn_poynting(self, event):
        self.dlg_poynting.update_fields()
        #self.dlg_poynting.load(0)
        self.dlg_poynting.ShowModal()

    def on_btn_energy_profile(self, event):
        #compute light energy flux profile for a single wavelength
        error=False
        if not self.multilayer.lmin <= self.wavelength_profile <= self.multilayer.lmax:self.wavelength_profile=self.multilayer.lmin
        dlg = wx.TextEntryDialog(self, 'Please choose wavelength and number of points / layer', 'Energy flux depth profile calculation', str(self.wavelength_profile)+" , "+str(self.points_profile))
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                Fi=float(self.txt_angle.GetValue())
                Fi=pi*Fi/180.0
                self.wavelength_profile,self.points_profile=float(answer.split(",")[0]),int(answer.split(",")[1])
                if self.multilayer.lmin <= self.wavelength_profile <= self.multilayer.lmax:
                    lam=[self.wavelength_profile]
                    structure=PrepareList(self.multilayer,lam)
                    E=[]
                    CumThick=0.0
                    for layer in self.multilayer.layer[1:-1]:#exclude top and bottom layer
                        thick=float(layer.thickness)
                        j=self.multilayer.layer.index(layer)
                        for i in range(self.points_profile-1):
                            x=i*1.0/(self.points_profile-1)
                            A=ComputeFlux(structure,lam,Fi,j,x)
                            E.append([CumThick+x*thick,A[0]])
                        CumThick=CumThick+thick
                    A=ComputeFlux(structure,lam,Fi,j,1)
                    E.append([CumThick,A[0]])
                    SaveFluxProfile(E)
                else:error=True
        finally:
            dlg.Destroy()
        if error:
            dlg = wx.MessageDialog(self, 'Wavelength is out of range !',
              ' ', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()

    def on_btn_alpha(self, event):
        dlg = wx.TextEntryDialog(self, 'Layer', 'Select layer (top layer = 1)', '1')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                layer = int(dlg.GetValue())
        finally:
            dlg.Destroy()

        #compute absorption coefficient
        self.ema()
        self.checkrange()
        start=max(float(self.txt_wave_min.GetValue()),self.multilayer.lmin)
        end=min(float(self.txt_wave_max.GetValue()),self.multilayer.lmax)
        Fi=float(self.txt_angle.GetValue())
        Fi=pi*Fi/180.0

        thick=float(self.multilayer.layer[layer].thickness)
        thick=thick*1E-8#convert from A to cm

        lam,Ti,a=[],[],[]
        for d in self.experiment.data:
            if start<= d.lam <= end:
                #print(d.lam,d.T,d.R)
                if d.T>0.01 and d.T/(1-d.R)<1:
                #if d.T/(1-d.R)<1:
                    lam.append(d.lam)
                    Ti.append(d.T/(1-d.R))
                    a.append((-1/thick)*log(d.T/(1-d.R)))#guess value for alpha

        structure=PrepareList(self.multilayer,lam)
        a=Alpha(structure,lam,Ti,a,Fi,layer)
#        
        SaveAlpha(lam,a,self.experiment.filename)
        n=structure[layer][1]
        SaveAlphaIn3(None,lam,n,a,self.experiment.filename)

        dlg = wx.MessageDialog(self, "Alpha.dat and Alpha.in3 saved in "+self.CurDir,'Absorption coefficient computed', wx.OK | wx.ICON_INFORMATION)
        try:
            dlg.ShowModal()
        finally:
            dlg.Destroy()


#        dlg=Tauc.Tauc(self)
#        try:
#            dlg.ShowModal()
#        finally:
#            dlg.Destroy()

    def on_btn_thick_det(self, event):
        self.multilayer.saved=False
        self.dlg_thick.update_fields()
        self.dlg_thick.ShowModal()

    def on_btn_chi_test(self,event):
        self.dlg_thick.show_chi()
        self.dlg_thick.ShowModal()

    def on_btn_compute(self,event):
        self.ema()
        self.checkrange()
        start=max(float(self.txt_wave_min.GetValue()),self.multilayer.lmin)
        end=min(float(self.txt_wave_max.GetValue()),self.multilayer.lmax)

        if end > start:
            Fi=float(self.txt_angle.GetValue())
            Fi=pi*Fi/180.0

            lam=[]
            for i in range(self.PlotPoints):
                lam.append(start+i*(end-start)/(self.PlotPoints-1))
            lam[-1]=end#to be sure last point is exactly end

            structure=PrepareList(self.multilayer,lam)
            R,T=ComputeRT(structure,lam,Fi)
            if self.CheckBox_A.GetValue():self.axes.plot(lam,100*(1-R-T))
            if self.CheckBox_T.GetValue():self.axes.plot(lam,100*T)
            if self.CheckBox_R.GetValue():self.axes.plot(lam,100*R)
            self.canvas.draw()

            SaveRT(lam,T,R)
        else:
            dlg = wx.MessageDialog(self, 'No points to plot ! Check wavelength range.','Warning', wx.OK | wx.ICON_INFORMATION)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()

    def on_btn_clear(self,event):
        self.axes.clear()
        self.axes.set_ylabel('%')
        self.axes.set_xlabel('Wavelength (nm)')
        self.axes.set_ylim(0,110)
        #self.axes.set_xlim(300,1100)
        self.axes.grid(True)
        #self.axes.set_autoscaley_on(False)
        #print self.axes.get_xlim()
        self.PlotExperiment()
        self.canvas.draw()

    def UpdateButtons(self):
        self.SetTitle("Optical "+version+" Multilayer = "+path.split(self.multilayer.filename)[1]+"    Experiment = "+path.split(self.experiment.filename)[1])

        #if len(self.experiment.data)>0 and len(self.multilayer.layer)>2:
        #    self.btn_thick_det.Enable(True)
        #    self.btn_chi_test.Enable(True)
        #else:
        #    self.btn_thick_det.Enable(False)
        #    self.btn_chi_test.Enable(False)

        if len(self.multilayer.layer)>2:
            self.btn_poynting.Enable(True)
            self.btn_energy_profile.Enable(True)
            if len(self.experiment.data)>0:
                self.btn_thick_det.Enable(True)
                self.btn_chi_test.Enable(True)
                self.btn_alpha.Enable(True)
            else:
                self.btn_thick_det.Enable(False)
                self.btn_chi_test.Enable(False)
                self.btn_alpha.Enable(False)
        else:
            self.btn_poynting.Enable(False)
            self.btn_energy_profile.Enable(False)
            #self.btnEFluxProfile.Enable(False)
            self.btn_thick_det.Enable(False)
            self.btn_chi_test.Enable(False)
            self.btn_alpha.Enable(False)

    def checkrange(self):
        if len(self.experiment.data)>0:
            lmin=min(self.multilayer.lmin,self.experiment.lmin)
            lmax=max(self.multilayer.lmax,self.experiment.lmax)
        else:
            lmin=self.multilayer.lmin
            lmax=self.multilayer.lmax
        if lmin > float(self.txt_wave_min.GetValue()):self.txt_wave_min.SetValue(str(lmin))
        if lmax < float(self.txt_wave_max.GetValue()):self.txt_wave_max.SetValue(str(lmax))
        if self.CheckBox_W.GetValue():
            self.txt_wave_min.SetValue(str(lmin))
            self.txt_wave_max.SetValue(str(lmax))

    def PlotExperiment(self):
        if len(self.experiment.data)>0:
            self.checkrange()
            start=float(self.txt_wave_min.GetValue())
            end=float(self.txt_wave_max.GetValue())

            lam,R,T=[],[],[]
            for d in self.experiment.data:
                if start<= d.lam <= end:
                    lam.append(d.lam)
                    R.append(d.R)
                    T.append(d.T)
            if len(lam)>0:
                R=array(R)
                T=array(T)
                if self.CheckBox_A.GetValue():self.axes.plot(lam,100*(1-R-T),color="black",linewidth=2)
                if self.CheckBox_T.GetValue():self.axes.plot(lam,100*T,color="blue",linewidth=2)
                if self.CheckBox_R.GetValue():self.axes.plot(lam,100*R,color="green",linewidth=2)

    def update_coords(self,event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            text="%.1f nm" %(x)+"  %.2f eV" %((1240/x))+"  %.2f cm-1" %(1E7/x)+"  %.2f " %(y)+"%"
            #text=text+"   Multilayer = "+path.split(self.multilayer.filename)[1]+"    Experiment = "+path.split(self.experiment.filename)[1]
            self.statusBar.SetStatusText((text),0)#"%1.2f" %(12400/x)

    def ema(self):
        try:
            EMA(self.multilayer)
            CheckWaveRange(self.multilayer)
        except:
            for layer in self.multilayer.layer:
                test=multilayer()
                test.add(layer)
                try:
                    EMA(test)
                except:
                    dlg = wx.MessageDialog(self, "Layer "+layer.name+" has index files missing or corrupted, please check !","",wx.OK | wx.ICON_INFORMATION)
                    try:
                        dlg.ShowModal()
                    finally:
                        dlg.Destroy()

    def CheckIfExpSaved(self):
        OK=True
        if False:#this experiment saved check has been removed to avoid unwanted old data file overwrite
        #if not self.experiment.saved:
            OK=False
            dlg=wx.MessageDialog(self, "The current experiment has been modified.\nDo you want to save your changes ?", "Warning !", wx.YES|wx.NO|wx.CANCEL)
            retcode = dlg.ShowModal()
            dlg.Destroy()
            if retcode == wx.ID_YES or retcode == wx.ID_NO:
                OK=True
                if retcode == wx.ID_YES:
                    self.on_menu_save_experiment(None)
        return OK

    def CheckIfMultiSaved(self):
        OK=True
        if not self.multilayer.saved:
            OK=False
            dlg=wx.MessageDialog(self, "The current Multilayer has been modified.\nDo you want to save your changes ?", "Warning !", wx.YES|wx.NO|wx.CANCEL)
            retcode = dlg.ShowModal()
            dlg.Destroy()
            if retcode == wx.ID_YES or retcode == wx.ID_NO:
                OK=True
                if retcode == wx.ID_YES:
                    self.on_menu_save_multilayer(None)
        return OK

    def on_close(self, event):#controlla la chiusura del programma principale
        if self.CheckIfMultiSaved() and self.CheckIfExpSaved():
            try:self.spectrometer.run=False
            except:pass
            self.dlg_edit.Destroy()
            self.dlg_thick.Destroy()
            self.dlg_poynting.Destroy()
            #os.remove("Lock")
            self.Destroy()

    def loadconf(self):

        #set relative path to directory containig structures
        StructureDir=self.settings["StructureDir"]
        StructureDir=StructureDir.replace("\\","/")#for win compatibility
        self.StructureDir=path.normpath(self.CurDir+"/"+StructureDir)

        #set relative path to directory containig refraction indexes
        IndexDir=self.settings["IndexDir"]        
        IndexDir=IndexDir.replace("\\","/")#for win compatibility
        self.IndexDir=path.normpath(self.CurDir+"/"+IndexDir)

        #set absolute path to directory containig experimental data
        ExpDir=self.settings["ExpDir"]        
        ExpDir=ExpDir.replace("\\","/")#for win compatibility
        self.ExpDir=path.normpath(self.CurDir+"/"+ExpDir)

        #set accuracy of experimental data
        StDev=float(self.settings["StDev"])
        self.StDev=StDev/100.0

        #Set number of points used in the plot
        PlotPoints=int(self.settings["PlotPoints"])
        self.PlotPoints=PlotPoints

        #set default incidence angle
        Fi=self.settings["Fi"]
        self.txt_angle.SetValue(Fi)

        #set reference reflectivity
        RefFile=self.settings["RefFile"]        
        self.RefFile=path.normpath(self.CurDir+"/"+RefFile)

        self.ref=loadref(self.RefFile)

app = wx.App()
frame = MainFrame()
frame.Centre()
frame.Show()
app.MainLoop()
