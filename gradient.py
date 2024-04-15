import numpy as np

class Gradient:
    def __init__(self,x0,y0):
        self.x0=x0
        self.y0=y0

    def gradient(self,x,y):
        gra_f=[]
        gra_f.append(20*x-10*y-12)
        gra_f.append(-10*x+50*y)
        return gra_f

    def get_norm(self,li):
        norm=np.sqrt((li[0])**2+(li[1])**2)
        return norm

    def solve_t(self,xn,yn):
        t=((70*xn-260*yn-12)*(xn-5*yn)+3*(20*xn-10*yn-12)*(3*xn-2))/((70*xn-260*yn-12)**2+9*((20*xn-10*yn-12)**2))
        return t

    def print_f(self,x,y,i):
        self.x=x
        self.y=y
        f=(5*self.y-self.x)**2+(2-3*self.x)**2
        print("x"+str(i)+":"+str(self.x)+" "+"y"+str(i)+":"+str(self.y)+" "+"f"+str(i)+":"+str(f))
        gra_f=self.gradient(self.x,self.y)
        self.nor_f=self.get_norm(gra_f)
        t_f=self.solve_t(self.x,self.y)
        deltax=[n*t_f for n in gra_f]
        self.nor_dx=self.get_norm(deltax)
        self.x=self.x-deltax[0]
        self.y=self.y-deltax[1]
        

    def get_f(self):
        delta=0.00001
        i=0
        self.print_f(self.x0,self.y0,i)
        i+=1

        while self.nor_f!=0 and self.nor_dx>delta and i<100:
            self.print_f(self.x,self.y,i)
            i+=1



class Newton:
    def __init__(self,x0):
        self.x0=x0

    def obj_f(self,x):
        f=2*x**4+3*x**3-10*x**2-7*x+1
        return f

    def deltax(self,x):
        self.df=8*x**3+9*x**2-20*x-7
        ddf=24*x**2+18*x-20
        deltax=self.df/ddf
        return deltax

    def print_f(self,x,i):
        self.x=x
        obj_f=self.obj_f(self.x)
        print("x"+str(i)+":"+str(self.x)+" "+"f"+str(i)+":"+str(obj_f))
        self.nor_dx=abs(self.deltax(self.x))
        self.x=self.x-self.deltax(self.x)

    def get_f(self):
        delta=0.00001
        i=0
        self.print_f(self.x0,i)
        i+=1

        while self.df!=0 and self.nor_dx>delta and i<100:
            self.print_f(self.x,i)
            i+=1


newton=Newton(-5)
newton.get_f()        
        
#gradient=Gradient(0,0)
#gradient=Gradient(1,0)
#gradient.get_f()