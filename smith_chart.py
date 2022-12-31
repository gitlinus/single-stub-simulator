import turtle
import cmath
import math

class SmithChart:
    def __init__(self, screen: turtle.TurtleScreen = None, width=500, font=12):
        if not screen:
            self.width=width
            self.scaling=width//2
            self.font=font
            self.screen=turtle.Screen()
            self.screen.bgcolor("black")
            self.screen.title("Smith Chart")
            self.screen.screensize(canvwidth=width,canvheight=width)
            self.screen.setworldcoordinates(llx=-1*self.scaling, lly=-1*self.scaling, urx=1*self.scaling, ury=1*self.scaling)
            self.smith_turtle=turtle.Turtle()
            self.smith_turtle.hideturtle()
            self.smith_turtle.speed(0)
        else:
            self.screen_dims = screen.screensize()
            self.width = min(self.screen_dims[0], self.screen_dims[1])
            self.scaling = self.width//2
            self.font = font
            self.screen = screen
            self.screen.bgcolor("black")
            self.smith_turtle = turtle.RawTurtle(self.screen)
            self.smith_turtle.hideturtle()
            self.smith_turtle.speed(0)
    
    def drawCircle(self, x, y, r, theta=360, colour="white"): # draw a circle centered at (x,y) with radius r
        self.smith_turtle.pencolor(colour)
        self.smith_turtle.penup()
        self.smith_turtle.home()
        self.smith_turtle.setpos(x=x*self.scaling,y=(y-r)*self.scaling)
        self.smith_turtle.pendown()
        self.smith_turtle.circle(r*self.scaling, extent=theta)
    
    def drawLine(self, x1, y1, x2, y2, colour="white"): # draw line from (x1, y1) to (x2, y2)
        self.smith_turtle.pencolor(colour)
        self.smith_turtle.penup()
        self.smith_turtle.home()
        self.smith_turtle.setpos(x=x1*self.scaling,y=y1*self.scaling)
        self.smith_turtle.pendown()
        self.smith_turtle.setpos(x=x2*self.scaling,y=y2*self.scaling)
    
    def plotSmithChartPoint(self, z, label=True, precision=3): # plot the point z = r + jx on the Smith chart
        # find the intersection of resistance circle at z.real and reactance circle at z.imag
        # the intersection lies on line y=mx+b
        r_L=z.real
        x_L=z.imag
        m=x_L*(r_L/(1+r_L)-1)
        b=(x_L/2)*(1+(1-r_L)/(1+r_L))
        a_0=1+m**2
        a_1=2*m*b-2*(r_L/(1+r_L))
        a_2=b**2-(1/(1+r_L))**2+(r_L/(1+r_L))**2
        x_2=(-a_1-math.sqrt(a_1**2-4*a_0*a_2))/(2*a_0) # x_1, y_1 is trivial solution (1,0)
        y_2=m*x_2+b
        self.smith_turtle.penup()
        self.smith_turtle.home()
        self.smith_turtle.setpos(x=x_2*self.scaling,y=y_2*self.scaling)
        self.smith_turtle.pencolor("yellow")
        if label:
            z_label = complex(round(z.real,precision), round(z.imag,precision))
            self.smith_turtle.write(z_label, align='right', font=('Arial', str(self.font), 'normal'))
        self.smith_turtle.dot()
    
    def plotNormalizedImpedance(self, Z_0, Z_in: complex, VSWR=True, admittance=False):
        Gamma_L = (Z_in-Z_0) / (Z_in+Z_0) # reflection coefficient
        if VSWR: # plot the voltage standing wave ratio (VSWR) circle
            self.drawCircle(x=0,y=0,r=abs(Gamma_L))
            self.smith_turtle.penup()
            self.smith_turtle.home()
            self.smith_turtle.setpos(x=0,y=abs(Gamma_L)*self.scaling)
            self.smith_turtle.write("VSWR", align='right', font=('Arial', str(self.font), 'normal'))
        z = complex(Z_in/Z_0) # normalized impedance
        self.plotSmithChartPoint(z)
        if admittance:
            y = 1 / z
            self.plotSmithChartPoint(y)

    def drawResistanceCircles(self, r_L_list=[0, 0.5, 1, 2, 3], label=True):
        # ( Gamma_r - r_L/(1+r_L) ) ^ 2 + Gamma_i ^ 2 = ( 1/(1+r_L) ) ^ 2
        for r_L in r_L_list:
            self.drawCircle(x=r_L/(1+r_L), y=0, r=1/(1+r_L), colour="red")
        if label:
            for r_L in r_L_list:
                self.smith_turtle.penup()
                self.smith_turtle.home()
                self.smith_turtle.setpos(x=(r_L-1)/(1+r_L)*self.scaling,y=0)
                self.smith_turtle.pencolor("white")
                self.smith_turtle.write(r_L, align='right', font=('Arial', str(self.font), 'normal'))

    def drawReactanceCircles(self, x_L_list=[-2, -1, -0.5, 0.5, 1, 2], label=True):
        # ( Gamma_r - 1 ) ^ 2 + ( Gamma_i - 1/x_L ) ^ 2 = ( 1/x_L ) ^ 2
        for x_L in x_L_list:
            # calculate the angle we need to draw
            y_0 = 1/x_L
            x_2 = (1/y_0**2 - 1) / (1/y_0**2 + 1)
            y_2 = 1/y_0 * (-x_2 + 1)
            a_x = x_2 - 1
            a_y = y_2 - y_0
            b_x = 0
            b_y = -y_0
            theta = math.acos( (a_x*b_x + a_y*b_y) / (math.sqrt(a_x**2 + a_y**2) * math.sqrt(b_x**2 + b_y**2)) ) * 180 / math.pi
            self.drawCircle(x=1, y=1/x_L, r=1/x_L, theta=-theta, colour="blue")
        if label:
            for x_L in x_L_list:
                y_0 = 1/x_L
                x_2 = (1/y_0**2 - 1) / (1/y_0**2 + 1)
                y_2 = 1/y_0 * (-x_2 + 1)
                self.smith_turtle.penup()
                self.smith_turtle.home()
                self.smith_turtle.setpos(x=x_2*self.scaling,y=y_2*self.scaling)
                self.smith_turtle.pencolor("white")
                self.smith_turtle.write(x_L, align='right', font=('Arial', str(self.font), 'normal'))
    
    def drawResistanceAxis(self):
        self.drawLine(-1,0,1,0,"green")
    
    def drawReactanceAxis(self):
        self.drawLine(0,-1,0,1,"green")

    def drawChart(self):
        self.screen.tracer(0)
        self.drawResistanceAxis()
        self.drawReactanceAxis()
        self.drawResistanceCircles()
        self.drawReactanceCircles()
        self.screen.update()
    
    def execMainLoop(self):
        self.screen.mainloop()

if __name__ == "__main__":
    a=SmithChart()
    a.drawChart()
    a.plotNormalizedImpedance(50,complex(75,-50),VSWR=True,admittance=True) # example
    a.execMainLoop()
