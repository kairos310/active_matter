# array that stores the birds
birds = []

# temperature
T = 0

# distance to consider as nearest neighbor
corrlength = 0

# number of birds
numbirds = 100

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


# class Plot:
#     def __init__(self, arr):
#         self.arr
#     def add():
        
#     def plot():
#         i = 0
#         for a in self.arr: 
#             line(
#             i += 1
    

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

    # basically rotates velocity, adds velocity to position            
    def timestep(self):
        
        # normalized vector subtraction is the same as getting rotating by delta theta 
        diff = PVector.sub(self.dir, self.vel)
        
        # noise component, initialize as a vector
        noisevec = PVector(1,0)
        # rotate by random between -pi and pi
        noisevec.rotate(random(-PI,PI))
        
        # multiplies noise by a constant, (this is T for now but should change)
        noisevec.setMag(T)
        
        # set mag of interation energy to inverse (also should change)
        diff.setMag(1. - T)
        
        # linear combination
        diff.add(noisevec)
        
        # inertial term, so they don't spin immediately
        diff.setMag(0.1)
        
        # rotate velocity vector
        self.vel.add(diff)
        self.vel.normalize()
        
        # add velocity to position
        self.pos = self.pos.add(self.vel)
        
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


def setup():
    # canvas size    
    size(500,500)
    
    # init birds ini random potitions and directions, store them in arraw birds[]
    for i in range(numbirds):
        b = Bird(randomVec(500,500),random(TWO_PI),1)
        birds.append(b)

# gets the normalized vector sum of all bird velocities if they are nearest neighbors to bird a
def neighboravg(a,radius):
    sum = PVector(0,0)
    
    # for every bird that is not a, loop through the nearest neighbors of bird a
    for b in birds:
        if (b != a) and (a.pos.dist(b.pos) < radius):
            # add up all their velocities
            sum.add(b.vel)

    if sum.mag() == 0:
        return a.vel
    
    # return the normalized velocity (only care about direction)
    return sum.normalize()
    
 
def draw():
    # set background color (r,g,b)
    background(50, 50 ,50 )
    
    # tell python that these variables don't care about scope
    global T
    global corrlength
    # map temperature and correlation length to mouse position
    T = mouseX / 500.
    T = T if T < 0.9 else 1.
    corrlength = (1 - mouseY / 500.) * 100
    
    # loop through all the birds, get their nearest neighbor spins, store them in bird.dir
    for b in birds:
        noFill()
        stroke(0)
        average = neighboravg(b, corrlength)
        b.align(average)
    
    # actually apply the calculations, separate two loops because each calculation might propagate
    for b in birds:
        b.timestep()
        b.drawbird()
        noFill()
        stroke(255,255,255,50)
        # radius circles
        circle(b.pos.x, b.pos.y, corrlength)
    
    # below are for analysis only
    
    # gets sum of velocities
    avgdirection = avgDir(birds)
    
    # gets magnetization
    avgdirection.mult(30. * 1./numbirds)
    stroke(255)
    line(30,400,30 + avgdirection.x,400 + avgdirection.y)
    noFill()
    circle(30,400, 2 * avgdirection.mag())
    text("average direction " + str(avgdirection.heading()), 10,450)
    text("temperature" + str(T), 10, 470)
    drawDistribution()
