from PIL import Image
from math import sin,pi,log,e
import random

ACCURACY=10000 #maximum loops, how much of the mandelbrot set gets drawn
COLORS={}

def color(c):
    if not c in COLORS:
        theta=pi*log(c)-1
        r,g,b=0,4,2 #offsets
        
        def colr(c,offset,rad):
            return int(255*(.5+sin(pi*theta+offset*pi/3)/2)**rad)
        def average(l):
            return int(sum(l)/len(l))
        COLORS[c]=(colr(c,r,1),colr(c,g,1.5),colr(c,b,2))
    return COLORS[c]

def mandel_math(x,y):
    pre_i=0
    pre_r=0
    for loops in range(1,ACCURACY):
        real=pre_r**2-pre_i**2+x
        imagenary=2*pre_r*pre_i+y
        if real**2+imagenary**2>=4:
            #return loops, real**2+imagenary**2-4
            return loops, pre_r**2+pre_i**2
        pre_r=real
        pre_i=imagenary
    return 0

def color_blend(c, remainder):
    '''
    ARATE=.1
    c1=color(c+1]
    #print(c1)
    c2=color(c]
    r=int(remainder*4)
    for r in range(r):
        c1=(c1[0]*(1-ARATE)+c2[0]*ARATE,c1[1]*(1-ARATE)+c2[1]*ARATE,c1[2]*(1-ARATE)+c2[2]*ARATE)
    c1=(int(c1[0]),int(c1[1]),int(c1[2]))
    #print(c1)
    return c1#'''
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
    '''
    c1=color(c+1)
    #print(c1)
    c2=color(c)
    ratio=remainder/(remainder+ACCURACY)
    #print(ratio,remainder)
    c1=(c1[0]*(1-ratio)+c2[0]*ratio,c1[1]*(1-ratio)+c2[1]*ratio,c1[2]*(1-ratio)+c2[2]*ratio)
    c1=(int(c1[0]),int(c1[1]),int(c1[2]))
    #print(c1)
    return c1#'''
        

def main():
    SIZE=10000#MUST BE EVEN! image will be SIZExSIZE
    Graph=[]
    #Defaults 0x, 0y, 1zoom
    center_x=-1.62806957
    center_y=00.02212084
    zoom=2**27
    '''
    center_x=0
    center_y=0
    zoom=1
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
    img.save('mandelbrot.png')

    print("done")

main()
