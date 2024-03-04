import numpy as np
class OP:
    def __init__(self,x0,y0):
        self.x0=x0
        self.y0=y0

    def obj_f(self,x,y):
        f=(x-3)**2+(y-4)**2-(x-4)*(y-3)  #任意の目的関数を入力してください
        return f
        
    def get_norm(self,li):
        norm=np.sqrt((li[0])**2+(li[1])**2)
        return norm

    def gradient(self,x,y):
        self.fx=2*x-y-3 #目的関数のx偏導関数
        self.fy=2*y-x-4 #目的関数のy偏導関数
        gra_f=np.array([self.fx,self.fy])
        return gra_f

    def hessian(self,x,y):
        fxx=2 #fxx
        fyy=2 #fyy
        fxy=-1 #fxy=fyx
        hessian=np.zeros((2,2))
        hessian[0][0]=fxx
        hessian[0][1]=fxy
        hessian[1][0]=fxy
        hessian[1][1]=fyy
        return hessian

    def deltax(self,li,t):
        deltax=li*t
        return deltax

    
class Gradient(OP):
    def solve_t(self,x,y):
        A,B,C,D,E,F,G=0,1,-3,0,1,-4,-1 #目的関数の数値を入れてください
        a=-3*(A*self.fx**3+D*self.fy**3)
        b=2*(3*(A*self.fx**2*x+D*self.fy**2*y)+(B*self.fx**2+E*self.fy**2)+G*self.fx*self.fy)
        c=-(3*(A*self.fx*x**2+D*self.fy*y**2)+2*(B*self.fx*x+E*self.fy*y)+C*self.fx+F*self.fy+G*(self.fx*y+self.fy*x))

        Dev=b**2-4*a*c
        if Dev>0:
            #t1=(-b+Dev**0.5)/2/a
            #t2=(-b-Dev**0.5)/2/a
            #if 2*a*t1+b>0:
                #t=t1
            #else:
                #t=t2
            
            t=-c/b

        elif Dev==0:
            t=-b/2/a

        else:
            t=0.01

        

        return t

    def print_f(self,x,y,i):
        self.x=x
        self.y=y
        obj_f=self.obj_f(self.x,self.y)
        print("x"+str(i)+":"+str(self.x)+" "+"y"+str(i)+":"+str(self.y)+" "+"f"+str(i)+":"+str(obj_f))
        gra_f=self.gradient(self.x,self.y)
        self.nor_f=self.get_norm(gra_f)
        t=self.solve_t(self.x,self.y)
        #t=0.01 #一定値の場合はこちらを選択
        deltax=self.deltax(gra_f,t)
        self.nor_dx=self.get_norm(deltax)
        self.x-=deltax[0]
        self.y-=deltax[1]

    def get_f(self):
        delta=1e-2
        i=0
        self.print_f(self.x0,self.y0,i)
        i+=1

        while self.nor_f!=0 and self.nor_dx/self.nor_f>delta and i<100:
            self.print_f(self.x,self.y,i)
            i+=1

    
class CG(OP):
    def solve_m(self,gra_f,alpha,m):
        m=gra_f+alpha*m
        return m

    def hold_m(self,m):
        former_m=m
        return former_m

    def solve_alpha(self,m,hessian,gra_f):
        top=np.dot(m,np.dot(hessian,gra_f))
        bottom=np.dot(m,np.dot(hessian,m))
        alpha=-top/bottom
        return alpha

    def solve_t(self,m,hessian,gra_f):
        top=np.dot(m,gra_f)
        bottom=np.dot(m,np.dot(hessian,m))
        t=-top/bottom
        return t

    def print_f(self,x,y,i):
        self.x=x
        self.y=y
        obj_f=self.obj_f(self.x,self.y)
        print("x"+str(i)+":"+str(self.x)+" "+"y"+str(i)+":"+str(self.y)+" "+"f"+str(i)+":"+str(obj_f))
        gra_f=self.gradient(self.x,self.y)
        self.nor_f=self.get_norm(gra_f)
        hessian=self.hessian(self.x,self.y)
        if i==0:
            m=gra_f
            self.former_m=self.hold_m(m)
        else:
            alpha=self.solve_alpha(self.former_m,hessian,gra_f)
            m=self.solve_m(gra_f,alpha,self.former_m)
            self.former_m=self.hold_m(m)
        t=self.solve_t(m,hessian,gra_f)
        deltax=self.deltax(m,t)
        self.nor_dx=self.get_norm(deltax)
        self.x+=deltax[0]
        self.y+=deltax[1]

    def get_f(self):
        delta=1e-10
        i=0
        self.print_f(self.x0,self.y0,i)
        i+=1

        while self.nor_f!=0 and self.nor_dx>delta and i<100:
            self.print_f(self.x,self.y,i)
            i+=1

class Newton(OP):
    def h_inv(self,hessian):
        h_inv=np.linalg.inv(hessian)
        return h_inv

    def print_f(self,x,y,i):
        self.x=x
        self.y=y
        obj_f=self.obj_f(self.x,self.y)
        print("x"+str(i)+":"+str(self.x)+" "+"y"+str(i)+":"+str(self.y)+" "+"f"+str(i)+":"+str(obj_f))
        gra_f=self.gradient(self.x,self.y)
        self.nor_f=self.get_norm(gra_f)
        hessian=self.hessian(self.x,self.y)
        h_inv=self.h_inv(hessian)
        deltax=np.dot(h_inv,gra_f)
        self.nor_dx=self.get_norm(deltax)
        self.x-=deltax[0]
        self.y-=deltax[1]

    def get_f(self):
        delta=1e-10
        i=0
        self.print_f(self.x0,self.y0,i)
        i+=1

        while self.nor_f!=0 and self.nor_dx>delta and i<100:
            self.print_f(self.x,self.y,i)
            i+=1
    


gradient=Gradient(2,8)
gradient.get_f()

#cg=CG(-1,-3)
#cg.get_f()

#newton=Newton(100,100)
#newton.get_f()