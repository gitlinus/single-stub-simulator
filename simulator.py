import tkinter as tk
from tkinter import HORIZONTAL, ttk
from PIL import ImageTk, Image
import cmath
import math

class Simulator(tk.Frame):

    stubType2filename = {"series stub":"series_stub.png", "shunt stub":"shunt_stub.png"}
    defaultCharImpedance=50
    defaultLoadImpedance=50
    precision=3

    def __init__(self, master, width=1200):
        super().__init__(master)
        master.title("Single Stub Tuner Simulator")
        self.width=width
        self.height=width*3/5
        self.ratio=3/5
        self.master=master

        self.rootFrame = tk.Frame(master=self.master, width=width, height=self.height, bg="white")
        self.rootFrame.grid(column=0,row=0)

        self.leftFrame = tk.Frame(master=self.rootFrame, width=width*self.ratio, height=self.height, bg="red")
        self.leftFrame.grid(column=0,row=0)
        self.rightFrame = tk.Frame(master=self.rootFrame, width=width*(1-self.ratio), height=self.height, bg="blue")
        self.rightFrame.grid(column=1,row=0)

        self.rightSelectFrame = tk.Frame(master=self.rightFrame, width=width*(1-self.ratio), height=self.height/2*1/3, bg="#A9A9A9")
        self.rightSelectFrame.grid(column=0,row=0)
        self.rightSelectFrame.grid_propagate(False)
        self.rightDiagramFrame = tk.Frame(master=self.rightFrame, width=width*(1-self.ratio), height=self.height/2*2/3, bg="white")
        self.rightDiagramFrame.grid(column=0,row=1)
        self.rightDiagramFrame.grid_propagate(False)
        self.rightParameterFrame = tk.Frame(master=self.rightFrame, width=width*(1-self.ratio), height=self.height/2, bg="#D3D3D3")
        self.rightParameterFrame.grid(column=0,row=2)
        self.rightParameterFrame.grid_propagate(False)
    
        row=0
        tk.Label(self.rightSelectFrame, text="", bg="#A9A9A9", font=("Times", 14)).grid(column=0,row=row) # spacer
        row+=1
        tk.Label(self.rightSelectFrame, text="Select stub type:", bg="#A9A9A9", font=("Times", 16)).grid(column=0,row=row)
        self.stubType = tk.StringVar(value="series stub")
        self.stubTypeChosen = ttk.Combobox(self.rightSelectFrame, width=20, textvariable=self.stubType)
        self.stubTypeChosen['values'] = ('series stub','shunt stub')
        self.stubTypeChosen.grid(column=1,row=row)
        row+=1
        self.stubTypeChosen.current()
        self.stubTypeChosen['state'] = 'readonly'
        self.stubTypeChosen.bind('<<ComboboxSelected>>',self.handleStubTypeSelection)

        tk.Label(self.rightSelectFrame, text="Select stub termination:", bg="#A9A9A9", font=("Times", 16)).grid(column=0,row=row)
        self.stubTermination = tk.StringVar(value="open")
        self.stubTerminationChosen = ttk.Combobox(self.rightSelectFrame, width=20, textvariable=self.stubTermination)
        self.stubTerminationChosen['values'] = ('open','short')
        self.stubTerminationChosen.grid(column=1,row=2)
        self.stubTerminationChosen.current()
        self.stubTerminationChosen['state'] = 'readonly'
        self.stubTerminationChosen.bind('<<ComboboxSelected>>',self.handleStubTermSelection)

        self.diagramCanvas = tk.Canvas(self.rightDiagramFrame,bg="white",width=(self.width*(1-self.ratio)),height=(self.height/2*2/3))
        self.diagramCanvas.grid(column=0,row=0)
        self.displayDiagram("series_stub.png")

        row=0
        self.Z_1 = complex(self.defaultLoadImpedance)
        self.inputImpedance = self.Z_1
        self.inputImpedanceText = tk.StringVar(value=f"Zin = {self.inputImpedance} Ω, Z1={self.Z_1} Ω")
        self.inputImpedanceEntry = tk.Entry(self.rightParameterFrame, textvariable=self.inputImpedanceText, state="readonly", font=("Times", 14), width=40).grid(column=0,row=row)
        row+=1

        tk.Label(self.rightParameterFrame, text="Parameters", bg="#D3D3D3", font=("Times", 20)).grid(column=0,row=row)
        row+=1

        self.distance=0
        self.distanceSlider = tk.Scale(self.rightParameterFrame,from_=0,to=0.5,digits=3,resolution=0.001,tickinterval=0.1,orient=tk.HORIZONTAL,command=self.getDistance,
                                        length=(self.width*(1-self.ratio)),label="Set distance from load, d (in terms of wavelengths λ)",font=("Times", 14),bg="#D3D3D3")
        self.distanceSlider.set(self.distance)
        self.distanceSlider.grid(column=0,row=row)
        row+=1

        self.length=0
        self.lengthSlider = tk.Scale(self.rightParameterFrame,from_=0,to=0.5,digits=3,resolution=0.001,tickinterval=0.1,orient=tk.HORIZONTAL,command=self.getLength,
                                        length=(self.width*(1-self.ratio)),label="Set length of stub, l (in terms of wavelengths λ)",font=("Times", 14),bg="#A9A9A9")
        self.lengthSlider.set(self.length)
        self.lengthSlider.grid(column=0,row=row)
        row+=1

        tk.Label(self.rightParameterFrame, text="", bg="#D3D3D3", font=("Times", 14)).grid(column=0,row=row) # spacer
        row+=1

        tk.Label(self.rightParameterFrame, text="Transmission line characteristic impedance, Z_0 (Ω)", bg="#D3D3D3", font=("Times", 14)).grid(column=0,row=row)
        row+=1

        self.charImpedance = tk.StringVar(value=self.defaultCharImpedance)
        self.charImpedanceInput = tk.Entry(self.rightParameterFrame, textvariable=self.charImpedance, font=("Times", 14), bg="#D3D3D3", width=10)
        self.charImpedanceInput.grid(column=0,row=row)
        row+=1
        self.charImpedanceInput.bind("<Return>",self.handleCharImpedanceInput)

        tk.Label(self.rightParameterFrame, text="Load impedance, Z_L (Ω)", bg="#D3D3D3", font=("Times", 14)).grid(column=0,row=row)
        row+=1

        self.loadImpedance = tk.StringVar(value=self.defaultLoadImpedance)
        self.loadImpedanceInput = tk.Entry(self.rightParameterFrame, textvariable=self.loadImpedance, font=("Times", 14), bg="#D3D3D3", width=10)
        self.loadImpedanceInput.grid(column=0,row=row)
        row+=1
        self.loadImpedanceInput.bind("<Return>",self.handleLoadImpedanceInput)

    def displayDiagram(self, filename):
        img = (Image.open(filename))
        img = img.resize((int(self.width*(1-self.ratio)),int(self.height/2*2/3)),Image.ANTIALIAS)
        self.master.diagram = diagram = ImageTk.PhotoImage(img)
        self.diagramCanvas.create_image(0,0,image=diagram,anchor='nw')
        self.diagramCanvas.update()
    
    def handleStubTypeSelection(self, event):
        print(f"{self.stubType.get()} selected")
        print(f"Displaying file {self.stubType2filename[self.stubType.get()]}")
        self.displayDiagram(self.stubType2filename[self.stubType.get()])
        self.master.focus()
    
    def handleStubTermSelection(self, event):
        print(f"{self.stubTermination.get()} termination selected")
        self.master.focus()
    
    def handleCharImpedanceInput(self, event):
        try:
            Z_0 = complex(self.charImpedance.get())
            self.charImpedance.set(Z_0)
            self.master.focus()
        except:
            self.charImpedance.set(self.defaultCharImpedance)
        self.updateInputImpedance()

    def handleLoadImpedanceInput(self, event):
        try: 
            Z_0 = complex(self.loadImpedance.get())
            self.loadImpedance.set(Z_0)
            self.master.focus()
        except:
            self.loadImpedance.set(self.defaultLoadImpedance)
        self.updateInputImpedance()

    def getDistance(self, event): # get currentl length of d
        self.distance = self.distanceSlider.get()
        self.updateInputImpedance()

    def getLength(self, event): # get currentl length of l
        self.length = self.lengthSlider.get()

    def updateInputImpedance(self):
        # Z_1 = Z_0 * (Z_L + j*Z_0*tan(βl)) / (Z_0 + j*Z_L*tan(βd)) where β = 2π/λ
        Z_0 = complex(self.charImpedance.get())
        Z_L = complex(self.loadImpedance.get())
        j = complex(0,1)
        d = float(self.distance)
        if self.distance == 0.25: # quarter wavelength transformer
            self.Z_1 = Z_0**2 / Z_L
        elif self.distance == 0.5: # half wavelength transformer
            self.Z_1 = Z_L
        else:
            self.Z_1 = Z_0 * (Z_L + j*Z_0*math.tan(2*math.pi * d)) / (Z_0 + j*Z_L*math.tan(2*math.pi * d))
        self.Z_1 = complex(round(self.Z_1.real,self.precision),round(self.Z_1.imag,self.precision))
        self.inputImpedanceText.set(f"Zin = {self.inputImpedance} Ω, Z1={self.Z_1} Ω")

root = tk.Tk()
a = Simulator(root)
a.mainloop()
