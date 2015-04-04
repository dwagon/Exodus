#!/usr/local/bin/python
# 
# Script to simulate colonial expansion of the galaxy
#
# Writen by Dougal Scott <dwagon@connect.com.au>
# $Id: galaxy.py,v 1.6 2005/11/21 21:34:20 dwagon Exp dwagon $
# $Source: /Users/dwagon/cvs/colonise/RCS/galaxy.py,v $

import os, sys, getopt, random, re, math, time
import pygame

verbose=0
planetcount=0
terrestriallist=[]
instdata={}

CARGOSIZE=100000000
MAXSHIPS=500
BLOWUP=10000
mode=1	# 0=no-recolonisation, 1=recolonisation
logfile=None

black=0,0,0
red=255,0,0
green=0,255,0
blue=0,0,255
purple=255,0,255
white=255,255,255

screensize=screenwidth,screenheight=800,800
galaxysize=galaxyradius,galaxyheight=100,1

################################################################################
class Coord:
    def __init__(self, x, y, z=0):
    	self.x=x
	self.y=y
	self.z=z

    ############################################################################
    def coords(self):
    	return (self.x, self.y, self.z)

    ############################################################################
    def __ne__(self, loc):
    	return (self.x!=loc.x or self.y!=loc.y or self.z!=loc.z)

    ############################################################################
    def __eq__(self, loc):
    	return (self.x==loc.x and self.y==loc.y and self.z==loc.z)

    ############################################################################
    def __nonzero__(self):
    	return self.x!=0 or self.y!=0 or self.z!=0

    ############################################################################
    def distance(self, loc):
    	#dist=abs(self.x-loc.x)+abs(self.y-loc.y)+abs(self.z-loc.z)
	dist=math.sqrt((self.x-loc.x)**2 + (self.y-loc.y)**2 + (self.z-loc.z)**2)
	return dist

    ############################################################################
    def __abs__(self):
    	x=self.x*float(screenwidth)/galaxyradius
	y=self.y*float(screenheight)/galaxyradius
	return (int(x)+1,int(y)+1)
    	
    ############################################################################
    def __repr__(self):
    	return "<Coord %d, %d, %d>" % (self.x,self.y,self.z)

################################################################################
class Ship:
    def __init__(self, startplanet=None, name=None):
	self.currplanet=None
	if startplanet:
	    self.location, self.orbit=startplanet.location, startplanet.orbit
	else:
	    self.location=Coord(0,0,0)
	    self.orbit=0
	if not name:
	    self.name=self.GenerateName()
	else:
	    self.name=name
	self.speed=2
	self.cargo=0
	self.loaded=0
	self.destination=None

    #############################################################################
    def Plot(self, surf):
    	itime=time.time()
	color=None
	if self.loaded:
	    color=purple
	else:
	    color=white

	if self.destination:
	    pygame.draw.line(surf, color, abs(self.location), abs(self.destination.location), 1)
	pygame.draw.circle(surf, color, abs(self.location), 2, 0)
	Instrument("Ship.Plot", itime)

    ############################################################################
    def GenerateName(self):
    	return "ship"
    	f=open('/usr/share/dict/words')
	output=f.readlines()
	f.close()
	numchoices=len(output)
	pos=int(random.random()*numchoices)
	return output[pos].strip().capitalize()

    ############################################################################
    def __repr__(self):
    	if self.destination:
	    return "<Ship %s at %s going to %s cargo: %s>" % (self.name, self.location, self.destination.location, self.cargo)
	else:
	    return "<Ship %s at %s going nowhere cargo: %s>" % (self.name, self.location, self.cargo)

    ############################################################################
    def has_destination(self):
    	if self.destination:
	    return 1
	return 0

    ############################################################################
    def determine_destination(self):
    	itime=time.time()
    	closestbest=0.0
	best=None
	for planet in terrestriallist:
	    if self.loaded:
		# Emphasise uncolonised planets
	   	if planet.homeplanet: continue
		if self.currplanet:
		    if planet.population>self.currplanet.population: continue
		if mode==0:
		    if planet.population!=0:
			continue
		    else:
			desire=planet.popcapacity/1000
		elif mode==1:
		    # KORG try desire relation to available capacity
		    desire=planet.popcapacity/1000-(planet.population*100000)
		    desire=100.*((planet.popcapacity-planet.population)/(1.0*planet.popcapacity))**5 * planet.popcapacity
		    if desire<0.0: desire=0.0
		else:
		    sys.stderr.write("Unknown mode %d\n" % mode)
		    sys.exit(1)
	    else:
		desire=planet.population
	    distance=self.location.distance(planet.location)
	    if distance<4:
		continue
	    distmod=distance**2.0		# Emphasise closeness
	    pull=float(desire)/distmod*(1.0-random.random()/5.0)
	    if pull>closestbest:
		best=planet
		closestbest=pull
	if not best:
	    Warn("No better location than here for %s" % `self`)
	    return self.location
	self.destination=best
	Instrument("Ship.determine_destination",itime)

    ############################################################################
    def move(self):
    	itime=time.time()
	moved=0
	goes=0
	self.currplanet=None
	x,y,z=self.location.coords()
	destx,desty,destz=self.destination.location.coords()
	while moved<self.speed:
	    if x==destx and y==desty and z==destz:
		break
	    goes+=1
	    if goes>self.speed*200:	# Hey we got lost
		print "Got lost (%s,%s,%s)->(%s,%s,%s)" % (x,y,z,destx,desty,destz)
		break
	    a=d6()
	    if a in (1,2):
		if x<destx:
		    x+=1
		    moved+=1
		elif x>destx:
		    x-=1
		    moved+=1
	    elif a in (3,4):
		if y<desty:
		    y+=1
		    moved+=1
		elif y>desty:
		    y-=1
		    moved+=1
	    else:
		if z<destz:
		    z+=1
		    moved+=1
		elif z>destz:
		    z-=1
		    moved+=1
	self.location=Coord(x,y,z)
	Instrument("ship.move",itime)

    ############################################################################
    def load(self):
	#print "Loading at %s" % `self.destination`
	if self.destination.population<CARGOSIZE*2:
	    #print "Can't load more than half the population onto %s" % `self`
	    return
    	self.loaded=1
	self.cargo=CARGOSIZE
	self.destination.population-=self.cargo
	self.currplanet=self.destination
	self.destination=None

    ############################################################################
    def unload(self):
    	self.loaded=0
	#print "Unloading at %s" % `self.destination`
	#if self.destination.population==0:
	    #print "%s newly colonising %s with %s" % (self.name, `self.destination`, self.cargo)
	self.destination.population+=self.cargo
	self.loaded=0
	self.cargo=0
	self.currplanet=self.destination
	self.destination=None

    ############################################################################
    def destination(self, loc=None):
    	if not loc:
	    return self.destination
	else:
	    self.destination=loc

################################################################################
class Planet:
    def __init__(self, plantype, loc, orbit, atmosphere='normal'):
	self.plantype=plantype
	self.location=loc
	self.orbit=orbit
	self.size=0
	self.density=0
	self.gravity=0
	self.homeplanet=0
	self.population=0
	self.popcapacity=0
	global planetcount
	planetcount+=1
	if plantype=='terrestrial':
	    self.genTerrestrial()
	elif plantype=='gasgiant':
	    self.genGasgiant()
	elif plantype=='asteroid':
	    self.genAsteroid()
	elif plantype=='rockball':
	    self.genRockball()
	elif plantype=='browndwarf':
	    self.genBrowndwarf()
	elif plantype=='greenhouse':
	    self.genGreenhouse()
	else:
	    Warn("Unhandled planettype %s" % plantype)
	self.gravity=self.size*self.density*0.0000228

    #############################################################################
    def Plot(self, surf):
    	print "Plot(planet)"
    	pass

    ############################################################################
    def genGreenhouse(self):
	pass

    ############################################################################
    def genBrowndwarf(self):
	pass

    ############################################################################
    def genRockball(self):
	pass

    ############################################################################
    def genAsteroid(self):
	pass

    ############################################################################
    def genGasgiant(self):
	self.size=(d6(2)+2)*10000
	self.density=(d6(3)/10.0)+0.5

    ############################################################################
    def genTerrestrial(self):
	self.size=d6(2)*1000
	self.density=d6(3)/10.0+d6()
	x=d6(2)
	if x in (2,3,4):
	    self.genRockball()
	elif x==5:
	    self.genGreenhouse()
	elif x in (6,7):
	    # Earthlike
	    self.popcapacity=1e10
	    pass
	elif x in (8,9):
	    # Desert
	    self.popcapacity=1e8
	    pass
	elif x==10:
	    # Hostile
	    self.popcapacity=1e7
	    pass
	elif x==11:
	    # Icy rockball
	    self.popcapacity=1e6
	    pass
	else:
	    # Iceball
	    self.popcapacity=1e6
	    pass

    ############################################################################
    def __repr__(self):
    	planstr=""
	if self.population>0:
	    planstr="Population: %s" % self.population
	else:
	    planstr="Empty"
    	return "<Planet %s: %s, Orbit %s %s>" % (self.plantype, `self.location`, self.orbit, planstr)

################################################################################
class Star:
    def __init__(self,loc):
    	bits=self.genStarClass()
	self.location=loc
	self.startype=bits[0]
	self.stardesc=bits[1]
	self.starsize=bits[2]
	self.orbits=[]
	self.genOrbits(self.startype, self.starsize)

    #############################################################################
    def Plot(self, surf):
    	print "Plot(star)"

    ############################################################################
    def planets(self):
    	return [orbit for orbit in self.orbits if orbit!=None]

    ############################################################################
    def __repr__(self):
    	return "<Star: %s %s %s>" % (self.startype, self.starsize, self.stardesc)

    ############################################################################
    def genOrbits(self, startype, starsize):
    	bits=self.getOrbitData(startype, starsize)
	if not bits:
	    return	
	size,stellmass,bzonestart,bzoneend,limit,stellrad, plan, orbs, life=bits
	if d6(3)>=plan:		# No planets
	    return
	for i in range(dice(orbs)):
	    radius=self.genOrbitRadius(startype, starsize, stellrad, i)
	    if radius<bzonestart:	# Orbits before the biozone
		x=d6(2)
		if 2<=x<=4:
		    self.orbits.append(None)
		elif 5<=x<=6:
		    self.orbits.append(Planet('greenhouse', self.location, i))
		elif 7<=x<=9:
		    self.orbits.append(Planet('rockball', self.location, i))
		elif 10<=x<=11:
		    self.orbits.append(Planet('asteroid', self.location, i))
		else:
		    if i==0:
			self.orbits.append(None)
		    else:
			self.orbits.append(Planet('browndwarf', self.location, i))
	    elif radius>bzoneend:	# Orbits after the biozone
	    	x=d6()
		if radius>10*bzoneend:
		    x+=1
		if x==1:
		    self.orbits.append(Planet('terrestrial', self.location, i))
		elif x==2:
		    self.orbits.append(Planet('asteroid', self.location, i))
		elif x==2:
		    self.orbits.append(None)
		elif 4<=x<=6:
		    self.orbits.append(Planet('gasgiant', self.location, i))
		elif x==7:
		    self.orbits.append(Planet('terrestrial', self.location, i, atmosphere='trace'))
	    else:	# Orbits within the biozone
		x=d6(2)
		if x in (2,3):
		    self.orbits.append(None)
		elif 4<=x<=8:
		    self.orbits.append(Planet('terrestrial', self.location, i))
		elif x in (9,10):
		    self.orbits.append(Planet('asteroid', self.location, i))
		elif x==11:
		    self.orbits.append(Planet('gasgiant', self.location, i))
		else:
		    self.orbits.append(Planet('browndwarf', self.location, i))

    ############################################################################
    def genOrbitRadius(self, startype, starsize, stellradius, orbitnum):
	inner=d6()*0.1
	if orbitnum==0:
	    if inner<stellradius:
		return None
	    else:
		return inner
	bode=self.genBodeConstant(startype, starsize)
	return inner+(2**orbitnum)*bode

    ############################################################################
    def genBodeConstant(self, startype, starsize):
	if startype=='M' and starsize=='VI':
	    bode=0.2
	else:
	    x=d6()
	    if x in (1,2):
		bode=0.3
	    elif x in (3,4):
	    	bode=0.35
	    else:
		bode=0.4
	return bode

    ############################################################################
    def getOrbitData(self, startype, starsize):
        """
	size, stellar mass, biozone start, biozone end, inner limit, stellar radius,
	planets on, #orbits, life roll
	"""
	orbitData={
	    'O': [ 
		('Ia', 70,790,1190,16,0.2,0,'',-12),
		('Ib', 60,630,950,13,0.1,0,'',-12),
		('V', 50,500,750,10,0.0,0,'',-9),
		],
	    'B': [
	    	('Ia', 50, 500, 750, 10, 0.2, 0, '', -10),
	    	('V', 10, 30, 45, 0.6, 0, 4, '3d', -9),
		],
	    'A': [
	    	('Ia', 30, 200, 300, 4.0, 0.6, 3, '3d+3', -10),
	    	('III', 6, 5, 7.5, 0, 0, 3, '3d+1', -10),
	    	('V', 3.0, 3.1, 4.7, 0, 0, 5, '3d-1', -9),
		],
	    'F': [
	    	('Ia', 15, 200, 300, 4.0, 0.8, 4, '3d+3', -10),
	    	('V', 1.9, 1.6, 2.4, 0, 0, 13, '3d-1', -8),
		],
	    'G': [
	    	('Ia', 12, 160, 240, 3.1, 1.4, 6, '3d+3', -10),
	    	('V', 1.1, 0.8, 1.2, 0, 0, 16, '3d-2', 0),
	    	('VI', 0.8, 0.5, 0.8, 0, 0, 16, '2d+1', 1),
		],
	    'K': [
	    	('Ia', 15, 125, 190, 2.5, 3.0, 10, '3d+2', -10),
	    	('V', 0.9, 0.5, 0.6, 0, 0, 16, '3d-2', 0),
	    	('VI', 0.5, 0.2, 0.3, 0, 0, 16, '2d+1', 1),
		],
	    'M': [
	    	('Ia', 20, 100, 150, 2, 7, 16, '3d', -10),
	    	('Ib', 16, 50, 76, 1, 4.2, 16, '3d', -10),
	    	('II', 8, 16, 24, 0.3, 1.1, 16, '3d', -9),
	    	('III', 4, 5, 7.5, 0.1, 0.3, 16, '3d', -6),
	    	('V', 0.3, 0.1, 0.2, 0, 0, 16, '3d-2', +1),
	    	('VI', 0.2, 0.1, 0.1, 0, 0, 16, '2d+2', +2),
	    	],
	    'D': [],
	    }
	if startype=='D':	# Ignore for now
	    return None

	if not orbitData.has_key(startype):
	    Warn("No orbitData for type %s" % startype)
	    return None
	for i in orbitData[startype]:
	    if i[0]==starsize:
		return i
	Warn("No orbitData for type %s size %s" % (startype, starsize))
	return None

    ############################################################################
    def genGiantType(self, desc, size):
    	x=d6(2)
	if x==2:
	    return ("O", "Blue %s" % desc, size)
	elif x==3:
	    return ("M", "Red %s" % desc, size)
	elif x in (4,5):
	    return ("B", "Blue-White %s" % desc, size)
	elif 6<=x<=9:
	    return ("K", "Orange %s" % desc, size)
	else:
	    return ("A", "White %s" % desc, size)

    ############################################################################
    def genStarClass(self):
    	x=d6(3)
	if 3<=x<=5:	# White Dwarf
	    return ("D", "White Dwarf", "")
	elif x==6:	# Subdwarf
	    y=d6()
	    if y==1:
		return ("G", "Yellow Subdwarf", "VI")
	    elif y==2:
		return ("K", "Orange Subdwarf", "VI")
	    else:
		return ("M", "Red Subdwarf", "VI")
	elif 7<=x<=17:	# Main sequence
	    y=d6(3)
	    if y==3:
		return ("O", "Blue", "V")
	    elif y==4:
		return ("B", "Blue-White", "V")
	    elif y==5:
	    	return ("A", "White", "V")
	    elif y==6:
	    	return ("F", "Yellow-White", "V")
	    elif y==7:
	    	return ("G", "Yellow", "V")
	    elif y==8:
	    	return ("K", "Orange", "V")
	    else:
	    	return ("M", "Red", "V")
	else:		# Giant star
	    y=d6(3)
	    if y==3:
		z=d6(1)
		if 1<=z<=2:
		    return self.genGiantType("SuperGiant", "Ia")
		else:
		    return self.genGiantType( "SuperGiant", "Ib")
	    elif y==4:
	    	return self.genGiantType( "Large Giant", "II")
	    elif 5<=y<=12:
	    	return self.genGiantType( "Giant", "III")
	    else:
		return self.genGiantType( "Subgiant", "IV")
		
################################################################################
class StarSystem:
    def __init__(self,loc):
    	self.numstars=self.genStarNum()
    	self.numstars=1				# Keep it simple
	self.location=loc
	self.starlist=[]
	for i in range(self.numstars):
	    self.starlist.append(Star(loc))
	self.basecolor=None

    #############################################################################
    def Plot(self, surf):
    	itime=time.time()
    	if not self.basecolor:
	    color=None
	    for star in self.starlist:
		for planet in star.planets():
		    if planet.population>0:
			color=green
			self.basecolor=color=green
			break
		    elif planet.popcapacity>0 and not color:
			color=blue
			break
	    if not color:
		self.basecolor=color=red
	else:
	    color=self.basecolor

    	pygame.draw.circle(surf, color, abs(self.location), 2, 0)
	Instrument("StarSystem.Plot", itime)

    ############################################################################
    def stars(self):
    	return self.starlist

    ############################################################################
    def __len__(self):
    	return len(self.starlist)

    ############################################################################
    def __repr__(self):
    	str=""
    	for i in self.starlist:
	    str+="%s " % `i`
    	return "<StarSystem %s: %s>" % (self.location, str)

    ############################################################################
    def genStarNum(self):
    	x=d6(2)
	if 2<=x<=10:
	    return 1
	elif x==11:
	    return 2
	elif x==12:
	    return 3
	else:
	    print "x=%d" % x

################################################################################
class Galaxy:
    def __init__(self, radius=1000, height=100):
    	self.starbits=[]
	self.initialise(radius, height)

    #############################################################################
    def starsystems(self):
   	return self.starbits

    #############################################################################
    def __getitem__(self, loc):
    	for starsystem in self.starbits:
	    if starsystem.location==loc:
		return starsystem

    #############################################################################
    def Plot(self, surf):
	print "Plot(Galaxy)"
    	pass

    #############################################################################
    def initialise(self, radius, height):
    	numstars=0
    	for x in range(radius):
	    for y in range(radius):
		for z in range(height):
		    loc=Coord(x,y,z)
		    if d6(2)>=11:
			ss=StarSystem(loc)
			self.starbits.append(ss)
			numstars+=len(ss)
	print "NumStars=%d" % numstars

################################################################################
def Instrument(str,secs):
    elapsed=time.time()-secs
    if not instdata.has_key(str):
	instdata[str]={ 'count':0, 'sum':0.0 }
    instdata[str]['count']+=1
    instdata[str]['sum']+=elapsed

################################################################################
def dice(str):
    itime=time.time()
    if not str:
	return 0
    reg=re.match('(?P<numdice>\d+)d(?P<modif>.*)', str)
    if reg:
	numdice=int(reg.group('numdice'))
	val=d6(numdice)
	Instrument("dice",itime)
	return eval("%d%s" % (val, reg.group('modif')))
    else:
	Warn("No idea how to handle %s" % str)
	sys.exit(0)

################################################################################
def d6(num=1):
    sum=0
    for i in range(num):
	sum+=int(random.random()*6)+1
    return sum

################################################################################
def Warn(msg):
    sys.stderr.write("%s\n" % msg)

################################################################################
def usage():
    sys.stderr.write("Usage: %s\n" % sys.argv[0])

################################################################################
def findHomePlanet(terrestriallist):
    found=0
    attempt=0
    cent=Coord(galaxyradius/2, galaxyradius/2, galaxyheight/2)
    mindist=galaxyradius*2
    homeplanet=None
    for planet in terrestriallist:
	if planet.popcapacity>1e9:
	    dist=planet.location.distance(cent)
	    if dist<mindist:
		mindist=dist
		homeplanet=planet

    print "Homeplanet=%s" % `homeplanet`
    homeplanet.population=int(homeplanet.popcapacity*0.5)
    homeplanet.homeplanet=1
    return homeplanet

################################################################################
def Diaspora(shiplist):
    itime=time.time()
    for ship in shiplist[:]:
	ship.startmonth=ship.location
	if random.random()*BLOWUP<=1:
	    print "Ship %s blew up" % `ship`
	    shiplist.remove(ship)
	    continue
	if not ship.destination:
	    ship.determine_destination()
	    #continue	# Takes time to navigate :)
	if not ship.destination:
	    shiplist.remove(ship)
	    print "Ship %s gives up" % `ship`
	    continue

	if ship.location!=ship.destination.location:
	    ship.move()
	else:
	    if ship.loaded:
		ship.unload()
		#shiplist.remove(ship)
	    else:
		ship.load()
	    continue
	if ship.location==ship.startmonth:
	    print "Static Ship=%s (%s)" % (`ship`, ship.startmonth)
    Instrument('Diaspora',itime)

################################################################################
def printPopulatedGalaxy(homeplanet):
    for starsystem in galaxy.starsystems():
	for star in starsystem.stars():
	    for planet in star.planets():
	    	if planet.population>0:
		    print "%s: %s (Dist %d)" % (`planet`, planet.population, planet.location.distance(homeplanet.location))

################################################################################
def endOfYear(shiplist,year):
    populated=0
    popcap=0
    totpop=0
    itime=time.time()
    for planet in terrestriallist:
	if planet.population>0:
	    totpop+=planet.population
	    populated+=1
	    #print 'EOY ship', planet.population>CARGOSIZE*10, len(shiplist)<MAXSHIPS
	    # KORG  reduced cargo*N
	    if planet.population>CARGOSIZE*10 and len(shiplist)<MAXSHIPS:
		for i in range(1):
		    s=Ship(planet)
		    s.destination=planet
		    s.load()
		    shiplist.append(s)
	    if planet.homeplanet:
		planet.population-=int(planet.population*0.03)
	    else:
		planet.population+=int(planet.population*0.03)
	    if planet.population>planet.popcapacity:
		planet.population=planet.popcapacity
	if planet.popcapacity>0:
	    popcap+=1
    #print "%s Year: %04d Ships: %d Colonised: %d/%d %0.2f%%" % ("#"*40, year, len(shiplist), populated, popcap, (100.0*populated/popcap))
    if logfile:
	f=open(logfile,"a")
	f.write("%d,%f,%f,%d\n" % (year, (100.0*populated/popcap),totpop, len(shiplist)))
	f.close()
    if populated==popcap:		# 100% colonised
	time.sleep(30)
    Instrument('endOfYear',itime)
    return year+1
	
################################################################################
def genAllPlanets():
    tmp=[]
    for starsys in galaxy.starsystems():
	for star in starsys.stars():
	    for planet in star.planets():
		tmp.append(planet)
    return tmp

################################################################################
def genTerrestrial(planetlist=None):
    tmp=[]
    if planetlist:
	for planet in planetlist:
	    if planet.popcapacity>0:
		tmp.append(planet)
    else:
	for starsys in galaxy.starsystems():
	    for star in starsys.stars():
		for planet in star.planets():
		    if planet.popcapacity>0:
			tmp.append(planet)
    return tmp

################################################################################
def drawText(surf, year, numships):
    itime=time.time()
    populated=0
    popcap=0
    totpop=0
    colpop=0
    homepop=0
    for planet in terrestriallist:
	if planet.population>0:
	    populated+=1
	    totpop+=planet.population
	    if not planet.homeplanet:
		colpop+=planet.population
	    else:
		homepop=planet.population
	if planet.popcapacity>0:
	    popcap+=1
    font=pygame.font.Font(None, 20)
    text=font.render("Year: %d Ships: %d Colonised: %d/%d %0.2f%% Population: %0.4fB Home %0.4fB Colonists: %0.4fB" % (year, numships, populated, popcap, (100.0*populated/popcap), totpop/1E9, homepop/1E9, colpop/1E9), 1, white)
    textpos=text.get_rect(centerx=surf.get_width()/2)
    surf.blit(text, textpos)
    Instrument('drawText',itime)

################################################################################
def main():
    global galaxy, terrestriallist
    pygame.init()
    screen=pygame.display.set_mode(screensize)
    galaxy=Galaxy(galaxyradius,galaxyheight)
    planetlist=genAllPlanets()
    terrestriallist=genTerrestrial(planetlist)
    print "planetcount=%d" % planetcount
    homeplanet=findHomePlanet(terrestriallist)
    #shiplist=[Ship(homeplanet)]
    shiplist=[]
    year=0
    try:
	while(1):
	    year=endOfYear(shiplist,year)
	    for i in range(12):
		for event in pygame.event.get():
		    if event.type==pygame.QUIT:
			raise KeyboardInterrupt
		Diaspora(shiplist)
		screen.fill(black)
		for ss in galaxy.starsystems():
		    ss.Plot(screen)
		for ship in shiplist:
		    ship.Plot(screen)
		drawText(screen, year, len(shiplist))
		pygame.display.flip()
    except KeyboardInterrupt:
	f=open('instrument.log','w')
	for k,v in instdata.items():
	    f.write("%s count: %d sum: %f avg: %f\n" % (k, v['count'], v['sum'], (v['sum']/v['count'])))
	f.close()
    	printPopulatedGalaxy(homeplanet)

################################################################################
if __name__=="__main__":
    try:
    	opts,args=getopt.getopt(sys.argv[1:], "v", ["log="])
    except getopt.GetoptError,err:
    	sys.stderr.write("Error: %s\n" % str(err))
    	usage()
	sys.exit(1)

    for o,a in opts:
    	if o=="-v":
	    verbose=1
	if o=="--log":
	    logfile=a

    main()

#EOF
