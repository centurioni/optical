#Optical, Copyright (C) 2005  Emanuele Centurioni
#see Optical.py

import time
#from Numeric import *
from numpy import *
from os import path, getcwd
from os import name as osname

#class settings:
#    def __init__(self,dir="structure/"):
#        self.filename=filename
#        self.name=name
#        self.saved=saved
#        self.lmin=lmin
#        self.lmax=lmax
#        self.index_dir=index_dir
#        self.struture_dir=structure_dir
#        self.layer=[]
#    def load(self):
#        pass
#    def save(self):
#        pass

class experiment:
    def __init__(self,filename="Untitled",name="Untitled",saved=True,lmin=200,lmax=1100):
        self.filename=filename
        self.name=name
        self.saved=saved
        self.lmin=lmin
        self.lmax=lmax
        self.data=[]
    def add(self,data):
        self.data.append(data)
    def remove(self,):
        self.data.remove(data)
    def clear(self):
        del self.data[:]
        self.filename="Untitled"
        self.name="Untitled"
        self.saved=True

class data:
    def __init__(self,lam=0,T=0,R=0):
        self.lam=lam
        self.T=T
        self.R=R

class multilayer:#
    def __init__(self,filename="Untitled",name="Untitled",saved=True,lmin=200,lmax=1100):
        self.filename=filename
        self.name=name
        self.saved=saved
        self.lmin=lmin
        self.lmax=lmax
        #self.index_dir=index_dir
        #self.struture_dir=structure_dir
        self.layer=[]
    def add(self,l):
        self.layer.append(l)
    def remove(self,l):
        self.layer.remove(l)
    def insert(self,l):
        i=self.layer.index(l)+1
        emptylayer=layer()
        self.layer.insert(i,emptylayer)
    def clear(self):
        del self.layer[:]
        self.filename="Untitled"
        self.name="Untitled"
        self.saved=True

class layer:#
    def __init__(self,name="Unnamed",file1="n/air.in3",file2="Not_selected",file3="Not_selected",fr1="100",fr2="0",fr3="0",thickness="0",incoherent="0",roughness="0",ln=[],lk=[]):
        self.name=name
        self.file1=file1
        self.file2=file2
        self.file3=file3
        self.fr1=fr1# % fraction of first EMA
        self.fr2=fr2
        self.fr3=fr3
        self.thickness=thickness
        self.incoherent=incoherent#True if the layer has to be treated as inchoerent
        self.roughness=roughness#top roughness in A
        self.ln=ln
        self.lk=lk

def EMA(multilayer):
    #computes n and k for a mixed material using
    #effective medium approximation (EMA)
    for layer in multilayer.layer:
        fr1,fr2,fr3=int(layer.fr1),int(layer.fr2),int(layer.fr3)
        if fr1==100:#just one medium, no EMA
            layer.ln,layer.lk=ReadIn3(layer.file1)
        else:#EMA 2 or 3 mediums
            n,k=[],[]
            nt,kt=ReadIn3(layer.file1)
            n.append(nt)
            k.append(kt)
            nt,kt=ReadIn3(layer.file2)
            n.append(nt)
            k.append(kt)
            n.append(0)
            k.append(0)
            if fr3 == 0:#just 2 mediums
                n[2],k[2]=nt,kt
            else:#O.K. 3 mediums
                n[2],k[2]=ReadIn3(layer.file3)

            ln,lk=[],[]
            for j in range(3):
                lnt,lkt=[],[]
                for h in range(len(n[j])):
                    lnt.append(n[j][h][0])
                for h in range(len(k[j])):
                    lkt.append(k[j][h][0])
                ln.append(lnt)
                lk.append(lkt)
            
            lmin=max(min(ln[0]),min(ln[1]),min(ln[2]),min(lk[0]),min(lk[1]),min(lk[2]))
            lmax=min(max(ln[0]),max(ln[1]),max(ln[2]),max(lk[0]),max(lk[1]),max(lk[2]))
            
            ln=ln[0]+ln[1]+ln[2]+[lmin,lmax]
            lk=lk[0]+lk[1]+lk[2]+[lmin,lmax]
            
            ln=sortRemoveDupes(ln)
            lk=sortRemoveDupes(lk)

            lnt=ln[:]
            ln=[]
            for j in lnt:
                if lmin <= j <= lmax:
                    ln.append(j)
                    
            lkt=lk[:]
            lk=[]
            for j in lkt:
                if lmin <= j <= lmax:
                    lk.append(j)
            
            nn,nk=[],[]
            fr=[fr1,fr2,fr3]
            for lam in ln:
                ne=[]
                for h in range(3):
                    nr=Interpol(n[h],lam)
                    ni=Interpol(k[h],lam)
                    ne.append(nr+ni*(1j))
                nn.append([lam, EMA3(ne, fr).real])
                
            for lam in lk:
                ne=[]
                for h in range(3):
                    nr=Interpol(n[h],lam)
                    ni=Interpol(k[h],lam)
                    ne.append(nr+ni*(1j))
                nk.append([lam, EMA3(ne, fr).imag])
                
            layer.ln=nn
            layer.lk=nk

def ReadIn3(filename):
    #load n and k from an index file *.in3
    n=[]
    k=[]
    filename=filename.replace("\\","/")#for win compatibility
    in_file=open(path.normpath(filename),"r")
    line=in_file.readline()
    line=in_file.readline()
    line=in_file.readline()
    nn=int(CleanRecord(line))
    for i in range(nn):
        line=in_file.readline()
        answer=CleanRecord(line).split()
        n.append([float(answer[0])/10.0, float(answer[1])])
    
    line=in_file.readline()
    nk=int(CleanRecord(line))
    for i in range(nk):
        line=in_file.readline()
        answer=CleanRecord(line).split()
        k.append([float(answer[0])/10.0, float(answer[1])])
    in_file.close()
    
    return n,k

def CleanRecord(a):
    if a[-2:]=="\r\n":#remove from string Ms format end of record
        a=a[:-2]
    elif a[-1:]=="\n":#remove from string Unix format end of record
        a=a[:-1]
    a=a.replace(","," ")
    return a

def CleanRecord2(a):
    if a[-2:]=="\r\n":#remove from string Ms format end of record
        a=a[:-2]
    elif a[-1:]=="\n":#remove from string Unix format end of record
        a=a[:-1]
    return a

def SaveMultilayer(multilayer):
    #save a multilayer
    out_file=open(multilayer.filename,"w",newline='')
    out_file.write(multilayer.name+"\r\n")
    for layer in multilayer.layer:
        record = ""
        record = record+layer.name+","
        record = record+layer.file1+","
        record = record+layer.file2+","
        record = record+layer.file3+","
        record = record+layer.fr1+","
        record = record+layer.fr2+","
        record = record+layer.fr3+","
        record = record+str(int(round(float(layer.thickness)*10)))+","
        record = record+str(layer.incoherent)+","
        record = record+str(int(round(float(layer.roughness)*10)))+"\r\n"
        out_file.write(record)
    out_file.close()
    multilayer.saved=True

def OpenMultilayer(multilayer):
    #load a multilayer
    in_file=open(multilayer.filename,"r")
    line=in_file.readline()
    multilayer.name=CleanRecord2(line)
    while True:
        line=in_file.readline()
        if len(line)==0:
            break
        v=CleanRecord2(line).split(",")
        if len(v)==9:v.append("0")#for compatibility with ver 0.15 and older
        l=layer(name=v[0],file1=v[1],file2=v[2],file3=v[3],fr1=v[4],fr2=v[5],fr3=v[6],thickness=str(float(v[7])/10.0),incoherent=v[8],roughness=str(float(v[9])/10.0))
        multilayer.add(l)
    in_file.close()
    multilayer.saved=True

def Interpol(a,l):
    #linear interpolation
    for i in range(len(a)):
        if a[i][0]==l:
            n=a[i][1]
            break
        if a[i][0]>l:
            n = a[i-1][1] + 1.0*(l - a[i-1][0]) / (a[i][0] - a[i-1][0]) * \
            (a[i][1] - a[i-1][1])
            break
    return n

def PrepareList(multilayer,l):
    #prepare list for globscatmatr
    b=[]
    for layer in multilayer.layer:
        n=[]
        for lam in l:
            nr=Interpol(layer.ln,lam)
            ni=Interpol(layer.lk,lam)
            n.append(nr+ni*(1j))
        #b.append([int(float(layer.thickness)), n, int(layer.incoherent), int(layer.roughness)])
        b.append([float(layer.thickness), n, int(layer.incoherent), float(layer.roughness)])
    return b

def sortRemoveDupes(lst):
    """Sort the list, and remove duplicate symbols.
    """
    if len(lst) == 0:
        return lst
    lst.sort()
    lst = [lst[0]] + [lst[i] for i in range(1, len(lst))
            if lst[i] != lst[i - 1]]
    return lst

def EMA3(n, fr):
    #effective medium approximation 3 medium 
    e1,e2,e3=n[0]**2,n[1]**2,n[2]**2
    f1,f2,f3=fr[0]/100.0,fr[1]/100.0,fr[2]/100.0
    nguess=f1*n[0]+f2*n[1]+f3*n[2]
    a=-4
    b=f1*(4*e1-2*(e2+e3))+f2*(4*e2-2*(e1+e3))+f3*(4*e3-2*(e1+e2))
    c=f1*(2*e1*(e2+e3)-e2*e3)+f2*(2*e2*(e1+e3)-e1*e3)+f3*(2*e3*(e1+e2)-e1*e2)
    d=(f1+f2+f3)*(e1*e2*e3)
    e=root3(a,b,c,d)
    pn=[e[0]**(0.5),e[1]**(0.5),e[2]**(0.5)]
    distance=[abs(pn[0]-nguess), abs(pn[1]-nguess), abs(pn[2]-nguess)]
    return pn[distance.index(min(distance))]

def root3(a,b,c,d):
    #finds roots of eq ax^3+bx^2+cx+d=0
    a,b,c=b/a,c/a,d/a
    p=(-a**2)/3+b
    q=(2*a**3)/27-a*b/3+c
    u1=(-q/2+((q**2)/4+(p**3)/27)**(0.5))**(1.0/3)
    u,x=[],[]
    u.append(u1)#there are 3 roots for u
    u.append(u1*exp(2*pi/3*1j))
    u.append(u1*exp(4*pi/3*1j))
    for i in range(3):
        x.append(u[i]-p/(3*u[i])-a/3)
    return x

def CheckWaveRange(multilayer):
    #return wavelength range that can be computed
    lmin,lmax=[],[]
    for layer in multilayer.layer:
        n=layer.ln
        k=layer.lk
        ln,lk=[],[]
        for h in range(len(n)):
            ln.append(n[h][0])
        for h in range(len(k)):
            lk.append(k[h][0])
        lmin.append(max(min(ln),min(lk)))
        lmax.append(min(max(ln),max(lk)))
    multilayer.lmin=max(lmin)
    multilayer.lmax=min(lmax)

def SaveRT(lam,T,R):
    #save computed R and T
    out_file=open("RT.dat","w",newline='')
    out_file.write("#Lam(nm)  R%(0-100)  T%(0-100)"+"\r\n")
    for i in range(len(lam)):
        record = ""
        record = record+"%.3f  " % lam[i]
        record = record+"%.3f  " % (R[i]*100)
        record = record+"%.3f  " % (T[i]*100)
        record = record+"\r\n"
        out_file.write(record)
    out_file.close()

def SaveLayerAbsorption(lam,A):
    #save internal light absorption
    out_file=open("Layer_absorption.dat","w",newline='')
    out_file.write("#Lam(nm)      A(%)"+"\r\n")
    for i in range(len(lam)):
        record = ""
        record = record+str(lam[i])+" "
        record = record+str(A[i]*100)+" "
        record = record+"\n"
        out_file.write(record)
    out_file.close()

def SavePoyntingFlux(lam,F):
    #save light energy flux
    out_file=open("Poynting_energy_flux.dat","w",newline='')
    out_file.write("#Lam(nm)      Flux(%)"+"\r\n")
    for i in range(len(lam)):
        record = ""
        record = record+str(lam[i])+" "
        record = record+str(F[i]*100)+" "
        record = record+"\n"
        out_file.write(record)
    out_file.close()

def SaveAlpha(lam,A,sample):
    #save absorption coefficient generated by alpha
    out_file=open("Alpha.dat","w",newline='')
    out_file.write("#Lam(nm)      Alpha(cm^-1)      "+sample+"\n")
    for i in range(len(lam)):
        record = ""
        record = record+str(round(lam[i],3))+" "
        record = record+str(round(A[i],3))+" "
        record = record+"\n"
        out_file.write(record)
    out_file.close()

def SaveAlphaIn3(filename,lam,n,a,sample):
    #save index of refraction generated by alpha
    #out_file=open(filename,"w")
    out_file=open("Alpha.in3","w",newline='')
    out_file.write("#Generated by Alpha      "+sample+"\n")
    
    lmin=min(lam)
    lmax=max(lam)
    
    out_file.write(str(round(lmin*10,2))+" "+str(round(lmax*10,2))+"\n")

    out_file.write(str(len(n))+"\n")        
    for i in range(len(n)):
        out_file.write(str(round(lam[i]*10,2))+" "+str(round(n[i].real,3))+"\n")

    out_file.write(str(len(a))+"\n")
    for i in range(len(a)):
        out_file.write(str(round(lam[i]*10,2))+" "+str(round(a[i]*lam[i]*1E-8/(4*pi),3))+"\n")

    out_file.close()

def SaveExperiment(experiment,lmin,lmax):
    #save computed R and T
    out_file=open(experiment.filename,"w",newline='')
    out_file.write("#Lam(nm)  R%(0-100)  T%(0-100)"+"\r\n")
    for data in experiment.data:
        record = ""
        if lmin <= data.lam <= lmax:
            record = record+"%.3f  " % data.lam
            record = record+"%.3f  " % (data.R*100)
            record = record+"%.3f  " % (data.T*100)
            record = record+"\r\n"
            out_file.write(record)
    out_file.close()
    experiment.saved=True

def SaveData(filename,unit,data):
    #save generic data
    out_file=open(filename,"w",newline='')
    out_file.write("#Lam(nm)  "+unit+"\r\n")
    for i in range(len(data)):
        out_file.write("%.3f  " % (data[i][0])+"%.3f  " % (data[i][1])+"\r\n")
    out_file.close()

def LoadExperiment(experiment):
    #print(experiment.filename,type(experiment.filename))
    infile=open(experiment.filename,"r")
    text=infile.readlines()
    infile.close()
    del text[0]
    #load experimental R and T spectra
    #if True:
    try:#try new format, R and T on the same file
        for line in text:
            values=CleanRecord(line).split()
            experiment.add(data(lam=float(values[0]),R=float(values[1])/100.0,T=float(values[2])/100.0))
        experiment.lmin=experiment.data[0].lam
        experiment.lmax=experiment.data[-1].lam
        return "##"
    #if False:
    except:
        #load experimental R and T from separate files, both files with same name beginning with R and T (old format)
        pa=path.split(experiment.filename)
        path_R,path_T="",""
        if path.exists(path.join(pa[0],"R"+pa[1][1:])):path_R=path.join(pa[0],"R"+pa[1][1:])
        if path.exists(path.join(pa[0],"r"+pa[1][1:])):path_R=path.join(pa[0],"r"+pa[1][1:])
        if path.exists(path.join(pa[0],"T"+pa[1][1:])):path_T=path.join(pa[0],"T"+pa[1][1:])
        if path.exists(path.join(pa[0],"t"+pa[1][1:])):path_T=path.join(pa[0],"t"+pa[1][1:])

        textR,textT,x="","","##"
        if path_R=="" or path_T=="":#single file  case without R or T at the beginning
            path_T,path_R,x=experiment.filename,experiment.filename,""

        try:
            infile=open(path_R,"r")
            textR=infile.readlines()
            infile.close()
            del textR[0]
        except:pass
        try:
            infile=open(path_T,"r")
            textT=infile.readlines()
            infile.close()
            del textT[0]
        except:pass

        expR=[]
        for line in textR:
            values=CleanRecord(line).split()
            expR.append([float(values[0]),float(values[1])/100.0])
        expT=[]
        for line in textT:
            values=CleanRecord(line).split()
            expT.append([float(values[0]),float(values[1])/100.0])

        if len(expR)==0:
            expR=[[1E-6,0.0],[1E6,0.0]]
        if len(expT)==0:
            expT=[[1E-6,0.0],[1E6,0.0]]

        lR,lT=[],[]
        for j in range(len(expR)):
            lR.append(expR[j][0])
        for j in range(len(expT)):
            lT.append(expT[j][0])
        
        lmin=max(min(lR),min(lT))
        lmax=min(max(lR),max(lT))
        lRT=sortRemoveDupes(lR+lT)

        lRTt=lRT[:]
        lRT=[]
        for j in lRTt:
            if lmin <= j <= lmax:
                lRT.append(j)
        
        for l in lRT:
            if lmin <= l <= lmax:
                experiment.add(data(lam=l,R=Interpol(expR,l),T=Interpol(expT,l)))
        experiment.lmin=experiment.data[0].lam
        experiment.lmax=experiment.data[-1].lam
        return x

def Chi(R,T,Re,Te,st_dev):
    #compute chi square test
    Chi_R,Chi_T=0.0,0.0
    for i in range(len(R)):
        Chi_R=Chi_R+((Re[i]-R[i])/st_dev)**2
        Chi_T=Chi_T+((Te[i]-T[i])/st_dev)**2
    Chi_RT = (Chi_R+Chi_T)/(len(R)+len(T))
    Chi_R = Chi_R/len(R)
    Chi_T = Chi_T/len(T)
    
    return Chi_R,Chi_T,Chi_RT

def FileExists(filename):
    #check if a file exists
    try:
        in_file=open(filename,"r")
        in_file.close()
        answer=True
    except:
        answer=False
    return answer

def LoadConf():
    #load some configuration values from "settings.txt"
    try:
        settings={}
        in_file=open("settings.txt","r")
        while True:
            line=in_file.readline()
            if len(line)==0:
                break
            values=CleanRecord2(line).split(",")
            if len(values)==2:
                if len(values[0])>0:
                    if values[0][:1]!="#":
                        settings[values[0]] = values[1]
        in_file.close()
    except:pass
    return settings

def SaveConf(settings):
    out_file=open("settings.txt","w",newline='')
    for c in settings.keys():
        out_file.write(c+","+settings[c]+"\r\n")
    out_file.close()

def loadref(a):
    data=[]
    in_file=open(a,"r")
    line=in_file.readline()
    while True:
        line=in_file.readline()
        if len(line)<2:
            break
        line=line[:-1]
        v=line.split()
        data.append([float(v[0]),float(v[1])])
    in_file.close()
    return data
