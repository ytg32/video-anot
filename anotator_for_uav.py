import sys, os          
import cv2
import numpy as np
from time import sleep

SCALE = 1.45

pathname = os.path.dirname(sys.argv[0])        
PATH = os.path.abspath(pathname) # path string

anot_path = os.path.join(PATH + "\\anots")
rgb_path = os.path.join(PATH + "\\imgs")


anot_name = os.listdir(anot_path)[0][:6]
countList = None
countIdx = 0


for root, dirs, files in os.walk(rgb_path,topdown=False):
    countList = [int(name[3:-4]) for name in files]


if len(countList) == 0:
    print("there exists no file in image path")
    exit()

count = countList[countIdx]

font = cv2.FONT_HERSHEY_SIMPLEX
Classes = {0: "Pedestrian",1: "Car", 2:"UAP", 3:"UAV"}
idx = 1

Color_Scheme = {0: (200, 50, 150), 1: (0, 255, 255), 2:(255,255,0), 3:(125,125,125)}

States = {0: "Drawing", 1: "Deleting",}
state = 0

drawing = False
ix = 0
iy = 0

cur_x = 0
cur_y = 0

def intersects(rect1,rect2):
    p1 = (rect1[0] , rect1[1]) 
    p2 = (rect1[0] + rect1[2], rect1[1] + rect1[3])

    p3 = (rect2[0] , rect2[1]) 
    p4 = (rect2[0] + rect2[2], rect2[1] + rect2[3])

    if p1[0] > p4[0] or p3[0] > p2[0]: 
        return False
    if (p1[1] > p4[1] or p3[1] > p2[1]):
        return False
    return True

def read(count):
    rgb_p = f"{rgb_path}\\img{str(count).zfill(6)}.jpg"
    anot_p = f"{anot_path}\\{anot_name}{str(count)}.txt"

    if not os.path.exists(anot_p):
        open(anot_p, 'w')
    
    img = cv2.imread(rgb_p)
    if drawing:
        img = cv2.circle(img,(int(ix/SCALE),int(iy/SCALE)), 3, (255,255,255), -1)
    
    cv2.line(img,(cur_x - 3000, cur_y),(cur_x + 3000,cur_y),(255,0,0),1)
    cv2.line(img,(cur_x, cur_y - 3000),(cur_x,cur_y + 3000),(255,0,0),1)

    with open(anot_p, 'r') as fp:
        line = fp.readline()
        while line:
            vals = line.split(' ')
            vals = list(map(float, vals[:-1])) 
            vals[0] = int(vals[0])
            #print(vals)
            p1 = (int(vals[1]), int(vals[2]))
            p2 = (int(vals[1] + vals[3]),int(vals[2]+ vals[4]))
            img = cv2.rectangle(img, p1, p2, Color_Scheme[vals[0]], 2)
            line = fp.readline()
    
    h = int(img.shape[0]* SCALE)
    w = int(img.shape[1]*SCALE)
    #print(img.shape[0],img.shape[1])
    img = cv2.resize(img, (w,h))
    
    cv2.putText(img, f'{Classes[idx]}',(10,25), font, 1,(255,255,255),2, cv2.LINE_AA)
    cv2.putText(img, f'{States[state]}',(10,50), font, 1,(255,255,255),2, cv2.LINE_AA)
    cv2.putText(img, f'{count}', (w-100,30), font, 1,(255,255,255),2, cv2.LINE_AA)
    
    return img

def delete(count, rect1):
    anot_p = f"{anot_path}\\{anot_name}{str(count)}.txt"
    temp_p = f"{anot_path}\\temp.txt"
    if not os.path.exists(anot_p):
        raise Exception(f"file {str(count).zfill(4)}.txt in anottation folder doesn't exist.")
    tempfp = open(temp_p, 'w')

    with open(anot_p, 'r') as fp:
        line = fp.readline()
        while line:
            vals = line.split(' ')
            vals = tuple(map(float, vals[1:-1]))
            if not intersects(rect1, vals):
                tempfp.write(line)            
            line = fp.readline()
    tempfp.close()

    with open(temp_p, 'r') as f:
        lines = f.readlines()
        with open(anot_p, 'w') as f1:
            f1.writelines(lines)
    
    os.remove(temp_p)
    
img = read(count)

def draw(event, x, y, flags, params):
    anot_p = f"{anot_path}\\{anot_name}{str(count)}.txt"
    global ix,iy,drawing, img, cur_x, cur_y
    cur_x = int(x / SCALE)
    cur_y = int(y / SCALE)
    if event == cv2.EVENT_RBUTTONDOWN:
        if States[state] == "Drawing":
            if drawing == True:
                xx, yy = int(min(ix, x)/SCALE), int(min(iy, y)/SCALE)
                ww, hh = int(abs(ix - x)/SCALE), int(abs(iy - y)/SCALE)
                with open(anot_p, "a") as outfile:     
                    outfile.write(f'{idx} {xx} {yy} {ww} {hh} \n')
                drawing = False
                img = read(count)
            else:    
                drawing = True
                ix = x
                iy = y
                img = cv2.circle(img,(int(ix/SCALE),int(iy/SCALE)), 5, (255,255,255), -1)
        if States[state] == "Deleting":
            if drawing == True:
                xx, yy = int(min(ix, x)/SCALE), int(min(iy, y)/SCALE)
                ww, hh = int(abs(ix - x)/SCALE), int(abs(iy - y)/SCALE)
                rect1 = (xx, yy, ww, hh)
                delete(count, rect1)
                drawing = False
                img = read(count)
            else:
                drawing = True
                ix = x
                iy = y
                img = cv2.circle(img,(int(ix/SCALE),int(iy/SCALE)), 5, (255,255,255), -1)
    elif event== cv2.EVENT_LBUTTONDOWN:
        drawing = False
        img = read(count)

cv2.namedWindow('Window')
#cv2.setWindowProperty("Window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback("Window",draw)

while(True):
    img = read(count)
    cv2.imshow("Window",img)
    k = cv2.waitKey(3)
    if k == 27:
        break
    elif k == 120:
        if countIdx + 1 < len(countList):
            countIdx += 1
            count = countList[countIdx]
            #img = read(count)  
    elif k == 122:
        if countIdx > 0 :
            countIdx -= 1
            count = countList[countIdx]
            #img = read(count)
    elif k == 115:
        idx += 1
        idx = idx % len(Classes)
        #img= read(count)
    elif k == 100:
        state += 1
        state = state % len(States)
        drawing = False
        #img = read(count)
    elif k == 252:
        if countIdx + 100 < len(countList):
            countIdx += 100
            count = countList[countIdx]
            #img = read(count)
    elif k == 240:
        if countIdx >= 100:
            countIdx -= 100
            count = countList[countIdx]
            #img = read(count)
    elif k == 105:
        if countIdx + 10 < len(countList):
            countIdx += 10
            count = countList[countIdx]
            #img = read(count)
    elif k == 254:
        if countIdx >= 10:
            countIdx -= 10
            count = countList[countIdx]
            #img = read(count)
    elif k==-1:  # normally -1 returned,so don't print it
        continue