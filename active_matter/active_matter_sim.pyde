import time
t = 0
birds = []
T = 0
corrlength = 0
numbirds = 100

def randomVec(x,y):
    return PVector(random(x),random(y))

def energy(a,b):
    return cos(a.dir - b.dir)
    
def partition_function():
    sum = 0
    for a in birds:
        for b in birds:
            sum = exp(- energy(a,b)/T)
    return sum

class Plot:
    def __init__(self, arr):
        self.arr
    # def add():
        
    # def plot():
    #     i = 0
    #     for a in self.arr: 
    #         line(
    #         i += 1
#def plotOrderParameters(y):
    

def drawDistribution():
    bins = []
    numbins = 30
    binsize = TWO_PI / numbins
    for b in range(numbins):
        bins.append(0)
    for a in birds:
        #print(floor((a.dir.heading() % TWO_PI)/ TWO_PI * numbins))
        bins[floor((a.dir.heading() % TWO_PI) / TWO_PI * numbins)] += 1
    
    i = 0
    for b in bins:
        y = 2 * b
        rect(i * width/ numbins, 500 - y, width/numbins, y)
        i += 1
    
def avgDir(arr):
    sum = PVector(0,0)
    for a in arr: 
        sum.add(a.vel)
        
    return sum

class Bird:
    def __init__(self, pos, angle, vel):
        self.pos = pos
        self.dir = PVector(1,0)
        self.dir.rotate(angle)
        self.vel = PVector(self.dir.x * vel, self.dir.y * vel)
        
    def timestep(self):
        t = time.time()/10 - 1732602054
        diff = PVector.sub(self.dir, self.vel)
        #noisevec = PVector(noise(t + self.pos.y) - 0.5, noise(t + 1000 + self.pos.x) - 0.5)
        #noisevec = PVector(random(-1,1), random(-1,1))
        noisevec = PVector(1,0)
        noisevec.rotate(random(-PI,PI))
        noisevec.setMag(T)
        diff.setMag(1. - T)
        diff.add(noisevec)
        diff.setMag(0.1)
        
        self.vel.add(diff)
        self.vel.normalize()
        self.pos = self.pos.add(self.vel)
        self.pos.x = self.pos.x % width
        self.pos.y = self.pos.y % width
        
    def align(self, neighboravgdir):
        self.dir = neighboravgdir
        self.dir.normalize()
    
    def drawbird(self):
        fill(255)
        stroke(0)
        x = self.pos.x
        y = self.pos.y
        dir = self.dir
        push()
        translate(x,y)
        rotate(self.vel.heading() + PI/2)
        ax,ay,bx,by,cx,cy = [0,-10,-5,5,5,5]
        triangle(ax,ay,bx,by,cx,cy)
        pop()


def setup():
    
    print("import")
    
    size(500,500)
    

    for i in range(numbirds):
        b = Bird(randomVec(500,500),random(TWO_PI),1)
        birds.append(b)
    
def neighboravg(a,radius):
    sum = PVector(0,0)
    for b in birds:
        if(a.pos.dist(b.pos) < radius) and (b != a):
            sum.add(b.vel)
    if sum.mag() == 0:
        return a.vel

    return sum.normalize()
    
 
def draw():
    background(50)
    global T
    global corrlength
    T = mouseX / 500.
    T = T if T < 0.9 else 1.
    corrlength = (1 - mouseY / 500.) * 100
    for b in birds:
        noFill()
        stroke(0)
        average = neighboravg(b, corrlength)
        b.align(average)
    
    for b in birds:
        b.timestep()
        b.drawbird()
        noFill()
        stroke(255,255,255,50)
        circle(b.pos.x, b.pos.y, corrlength)
    
    avgdirection = avgDir(birds)
    avgdirection.mult(30. * 1./numbirds)
    stroke(255)
    line(30,400,30 + avgdirection.x,400 + avgdirection.y)
    noFill()
    circle(30,400, 2 * avgdirection.mag())
    text("average direction " + str(avgdirection.heading()), 10,450)
    text("temperature" + str(T), 10, 470)
    drawDistribution()
