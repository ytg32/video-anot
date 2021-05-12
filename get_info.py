import os, sys

pathname = os.path.dirname(sys.argv[0])        
PATH = os.path.abspath(pathname)

anot_path = os.path.join(PATH , "anots")

Classes = {0: "Pedestrian",1: "Car",2:"UAP", 3:"UAI"}

values = {0: 0, 1: 0, 2: 0, 3: 0}

percentage = {0: 0, 1: 0, 2: 0, 3: 0}
def get_info(anot_path):
    x = 0
    for fi in os.listdir(anot_path):
        x += 1
        #print(x)
        with open(os.path.join(anot_path, fi), 'r') as fp:
            line = fp.readline()
            while line:
                val = line.partition(" ")[0]
                v = int(val)
                values[v] += 1
                line = fp.readline()
    sum=values[0]+values[1]+values[2]+values[3]
    percentage[0]=int(100*(values[0]/sum))
    percentage[1]=int(100*(values[1]/sum))
    percentage[2]=int(100*(values[2]/sum))
    percentage[3]=int(100*(values[3]/sum))
    
    for x in values:
        print(f"{Classes[x]}: {values[x]}: %{percentage[x]} ")

get_info(anot_path)