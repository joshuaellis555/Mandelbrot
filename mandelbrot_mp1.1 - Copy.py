from tkinter import *
#import Image, imageTk
from PIL import Image, ImageTk
from math import sin,pi,log,e
import random
import multiprocessing as mp

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

d=3
circle=[(x,y) for x in range(-d,d+1,1) for y in range(-d,d+1,1) if x*x+y*y<=d*d]

def color(c):
    c=min(int(c),254)
    return (c,c,c)

def mandel_math(x,y,zoom):
    real=0
    imagenary=0
    s=0
    accuracy=int(5*zoom**2+zoom*30+40)
    for loops in range(1, accuracy ):
        real, imagenary = real*real-imagenary*imagenary+x, 2*real*imagenary+y
        t=real**2+imagenary**2
        s+=t
        if t>=4:
            return loops
            #return ((1/s)**(s/loops**(1/loops)))**(1/loops)*255
    return 0

def draw_row(y,center_x,zoom,SIZE):
    Graph_row=[]
    for Col in range(-int(SIZE/2),int(SIZE/2)):
            z=2**zoom
            x=Col/SIZE*4/z+center_x

            #mandel brot set ranges from -2 to 2 on x and y
            c=mandel_math(x,y,zoom)
            if c:                
                Graph_row+=[c]
            else:
                Graph_row+=[255]
    return Graph_row

'''MULTIPROCESSING'''

def Worker(JobsQ,ReturnQ,i):
    while True:
        R,y,cx,z,s=JobsQ.get()
        #print(R,i)
        ReturnQ.put( (R,draw_row(y,cx,z,s)) )

def blend(cGraph,SIZE):
    rGraph=list(cGraph)
    for row in range(SIZE):
        for col in range(SIZE):
            t=0
            for x,y in circle:
                r,c=row+y,col+x
                print(r,c)
                if r>=0 and r<SIZE and c>=0 and c<SIZE:
                    print(cGraph[r][c])
                    t+=abs(cGraph[row][col]-cGraph[r][c])
            rGraph[row][col]=t
    return rGraph
                    
                

def draw_graph(center_y,center_x,zoom,SIZE,JobsQ,ReturnQ):
    for Row in range(-int(SIZE/2),int(SIZE/2)):
        z=2**zoom
        y=Row/SIZE*4/z-center_y
        
        JobsQ.put( (Row,y,center_x,zoom,SIZE) )

    ReturnList=[]
    for Row in range(SIZE):
        ReturnList+=[ReturnQ.get()]
    
    ReturnList.sort()
    cGraph=[]
    for row in ReturnList:
        cGraph+=[row]

    cGraph=blend(cGraph,SIZE)
    pGraph=[]
    for row in range(SIZE):
        for c in cGraph[row]:
            pGraph+=[color(c)]
    return pGraph

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
    SIZE=6#MUST/should BE EVEN! image will be SIZExSIZE
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

