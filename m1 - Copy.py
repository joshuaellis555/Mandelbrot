from PIL import Image
from math import sin,pi,log,e
import random

ACCURACY=220 #maximum loops, how much of the mandelbrot set gets drawn

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
bc=[((200,200,210),1),((240,180,130),1),((230,110,20),4),((60,30,70),2),((0,0,230),7)]
COLORS=spectrum(bc)
print(COLORS)
CL=len(COLORS)
COLOR_DICT={}

def color(c):
    if not c in COLOR_DICT:
        lc=20*(c-1)**.4-20
        def shyft(a,b,r):
            return (int(a[0]*r+b[0]*(1-r)),int(a[1]*r+b[1]*(1-r)),int(a[2]*r+b[2]*(1-r)))
        if lc%1:
            COLOR_DICT[c]= shyft(COLORS[int(lc)%CL],COLORS[int(lc+1)%CL],lc%1)
        else:
            COLOR_DICT[c]= COLORS[int(lc)%CL]
    return COLOR_DICT[c]
        
def mandel_math(x,y):
    pre_i=0
    pre_r=0
    for loops in range(1,ACCURACY):
        real=pre_r**2-pre_i**2+x
        imagenary=2*pre_r*pre_i+y
        if real**2+imagenary**2>=4:
            return loops, pre_r**2+pre_i**2
        pre_r=real
        pre_i=imagenary
    return 0

def color_blend(c, remainder):
    #'''
    c1=color(c+1)
    #print(c1)
    c2=color(c)
    ratio=((remainder)/4)**2
    #print(ratio,remainder)
    c1=(c1[0]*(1-ratio)+c2[0]*ratio,c1[1]*(1-ratio)+c2[1]*ratio,c1[2]*(1-ratio)+c2[2]*ratio)
    c1=(int(c1[0]),int(c1[1]),int(c1[2]))
    #print(c1)
    return c1#'''
        

def main():
    SIZE=500#MUST BE EVEN! image will be SIZExSIZE
    Graph=[]
    #Defaults 0x, 0y, 1zoom
    center_x=-1.62806957
    center_y=00.02212084
    zoom=2**27
    #'''
    center_x=-0.11
    center_y =0.9
    zoom=2**8
    '''
    center_x=0
    center_y =0
    zoom=2**0
    #'''

    for Row in range(-int(SIZE/2),int(SIZE/2)):
        y=Row/SIZE*4/zoom-center_y
        
        print(int(Row+SIZE/2)+1," of ",SIZE)#show user how far into render we are
        for Col in range(-int(SIZE/2),int(SIZE/2)):
            x=Col/SIZE*4/zoom+center_x

            #mandel brot set ranges from -2 to 2 on x and y
            cr=mandel_math(x,y)
            #cr=Col,0
            if cr:
                c,r=cr#c is color (number of loops), r is remainder=real**2+imagenary**2)
                #print(r)
                #Graph+=[color(c)]
                Graph+=[color_blend(c,r)]
            else:
                Graph+=[(0,0,0)]

    #print(Graph)

    img = Image.new('RGB', (SIZE, SIZE))
    img.putdata(Graph)
    img.save('Tmandelbrot.png')

    print("done")

main()
