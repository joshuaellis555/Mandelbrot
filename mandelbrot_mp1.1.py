from tkinter import *
#import Image, imageTk
from PIL import Image, ImageTk
from math import sin,pi,log,e
import random
import multiprocessing as mp

#spectrum blends one color into another over n steps where n is their combines steps
#giving a color a larger number of steps causes the graph to have more of that color
#base colors [((color1),setps1),((color2),steps2),...]
bc=[((200,200,210),1),((240,180,130),1),((250,130,30),4),((50,20,30),2),((0,0,230),7)]
def spectrum(l):
    lst=[l[-1][0]]
    def shyft(a,b,r):
        return (int(a[0]*(1-r)+b[0]*r),int(a[1]*(1-r)+b[1]*r),int(a[2]*(1-r)+b[2]*r))
    
    for j in range(len(l)):
        r=l[j-1][1]
        for k in range(1,r+1):
            lst+=[shyft(l[j-1][0],shyft(l[j-1][0],l[j][0],0.5),k/(r))]
        r=l[j][1]
        for k in range(1,r+1):
            lst+=[shyft(shyft(l[j-1][0],l[j][0],0.5),l[j][0],k/(r))]
    return lst
COLORS=spectrum(bc)

CL=len(COLORS)
COLOR_DICT={}
def color(c):
    if not c in COLOR_DICT:
        lc=35*(c-1)**.3-35
        def shyft(a,b,r):
            return (int(a[0]*r+b[0]*(1-r)),int(a[1]*r+b[1]*(1-r)),int(a[2]*r+b[2]*(1-r)))
        if lc%1:
            COLOR_DICT[c]= shyft(COLORS[int(lc)%CL],COLORS[int(lc+1)%CL],lc%1)
        else:
            COLOR_DICT[c]= COLORS[int(lc)%CL]
    return COLOR_DICT[c]

def color_blend(c, remainder):
    c1=color(c+1)
    c2=color(c)
    ratio=((remainder)/4)**2
    c1=(c1[0]*(1-ratio)+c2[0]*ratio,c1[1]*(1-ratio)+c2[1]*ratio,c1[2]*(1-ratio)+c2[2]*ratio)
    c1=(int(c1[0]),int(c1[1]),int(c1[2]))
    return c1

'''TKINTER'''

class LoadImage:
    def __init__(self,root,graph_img,center_x,center_y,zoom,SIZE,JobsQ,ReturnQ):
        self.root=root
        frame = Frame(root)
        self.canvas = Canvas(frame,width=900,height=900)
        self.canvas.pack()
        frame.pack()
        #File = "Tmandelbrot.png"
        #self.orig_img = Image.open(File)
        #self.img = ImageTk.PhotoImage(self.orig_img)
        self.orig_img = graph_img
        self.img = ImageTk.PhotoImage(graph_img)
        self.canvas.create_image(0,0,image=self.img, anchor="nw")

        self.center_x=center_x
        self.center_y=center_y
        self.zoom=zoom
        self.SIZE=SIZE

        self.JobsQ=JobsQ
        self.ReturnQ=ReturnQ

        self.zoomcycle = None
        self.zimg_id = None

        root.bind("<Button-1>",self.zoomin)
        root.bind("<MouseWheel>",self.scrollzoom)
        root.bind("<Button-2>",self.superdraw)
        root.bind("<Button-3>",self.zoomout)
        self.canvas.bind("<Motion>",self.mouse_move)

    def scrollzoom(self,event):
        if self.zoomcycle!=None:
            if event.delta>0:
                self.zoomcycle+=1
            elif event.delta<0:
                self.zoomcycle-=1
            x,y = event.x, event.y
            ofst=self.SIZE/2/2**self.zoomcycle
            tmp = self.orig_img.crop((x-ofst,y-ofst,x+ofst,y+ofst))
            size = 400,400
            self.zimg = ImageTk.PhotoImage(tmp.resize(size))
            self.zimg_id = self.canvas.create_image(event.x,event.y,image=self.zimg)
                
    def superdraw(self,event):
        size=8000
        Graph=draw_graph(self.center_y,self.center_x,self.zoom,size,self.JobsQ,self.ReturnQ)
                
        img = Image.new('RGB', (size, size))
        img.putdata(Graph)
        img.save('SuperMandelbrot.png')
        print("Done")
        
    def zoomin(self,event):
        #print(self.canvas.winfo_height())
        if self.zimg_id: self.canvas.delete(self.zimg_id)
        if self.zoomcycle==None:
            self.zoomcycle=0
            if event:
                x,y = event.x, event.y
                self.root.title(str((x,y)))
                ofst=self.SIZE/2/2**self.zoomcycle
                tmp = self.orig_img.crop((x-ofst,y-ofst,x+ofst,y+ofst))
                size = 400,400
                self.zimg = ImageTk.PhotoImage(tmp.resize(size))
                self.zimg_id = self.canvas.create_image(event.x,event.y,image=self.zimg)
        else:
            x,y = event.x, event.y
            if x<=self.SIZE and y<=self.SIZE:
                
                x,y=int(x-self.SIZE/2),-int(y-self.SIZE/2)
                print(x,y)
                
                self.center_x += x/self.SIZE*4/(2**self.zoom)
                self.center_y += y/self.SIZE*4/(2**self.zoom)
                
                self.zoom+=self.zoomcycle
                
                Graph=draw_graph(self.center_y,self.center_x,self.zoom,self.SIZE,self.JobsQ,self.ReturnQ)
                
                img = Image.new('RGB', (self.SIZE, self.SIZE))
                img.putdata(Graph)
                
                self.orig_img=img
                self.img = ImageTk.PhotoImage(img)
                self.canvas.create_image(0,0,image=self.img, anchor="nw")
                self.zoomcycle=None
                
            
            
    def zoomout(self,event):
        self.zoomcycle=None
        if self.zimg_id: self.canvas.delete(self.zimg_id)

    def mouse_move(self,event):
        if self.zimg_id: self.canvas.delete(self.zimg_id)
        x,y = event.x, event.y
        self.root.title(str((x,y)))
        if self.zoomcycle!=None:
            ofst=self.SIZE/2/2**self.zoomcycle
            tmp = self.orig_img.crop((x-ofst,y-ofst,x+ofst,y+ofst))
            size = 400,400
            self.zimg = ImageTk.PhotoImage(tmp.resize(size))
            self.zimg_id = self.canvas.create_image(event.x,event.y,image=self.zimg)
        
'''BASIC MANDELBROT FUNCTIONS'''

def mandel_math(x,y,zoom):
    pre_i=0
    pre_r=0
    for loops in range(1, int(5*zoom**2+zoom*30+40) ):
        real=pre_r**2-pre_i**2+x
        imagenary=2*pre_r*pre_i+y
        if real**2+imagenary**2>=4:
            return loops, pre_r**2+pre_i**2
        pre_r=real
        pre_i=imagenary
    return 0

def draw_row(y,center_x,zoom,SIZE):
    Graph_row=[]
    for Col in range(-int(SIZE/2),int(SIZE/2)):
            z=2**zoom
            x=Col/SIZE*4/z+center_x

            #mandel brot set ranges from -2 to 2 on x and y
            cr=mandel_math(x,y,zoom)
            if cr:
                c,r=cr#c is color (number of loops), r is remainder=real**2+imagenary**2)
                
                Graph_row+=[color_blend(c,r)]
            else:
                Graph_row+=[(0,0,0)]
    return Graph_row

'''MULTIPROCESSING'''

def Worker(JobsQ,ReturnQ,i):
    while True:
        R,y,cx,z,s=JobsQ.get()
        #print(R,i)
        ReturnQ.put( (R,draw_row(y,cx,z,s)) )

def draw_graph(center_y,center_x,zoom,SIZE,JobsQ,ReturnQ):
    for Row in range(-int(SIZE/2),int(SIZE/2)):
        z=2**zoom
        y=Row/SIZE*4/z-center_y
        
        JobsQ.put( (Row,y,center_x,zoom,SIZE) )

    ReturnList=[]
    for Row in range(SIZE):
        ReturnList+=[ReturnQ.get()]
    
    ReturnList.sort()
    rl=[]
    for r in [x[1] for x in ReturnList]:
        rl+=r
    return rl

'''MAIN'''

def main():

    #create Queues and start workers
    JobsQ = mp.Queue()
    ReturnQ = mp.Queue()
    
    CORES = mp.cpu_count()
    
    p={}
    for i in range(CORES):
        p[i] = mp.Process(target = Worker, args=[JobsQ,ReturnQ,i])
        p[i].start()

    #Draw the initial graph
    SIZE=600#MUST/should BE EVEN! image will be SIZExSIZE
    Graph=[]
    #Defaults 0x, 0y, 1zoom
    center_x=0
    center_y=0
    zoom=0

    Graph=draw_graph(center_y,center_x,zoom,SIZE,JobsQ,ReturnQ)
    
    img = Image.new('RGB', (SIZE, SIZE))
    img.putdata(Graph)

    #Start Tkinter
    root = Tk()
    root.title("Crop Test")
    App = LoadImage(root,img,center_x,center_y,zoom,SIZE,JobsQ,ReturnQ)
    root.mainloop()

if __name__ == '__main__':
    main()

