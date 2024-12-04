import time
import gc

# computation mode
manhattan = True

# choose display mode
traceMode = False
coarseGrainMode = False
coarseGrainSize = 25
resetTime = 1

# array that stores the birds
birds = []

# intrinsic and extrinsic noise parameter
T = 0.5
h = 1.

# distance to consider as nearest neighbor
interactionradius = 10

# global velocity
gvel = 1.

# stiffness, or configuration energy 
J = 1.


# number of birds
numbirds = 100

#gridSizes
gridSizes = [1, 2, 4, 5, 10, 20, 25, 50, 100, 125, 250]

#numGrid
numGrid = gridSizes[0]

#density
density = 1.0

def genMatrix(numGrid, matrix):
    gridSize = width / numGrid
    for b in birds:
        x = floor(b.pos.x / gridSize)
        y = floor(b.pos.y / gridSize)
        matrix[x][y].add(b.vel)
    
def avgVel(b,matrix, numGrid):
    gridSize = width / numGrid
    
    avgVel = PVector(0,0)
    x = floor(b.pos.x / gridSize)
    y = floor(b.pos.y / gridSize)
    for k in range(9):
        i = k % 3 - 1
        j = floor(k/3) - 1
        if(i == 0 and j == 0):
            continue
        avgVel.add(matrix[(x + i) % numGrid][(y + j) % numGrid])
    return avgVel.normalize()

def correlation():
    
    # allcorr = []
    
    # for a in birds:
    #     if a.pos.x > 400 or a.pos.x < 100 or a.pos.y < 100 or a.pos.y > 400:
    #         continue
    #     for b in birds:
    #         if a == b:
    #             break
    #     # b =birds[0]
        
    #         corr = [PVector.dot(a.vel,b.vel),PVector.dist(a.pos, b.pos)]
    #         allcorr.append(corr)
    # with open("correlation.txt", "w+") as f:
    #     text = ""
    #     for c in allcorr:
    #         text += str(c[0]) + "," + str(c[1]) + "\n"
    #     f.write(text)
        
    # get closest radius where the correlation is less than some threshold
    threshold = 0.7
    
    avgcorrlength = 0.
    
    for a in birds:
        corrlength = 500.
        for b in birds:
            corr = PVector.dot(a.vel,b.vel)
            distance = PVector.dist(a.pos, b.pos)
            if corrlength > distance:
                if corr < threshold:
                    corrlength = distance
        avgcorrlength += corrlength
        
    return avgcorrlength / numbirds
            
def timegraph(orderparam):
    with open("time.txt", "a+") as f:
        data = [frameCount, orderparam]
        t = str(data)[1:-2]
        print(t)
        f.write(t + "\n")

def updateParams(orderparam):
    global J
    global T
    global h
    global numGrid
    global density
    i=0
    with open("log.txt", "a+") as f:
        data = [i, T, h, density, numbirds, gvel, orderparam]
        t = str(data)[1:-2]
        print(t)
        f.write(t + "\n")
    i = int(frameCount / (60 * resetTime)) - 1
    #J = map( i % 10, 0, 9, 0.01, 0.5) #dont update J
    T = map( int(i % 10), 0, 9, 0.0, 1.0)
    h = map( int(i / 10), 0, 9, 0.0, 1.0)
    #numGrid = gridSizes[(i) / 10 ]
    numGrid = gridSizes[4]
    
#def orderParamGraph(noiseparam, orderparam, density):
    #saves data (noise, order parameter, density) for plotting.
    #print("noise, orderParameter, density", noiseparam, orderparam, density)
    #with open("orderParam.txt", "a+") as f:
        #data = [noiseparam, orderparam, density]
        #t = str(data)[1:-1]
        #f.write(t + "\n")

def reset():
    del birds[0:]
    gc.collect()
    # init birds ini random potitions and directions, store them in array birds[]
    for i in range(numbirds):
        b = Bird(randomVec(500,500),random(TWO_PI),1)
        birds.append(b)
    

def coarseGraining(grainSize):
    numGrain = int(width/ grainSize)
    Density = []
    direction = []
    for i in range(numGrain):
        densitycol = []
        dircol = []
        # stroke(255,255,255,20)
        for j in range(numGrain):
            densitycol.append(0.)
            dircol.append(PVector(0,0))
        Density.append(densitycol)
        direction.append(dircol)
    for b in birds:
        i = int(b.pos.x / grainSize)
        j = int(b.pos.y / grainSize)
        Density[i][j] += 1.
        dir = direction[i][j].add(b.vel)
        
    for i in range(numGrain):
        for j in range(numGrain): 
            push()
            colorMode(HSB, 360, 100, 100)
            noStroke()
            fill(degrees(direction[i][j].heading()) + 180, 100, 10 * Density[i][j])
            rect(i * grainSize, j * grainSize, grainSize, grainSize)
            pop()
        

# creates random vector with components between 0 and 1
def randomVec(x,y):
    return PVector(random(x),random(y))

# hamiltonian
def energy(a,b):
    return cos(a.dir - b.dir)

# partition function
def partition_function():
    sum = 0
    for a in birds:
        for b in birds:
            sum = exp(- energy(a,b)/T)
    return sum

# adds up all spins into bins, for analysis of distribution 
def drawDistribution():
    bins = []
    numbins = 30

    # initialize array
    for b in range(numbins):
        bins.append(0)
    
    # sort every angle into its respective bin
    for a in birds:
        bins[floor((a.dir.heading() % TWO_PI) / TWO_PI * numbins)] += 1
    
    # draws the bins at the bottom
    i = 0
    for b in bins:
        y = 2 * b
        rect(i * width/ numbins, 500 - y, width/numbins, y)
        i += 1

# sums all vectors in given vector arrray
def avgDir(arr):
    sum = PVector(0,0)
    for a in arr: 
        sum.add(a.vel)
        
    return sum


class Bird:
    def __init__(self, pos, angle, vel):
        self.pos = pos
        
        # stores direction of neighbors
        self.dir = PVector(1,0)
        self.dir.rotate(angle)
        
        # normalized velocity
        self.vel = PVector(self.dir.x * vel, self.dir.y * vel)
        self.vel.normalize()
        self.vel.rotate(angle)

    # basically rotates velocity, adds velocity to position            
    def timestep(self):
        # normalized vector subtraction is the same as getting rotating by delta theta 
        diff = PVector.sub(self.dir, self.vel)
        
        # neighbor strength (stiffness)
        diff.mult(J * 0.5)
        # noise component, initialize as a vector
        extrinsicNoise = PVector(1,0)
        # rotate by random between -pi and pi
        extrinsicNoise.rotate(random(-PI,PI))
        
        # multiplies noise by a constant, this is external noise param h
        extrinsicNoise.setMag(h)
        
        # linear combination
        diff.add(extrinsicNoise)
        
        # rotate velocity vector
        self.vel.add(diff)
        self.vel.normalize()
        
        # rotate velocity again due to internal noise
        self.vel.rotate(T * random(-PI,PI))
        
        # add velocity to position
        self.pos = self.pos.add(PVector.mult(self.vel, gvel))
        
        # circular boundary conditions
        self.pos.x = self.pos.x % width
        self.pos.y = self.pos.y % width
        
    # stores neighbor averages in self.dir
    def align(self, neighboravgdir):
        self.dir = neighboravgdir
        self.dir.normalize()
    
    # draws bird
    def drawbird(self):
        fill(255)
        stroke(0)
        x = self.pos.x
        y = self.pos.y
        
        # push and pop just mean all translations done here are removed after pop
        # translates and rotates the whole system, so don't want to compound that
        push()
        translate(x,y)
        rotate(self.vel.heading() + PI/2)
        ax,ay,bx,by,cx,cy = [0,-10,-5,5,5,5]
        triangle(ax,ay,bx,by,cx,cy)
        pop()
    
    # draw simplified bird for traces
    def drawtrace(self):
        x = self.pos.x
        y = self.pos.y
    
        push()
        stroke(255)
        strokeWeight(1)
        translate(x,y)
        rotate(self.vel.heading() + PI/2)
        line(0,0,0,3)
        pop()


def setup():
    with open("log.txt", "w+") as f:
        f.write("i, T, h, density, len(birds), gvel, orderparam\n")
    with open("time.txt", "w+") as f:
        f.write("frames, orderparam")
    #with open("orderParam.txt", "w+") as f:
        #f.write("noise, order parameter, density\n")
    
    global traceMode
    global gvel
    # canvas size    
    size(500,500)
    if traceMode:
        background(255,255,255,1.0)
    
    reset()

# gets the normalized vector sum of all bird velocities if they are nearest neighbors to bird a
def neighboravg(a,radius):
    sum = PVector(0,0)
    
    # loop through the nearest neighbors of bird a
    for b in birds:
        if (a.pos.dist(b.pos) < radius):
            # add up all their velocities
            sum.add(b.vel)

    # return the normalized velocity (only care about direction)
    return sum.normalize()
    
 
def draw():
    
    # tell python that these variables don't care about scope
    global traceMode
    global T
    global J
    global interactionradius
    global h
    global gridSizes
    global numGrid
    global density
    

    # set background color (r,g,b)
    if not traceMode:
        background(50, 50 ,50 )
    else: 
        push()
        c = color(0,0,0,50)
        fill(c)
        rect(0,0,600,600)
        pop()
    if coarseGrainMode:
        coarseGraining(coarseGrainSize)
    
    # map temperature and correlation length to mouse position
    #T = mouseX / 500.
    #T = T if T < 0.9 else 1.
    interactionradius = (1 - mouseY / 500.) * 300
    #gridSizes = [1, 2, 4, 5, 10, 20, 25, 50, 100, 125, 250] 
    #numGrid = gridSizes[floor(map(mouseY, 0, 500, 0, 11))]
    #numGrid = gridSizes[4]
    #print("numGrid " , numGrid)
    if manhattan:
        matrix = [[PVector(0,0) for i in range(numGrid)] for j in range(numGrid)]
        genMatrix(numGrid, matrix)
        
        for b in birds:    
            average = avgVel(b, matrix, numGrid)
            b.align(average)
    else:
        # loop through all the birds, get their nearest neighbor spins, store them in bird.dir
        for b in birds:
            average = neighboravg(b, interactionradius)
            b.align(average)
    # actually apply the calculations, separate two loops because each calculation might propagate
    if manhattan:
        for i in range(numGrid):
            stroke(255,255,255,500 / numGrid)
            line(0, width / numGrid * i, width, width  / numGrid * i)
            line(width / numGrid * i,0, width  / numGrid * i, width)
    for b in birds:
        b.timestep()
    
        if not traceMode:
            b.drawbird()
        
            noFill()
            stroke(255,255,255,50)
            # radius circles
            if not manhattan:
                circle(b.pos.x, b.pos.y, interactionradius)
    
                
        else:
            b.drawtrace()
    
    # below are for analysis only
    if not traceMode:
        # gets vector sum of bird velocities
        avgdirection = avgDir(birds)
        density = 0.0 
        
        #print("order parameter", avgdirection.mag()/numbirds)
        
        # gets magnetization
        avgdirection.mult(1./numbirds)
        stroke(255)
        line(30,400,30 + avgdirection.x * 30,400 + avgdirection.y * 30)
        noFill()
    
        circle(30,400, 2 * avgdirection.mag())
        text("average direction (deg) " + str((-180./PI)*avgdirection.heading()), 10,450)
        text("noise amplitude" + str(T), 10, 470)
        if manhattan:
            density = float(numbirds) / float(numGrid ** 2)
            text("density" + str(numbirds / float(numGrid ** 2)), 10, 490)
        else:
            density = numbirds / (float(500 ** 2)/interactionradius ** 2 * PI)
            text("density" + str(numbirds / (float(500 ** 2)/interactionradius ** 2 * PI)), 10, 490) 
        
        drawDistribution()
        
        #The fact that T is global means it does the funny thing with ints/floats when I try to pass it
        #to a function so I'll just do this. (Im the sloppiest coder ever)
        #noiseParam = T
        
        if frameCount % 30 == 0:
            # timegraph(avgdirection.mag())
            #print(correlation())
            pass
        if frameCount % (60 * resetTime) == 0: 
            #print([T, interactionradius, avgdirection.mag()])
            updateParams(avgdirection.mag()) #this argument is the order parameter.
            #orderParamGraph(noiseParam, avgdirection.mag(), density)
            reset()
            
    
        
