import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import cmath
import math
import turtle
import smith_chart

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

        self.leftCanvas = tk.Canvas(self.leftFrame, width=width*self.ratio, height=self.height, bg="white")
        self.leftCanvas.grid(column=0,row=0)
        self.screen = turtle.TurtleScreen(self.leftCanvas)
        self.smith = smith_chart.SmithChart(self.screen)
        self.simulator_turtle = turtle.RawTurtle(self.screen)
        self.simulator_turtle.hideturtle()
        self.simulator_turtle.speed(0)

        self.rightFrame = tk.Frame(master=self.rootFrame, width=width*(1-self.ratio), height=self.height, bg="white")
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
        self.stubType = tk.StringVar(value="series stub") # default to series stub
        self.stubTypeChosen = ttk.Combobox(self.rightSelectFrame, width=20, textvariable=self.stubType)
        self.stubTypeChosen['values'] = ('series stub','shunt stub')
        self.stubTypeChosen.grid(column=1,row=row)
        row+=1
        self.stubTypeChosen.current()
        self.stubTypeChosen['state'] = 'readonly'
        self.stubTypeChosen.bind('<<ComboboxSelected>>',self.handleStubTypeSelection)

        tk.Label(self.rightSelectFrame, text="Select stub termination:", bg="#A9A9A9", font=("Times", 16)).grid(column=0,row=row)
        self.stubTermination = tk.StringVar(value="short") # default to short
        self.stubTerminationChosen = ttk.Combobox(self.rightSelectFrame, width=20, textvariable=self.stubTermination)
        self.stubTerminationChosen['values'] = ('open','short')
        self.stubTerminationChosen.grid(column=1,row=row)
        self.stubTerminationChosen.current()
        self.stubTerminationChosen['state'] = 'readonly'
        self.stubTerminationChosen.bind('<<ComboboxSelected>>',self.handleStubTermSelection)

        self.diagramCanvas = tk.Canvas(self.rightDiagramFrame,bg="white",width=(self.width*(1-self.ratio)),height=(self.height/2*2/3))
        self.diagramCanvas.grid(column=0,row=0)
        self.displayDiagram("series_stub.png") # default to series stub

        row=0
        self.Z_1 = complex(self.defaultLoadImpedance)
        self.Z_stub = cmath.inf if self.stubTermination.get()=="open" else 0
        self.inputImpedance = self.Z_1
        self.inputImpedanceText = tk.StringVar(value=f"Zin = {self.inputImpedance} Ω, Z1 = {self.Z_1} Ω, Zstub = {self.Z_stub} Ω")
        self.inputImpedanceEntry = tk.Entry(self.rightParameterFrame, textvariable=self.inputImpedanceText, state="readonly", font=("Times", 14), width=55).grid(column=0,row=row)
        row+=1
        self.Gamma = None # reflection coefficient Γ = (Z_in - Z_0) / (Z_in + Z_0)
        self.VSWR = None # voltage standing wave ratio S = (1 + |Γ|) / (1 - |Γ|)
        self.reflectionText = tk.StringVar(value=f"Γ = {self.Gamma}, VSWR = {self.VSWR}")
        self.reflectionEntry = tk.Entry(self.rightParameterFrame, textvariable=self.reflectionText, state="readonly", font=("Times", 14), width=55).grid(column=0,row=row)
        row+=1
        tk.Label(self.rightParameterFrame, text="", bg="#D3D3D3", font=("Times", 14)).grid(column=0,row=row) # spacer
        row+=1
        # tk.Label(self.rightParameterFrame, text="Parameters", bg="#D3D3D3", font=("Times", 20)).grid(column=0,row=row)
        # row+=1

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

        self.updateInputImpedance()

    def displayDiagram(self, filename):
        img = (Image.open(filename))
        img = img.resize((int(self.width*(1-self.ratio)),int(self.height/2*2/3)),Image.ANTIALIAS)
        self.master.diagram = diagram = ImageTk.PhotoImage(img)
        self.diagramCanvas.create_image(0,0,image=diagram,anchor='nw')
        self.diagramCanvas.update()

    def handleStubTypeSelection(self, event):
        # print(f"{self.stubType.get()} selected")
        # print(f"Displaying file {self.stubType2filename[self.stubType.get()]}")
        self.displayDiagram(self.stubType2filename[self.stubType.get()])
        if(self.stubType.get() == 'series stub'): # set series stub default to short termination
            self.stubTermination.set('short')
        else: # set shunt stub default to open termination
            self.stubTermination.set('open')
        self.master.focus()
        self.updateInputImpedance()

    def handleStubTermSelection(self, event):
        # print(f"{self.stubTermination.get()} termination selected")
        self.master.focus()
        self.updateInputImpedance()

    def handleCharImpedanceInput(self, event):
        try:
            Z_0 = complex(self.charImpedance.get())
            if(Z_0.real > 0):
                self.charImpedance.set(Z_0)
            else:
                self.charImpedance.set(self.defaultCharImpedance)
        except:
            self.charImpedance.set(self.defaultCharImpedance)
        self.updateInputImpedance()
        self.master.focus()

    def handleLoadImpedanceInput(self, event):
        try:
            Z_L = complex(self.loadImpedance.get())
            if(Z_L.real >= 0):
                self.loadImpedance.set(Z_L)
            else:
                self.loadImpedance.set(self.defaultLoadImpedance)
        except:
            if(self.loadImpedance.get()=="inf"):
                Z_L = complex(cmath.inf)
                self.loadImpedance.set(Z_L)
            else:
                self.loadImpedance.set(self.defaultLoadImpedance)
        self.updateInputImpedance()
        self.master.focus()

    def getDistance(self, event): # get currentl length of d
        self.distance = self.distanceSlider.get()
        self.updateInputImpedance()

    def getLength(self, event): # get currentl length of l
        self.length = self.lengthSlider.get()
        self.updateInputImpedance()

    def updateInputImpedance(self):
        try:
            Z_0 = complex(self.charImpedance.get())
            if(Z_0.real > 0):
                self.charImpedance.set(Z_0)
            else:
                self.charImpedance.set(self.defaultCharImpedance)
        except:
            self.charImpedance.set(self.defaultCharImpedance)
        try:
            Z_L = complex(self.loadImpedance.get())
            if(Z_L.real >= 0):
                self.loadImpedance.set(Z_L)
            else:
                self.loadImpedance.set(self.defaultLoadImpedance)
        except:
            if(self.loadImpedance.get()=="inf"):
                Z_L = complex(cmath.inf)
                self.loadImpedance.set(Z_L)
            else:
                self.loadImpedance.set(self.defaultLoadImpedance)
        # For Z_1
        # Z_1 = Z_0 * (Z_L + j*Z_0*tan(βd)) / (Z_0 + j*Z_L*tan(βd)) where β = 2π/λ
        Z_0 = complex(self.charImpedance.get())
        Z_L = complex(self.loadImpedance.get())
        j = complex(0,1)
        d = float(self.distance)
        if Z_L != 0 and Z_L != cmath.inf:
            if self.distance == 0.25: # quarter wavelength transformer
                self.Z_1 = Z_0**2 / Z_L
            elif self.distance == 0.5: # half wavelength transformer
                self.Z_1 = Z_L
            else:
                self.Z_1 = Z_0 * (Z_L + j*Z_0*math.tan(2*math.pi * d)) / (Z_0 + j*Z_L*math.tan(2*math.pi * d))
        elif Z_L == cmath.inf:
            # Z_1 = -j*Z_0*cot(βd)
            if self.length == 0.25:
                self.Z_1 = 0
            elif self.length == 0 or self.length == 0.5:
                self.Z_1 = cmath.inf
            else:
                self.Z_1 = -j*Z_0/math.tan(2*math.pi * d)
        else: # Z_L == 0
            # Z_1 = j*Z_0*tan(βd)
            if self.length == 0.25:
                self.Z_1 = cmath.inf
            elif self.length == 0 or self.length == 0.5:
                self.Z_1 = 0
            else:
                self.Z_1 = j*Z_0*math.tan(2*math.pi * d)

        # For Z_stub
        l = float(self.length)
        if self.stubTermination.get() == 'open':
            # Z_stub = -j*Z_0*cot(βl)
            if self.length == 0.25:
                self.Z_stub = 0
            elif self.length == 0 or self.length == 0.5:
                self.Z_stub = cmath.inf
            else:
                self.Z_stub = -j*Z_0/math.tan(2*math.pi * l)
        elif self.stubTermination.get() == 'short':
            # Z_stub = j*Z_0*tan(βl)
            if self.length == 0.25:
                self.Z_stub = cmath.inf
            elif self.length == 0 or self.length == 0.5:
                self.Z_stub = 0
            else:
                self.Z_stub = j*Z_0*math.tan(2*math.pi * l)
        else:
            assert False, "WTF"

        self.Z_1 = complex(round(self.Z_1.real,self.precision),round(self.Z_1.imag,self.precision))
        self.Z_stub = complex(round(self.Z_stub.real,self.precision),round(self.Z_stub.imag,self.precision))
        if self.stubType.get() == 'series stub':
            self.inputImpedance = self.Z_1 + self.Z_stub
            self.inputImpedance = complex(round(self.inputImpedance.real,self.precision),round(self.inputImpedance.imag,self.precision))
            self.inputImpedanceText.set(f"Zin = {self.inputImpedance} Ω, Z1 = {self.Z_1} Ω, Zstub = {self.Z_stub} Ω")
        elif self.stubType.get() == 'shunt stub':
            # show admittance instead
            Y_1 = 1/self.Z_1 if self.Z_1 != 0 else cmath.inf
            Y_stub = 1/self.Z_stub if self.Z_stub != 0 else cmath.inf
            Yin = Y_1 + Y_stub
            Y_1 = complex(round(Y_1.real,self.precision),round(Y_1.imag,self.precision))
            Y_stub = complex(round(Y_stub.real,self.precision),round(Y_stub.imag,self.precision))
            Yin = complex(round(Yin.real,self.precision),round(Yin.imag,self.precision))
            self.inputImpedanceText.set(f"Yin = {Yin} S, Y1 = {Y_1} S, Ystub = {Y_stub} S")
            self.inputImpedance = 1 / Yin if Yin != 0 else cmath.inf
            self.inputImpedance = complex(round(self.inputImpedance.real,self.precision),round(self.inputImpedance.imag,self.precision))
        else:
            assert False, "WTF"

        Z_in = self.inputImpedance
        self.Gamma = (Z_in - Z_0) / (Z_in + Z_0)
        Gamma_polar = cmath.polar(self.Gamma)
        Gamma_polar = (Gamma_polar[0], Gamma_polar[1] + 2*math.pi if Gamma_polar[1] < 0 else Gamma_polar[1])
        self.VSWR = (1 + abs(self.Gamma)) / (1 - abs(self.Gamma)) if abs(self.Gamma) != 1 else cmath.inf
        Gamma_polar = (round(Gamma_polar[0],self.precision),round(Gamma_polar[1]*180/math.pi,self.precision))
        self.VSWR = round(self.VSWR, self.precision)
        self.reflectionText.set(f"Γ = {Gamma_polar[0]}exp({Gamma_polar[1]}), VSWR = {self.VSWR}")

        # plot the point on the Smith chart
        self.simulator_turtle.clear()
        self.smith.plotNormalizedImpedance(Z_0=Z_0, Z_in=Z_in, admittance=(self.stubType.get()=='shunt stub'), new_turtle=self.simulator_turtle)

if __name__ == "__main__":
    root = tk.Tk()
    a = Simulator(root)
    a.mainloop()
