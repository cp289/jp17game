# Melody Mao
# CS269, January 2017
# Debug Davis (temporary title)

# agents.py
# This file defines the Thing class and its child classes.
# The Thing class extends the pygame Sprite class, so that it can be handled in Groups.
# The position of an Thing is the upper left corner of its image/rect.
# Playable Characters increase their stats with every level-up.

# to run test code for the classes in this file, call like this:
# python agents.py

import pygame
import sys

# some useful variables for the rest of this file
back, front, left, right, none = range( 5 )
green = ( 150, 255, 150 )
red = ( 255, 150, 150 )


'''
This class represents any entity in the game that has a position on the screen,
including both moving characters and stationary objects.
A Thing object that is not an instance of a child class represents some physical
object in the game, such as a table or wall.
'''
class Thing( pygame.sprite.Sprite ):
	
	# fields: position, image, rect
	
	# creates a new Thing at the given position
	def __init__( self, pos, img ):
		pygame.sprite.Sprite.__init__( self ) # call parent constructor
		
		self.pos = [ pos[0], pos[1] ]
		self.image = img
		
		self.rect = self.image.get_rect()
		self.rect.topleft = pos[0], pos[1]
		
		# fields for detecting collision
		self.rightEdge = pos[0] + self.rect.width
		self.bottomEdge = pos[1] + self.rect.height
	
	# return a clone of the position list
	def getPosition( self ):
		return self.pos[:]
	
	# returns the Rect representing the area of this Thing
	def getRect( self ):
		return self.rect
	
	# returns a tuple: top edge y, left edge x, bottom edge y, right edge x
	def getBounds( self ):
		return ( self.pos[1], self.pos[0], self.bottomEdge, self.rightEdge )
	
	# change the position of the Thing to the given coordinates
	def setPosition( self, newx, newy ):
		# change position of image/rect
		self.rect.topleft = newx, newy
		
		# change pos field
		self.pos[0] = newx
		self.pos[1] = newy
		
		# change fields for detecting collision
		self.rightEdge = newx + self.rect.width
		self.bottomEdge = newy + self.rect.height
	
	# change the position of the Thing by the given amounts in the x and y directions
	def move( self, dx, dy ):
		self.pos[0] += dx
		self.pos[1] += dy
		
		self.rect = self.rect.move( dx, dy )
		
		# change fields for detecting collision
		self.rightEdge += dx
		self.bottomEdge += dy
	
	# draws the Thing at its current position on the given Surface
	def draw( self, screen ):
		screen.blit( self.image, self.rect )
	
	# returns a string reporting the position and dimensions of the Thing
	def toString( self ):
		s = 'an Thing at (' + str( self.pos[0] ) + ', ' + str( self.pos[1] ) + '), of width ' \
			+ str( self.rect.width ) + ' and height ' + str( self.rect.height )
		return s

'''
This class represents a general Character in the game,
which can attack another Character and take damage.
A Character is a type of Thing.
'''
class Character( Thing ):
	
	# fields: name, totalHP, HP, showHP, rects for displaying HP bar
	
	# creates a new Character at the given position with the given image and name
	def __init__( self, pos, img, name, hp = 700 ):
		Thing.__init__( self, pos, img ) # call parent constructor
		
		self.name = name
		self.totalHP = hp
		self.hp = hp
		self.showHP = False
		
		# rects for drawing health bar
		self.hpbarWidth = 70
		self.hpbarHeight = 10
		self.hpbarBG = pygame.Rect( ( pos[0], pos[1] + self.rect.height ), ( self.hpbarWidth, self.hpbarHeight ) )
		self.hpbarFG = pygame.Rect( ( pos[0] + 1, pos[1] + self.rect.height + 1 ),
			( self.hpbarWidth - 2, self.hpbarHeight - 2 ) )
	
	# returns whether this Character has died, i.e. has 0 HP
	def isDead( self ):
		return self.hp == 0
	
	# change the position of the Character to the given coordinates
	def setPosition( self, newx, newy ):
		Thing.setPosition( self, newx, newy ) # call parent class method
		
		# adjust position of health bar
		self.hpbarBG.topleft = newx, newy + self.rect.height
		self.hpbarFG.topleft = newx + 1, newy + self.rect.height + 1
		
	
	# change the position of the Character by the given amounts in the x and y directions
	def move( self, dx, dy ):
		Thing.move( self, dx, dy ) # call parent class method
		
		# adjust position of health bar
		self.hpbarBG = self.hpbarBG.move( dx, dy )
		self.hpbarFG = self.hpbarFG.move( dx, dy )
	
	# reduces the Character's HP by the given amount
	def takeDamage( self, amt ):
		self.hp -= amt
		
		if self.hp < 0: # if the damage would make the HP negative, just make it 0
			self.hp = 0
	
	# attacks the given Character target and does the given amount of damage
	def attack( self, target, dmg ):
		target.takeDamage( dmg )
	
	# 
	#def die( self ):
	'''I'm not quite sure what this does'''
	
	# draws the Enemy with a health bar at its current position on the given Surface
	def draw( self, screen ):
		screen.blit( self.image, self.rect )
		
		# if HP bar should be displayed
		if self.showHP:
			# draw health bar background (in black)
			pygame.draw.rect( screen, ( 0, 0, 0 ), self.hpbarBG )
		
			# draw health bar foreground based on current HP left (if there is any)
			if self.hp != 0:
				fraction = float( self.hp ) / self.totalHP
				newWidth = int( ( self.hpbarWidth - 2 ) * self.hp / self.totalHP )
				self.hpbarFG.width = newWidth
				#pygame.draw.rect( screen, green, self.hpbarFG )
			
				if fraction > 0.3:
					pygame.draw.rect( screen, green, self.hpbarFG )
				else:
					pygame.draw.rect( screen, red, self.hpbarFG )
	
	# returns a string reporting the name and current HP of the Character
	def toString( self ):
		s = 'a Character named ' + self.name + ' with ' + str( self.hp ) + ' HP'
		return s

'''
This class represents an Enemy that can attack players and take damage.
An Enemy is a type of Character.
'''
class Enemy( Character ):
	
	# fields: stats
	
	# creates a new Enemy at the given position with the given image, name,
	# and starting amount of HP
	# all stats are given a default value of 700
	def __init__( self, pos, img, name, hp = 700 ):
		Character.__init__( self, pos, img, name ) # call parent constructor
		self.showHP = True # Enemies only appear in battle, so always show HP
		
		# initialize stats
		self.atk = 700
		self.dfn = 700
		self.spd = 700
		self.acc = 700
	
	# returns a string reporting the name and current HP of the Enemy
	def toString( self ):
		s = 'an Enemy named ' + self.name + ' with ' + str( self.hp ) + ' HP'
		return s

'''
This class represents a character that the player can control throughout the game.
Each character has stats, and can move around in exploring mode and attack in battle mode.
A PlayableCharacter is a type of Character.
'''
class PlayableCharacter( Character ):
	
	# fields: stats, growth rates, sprite images & status portrait, attacks
	
	# creates a new PlayableCharacter with the given position, images, and name
	# images should be given in the following order: front, back, left, right, status
	# all images besides status portrait should be the same size
	# all stats and growth rates are given a default value
	def __init__( self, pos, battlePos, imglist, name ):
		Character.__init__( self, pos, imglist[0], name ) # call parent constructor
		
		self.battlePos = [ battlePos[0], battlePos[1] ] # separate from the exploring pos, which is self.explorePos
		self.explorePos = [ pos[0], pos[1] ] # stores last exploring position when character goes into battle mode
		
		# initialize stats
		self.atk = 700
		self.dfn = 700
		self.spd = 700
		self.acc = 700
		self.time = 5
		
		# initialize growth rates
		self.hpGR = 100
		self.atkGR = 100
		self.dfnGR = 100
		self.spdGR = 100
		self.accGR = 100
		
		# initialize attack list as empty
		self.attacks = [] # all attacks the character is capable of
		self.currentAttacks = [] # attacks the character can currently choose from (a subset of self.attacks)
		
		# variables for current player state
		self.level = 1
		self.orientation = front
		
		# variables for player movement
		self.movement = [ 0, 0 ] # current stored movement to follow: direction, distance left to go
		self.step = 10 # how far the character moves in one time-step, if it is currently moving
		self.ghost = self.rect.copy() # represents the position of the character one time-step later
		
		# sprite images
		self.imgFront = imglist[0]
		self.imgBack = imglist[1]
		self.imgLeft = imglist[2]
		self.imgRight = imglist[3]
		self.imgStatus = imglist[4]
	
	# change the position of the PlayableCharacter to the given coordinates
	def setPosition( self, newx, newy ):
		Character.setPosition( self, newx, newy ) # call parent method
		
		self.ghost = self.rect.copy()
	
	# change the position of the PlayableCharacter by the given amounts in the x and y directions
	def move( self, dx, dy ):
		Character.move( self, dx, dy ) # call parent method
	
	# send the character towards the left, updating orientation
	# tile size should be a multiple of the player step size
	def goLeft( self, tileSize ):
		self.movement[0] = left
		self.movement[1] = tileSize
		self.orientation = left
		self.ghost = self.ghost.move( -self.step, 0 )
	
	# send the character towards the right
	# tile size should be a multiple of the player step size
	def goRight( self, tileSize ):
		self.movement[0] = right
		self.movement[1] = tileSize
		self.orientation = right
		self.ghost = self.ghost.move( self.step, 0 )
	
	# send the character towards the front
	# tile size should be a multiple of the player step size
	def goForward( self, tileSize ):
		self.movement[0] = front
		self.movement[1] = tileSize
		self.orientation = front
		self.ghost = self.ghost.move( 0, self.step )
	
	# send the character towards the back
	# tile size should be a multiple of the player step size
	def goBackward( self, tileSize ):
		self.movement[0] = back
		self.movement[1] = tileSize
		self.orientation = back
		self.ghost = self.ghost.move( 0, -self.step )
	
	# updates the character's position to move along its current trajectory
	# returns whether the character moved
	def update( self ):
		# if the character has a movement to finish
		if self.movement[1] > 0:
			
			dx = 0
			dy = 0
			
			if self.movement[0] == front:
				dy = self.step
			elif self.movement[0] == back:
				dy = - self.step
			elif self.movement[0] == left:
				dx = - self.step
			elif self.movement[0] == right:
				dx = self.step
			
			self.move( dx, dy )
			
			self.movement[1] -= self.step
			
			# adjust ghost if there's more movement
			if self.movement[1] > 0:
				if self.movement[0] == front:
					self.ghost = self.rect.move( 0, self.step )
				elif self.movement[0] == back:
					self.ghost = self.rect.move( 0, -self.step )
				elif self.movement[0] == left:
					self.ghost = self.rect.move( -self.step, 0 )
				elif self.movement[0] == right:
					self.ghost = self.rect.move( self.step, 0 )
			
			return True
		else:
			return False
	
	# determines whether this character is about to collide with the given Thing,
	# based on the character's movement
	# if they will collide, the character's movement is halted
	# returns whether a collision was detected
	def collide( self, other ):
		# if the character is about to move
		if self.movement[1] > 0:
			if self.ghost.colliderect( other.getRect() ):
				if self.movement[0] == front:
					self.movement[1] = 0
					self.ghost = self.rect.copy()
					# print 'collided with the top!'
					return True
				elif self.movement[0] == back:
					self.movement[1] = 0
					self.ghost = self.rect.copy()
					# print 'collided with the bottom!'
					return True
				elif self.movement[0] == left:
					self.movement[1] = 0
					self.ghost = self.rect.copy()
					# print 'collided with the right!'
					return True
				elif self.movement[0] == right:
					self.movement[1] = 0
					self.ghost = self.rect.copy()
					# print 'collided with the left!'
					return True
			else:
				return False
	
	# setter for total HP
	def setTotalHP( self, h ):
		self.totalHP = h
	
	# setter for current HP
	def setCurrentHP( self, h ):
		self.hp = h
	
	# setter for ATK (attack) stat
	def setATK( self, a ):
		self.atk = a
	
	# setter for DFN (defense) stat
	def setDFN( self, d ):
		self.dfn = d
	
	# setter for SPD (speed) stat
	def setSPD( self, s ):
		self.spd = s
	
	# setter for ACC (accuracy) stat
	def setACC( self, a ):
		self.acc = a
	
	# setter for time stat
	def setTime( self, t ):
		self.time = t
	
	# sets all stats except for current health points (assumed to be full)
	# passed in as a list in the following order: total HP, ATK, DFN, SPD, ACC, time
	def setAllStats( self, list ):
		self.totalHP = list[0]
		self.hp = self.totalHP
		self.atk = list[1]
		self.dfn = list[2]
		self.spd = list[3]
		self.acc = list[4]
		self.time = list[5]
	
	# setter for HP growth rate
	def setHPGR( self, hg ):
		self.hpGR = hg
	
	# setter for ATK growth rate
	def setATKGR( self, ag ):
		self.atkGR = ag
	
	# setter for DFN growth rate
	def setDFNGR( self, dg ):
		self.dfnGR = dg
	
	# setter for SPD growth rate
	def setSPDGR( self, sg ):
		self.spdGR = sg
	
	# setter for ACC growth rate
	def setACCGR( self, ag ):
		self.accGR = ag
	
	# setter for all growth rates at once (in the order above)
	# passed in as a list in the following order: HP, ATK, DFN, SPD, ACC
	def setAllGR( self, ratelist ):
		self.hpGR = ratelist[0]
		self.atkGR = ratelist[1]
		self.dfnGR = ratelist[2]
		self.spdGR = ratelist[3]
		self.accGR = ratelist[4]
	
	# add a given DebuggingMethod to this character's repertoire of attacks
	def addAttack( self, aaa ):
		self.attacks.append( aaa )
	
	# level up the character, increasing all stats by the growth rate
	def levelUp( self ):
		self.level += 1
		
		# increase stats
		self.totalHP += self.hpGR
		self.atk += self.atkGR
		self.dfn += self.dfnGR
		self.spd += self.spdGR
		self.acc += self.accGR
	
	# sends the character into battle mode, with full HP, a randomized set of available attacks,
	# and orientation set to a side view
	def enterBattle( self ):
		self.showHP = True
		self.orientation = left
		
		# store exploring position, switch to battle position
		self.explorePos= self.pos[:]
		self.setPosition( self.battlePos[0], self.battlePos[1] )
		
		self.hp = self.totalHP # reset to full HP
		self.movement = [ 0, 0 ] # clear out stored movement
		
		'''FILL IN CODE HERE FOR CHOOSING AVAILABLE ATTACKS AFTER CODING DEBUGGINGMETHODS'''
	
	# takes the character out of battle mode
	def leaveBattle( self ):
		self.showHP = False
		self.setPosition( self.explorePos[0], self.explorePos[1] )
	
	# draws the character at its current position on the given Surface
	# if it is in battle mode, it has a health bar
	def draw( self, screen ):
		# determine which image to use based on current orientation
		if self.orientation == front:
			self.image = self.imgFront
		elif self.orientation == back:
			self.image = self.imgBack
		elif self.orientation == left:
			self.image = self.imgLeft
		elif self.orientation == right:
			self.image = self.imgRight
		
		# pygame.draw.rect( screen, (215, 200, 255), self.ghost ) # for seeing where the ghost is
		
		Character.draw( self, screen )
	
	# returns a string reporting all attacks the character has
	def listAttacks( self ):
		s = 'attacks for ' + self.name + ':'
		
		for attack in self.attacks:
			s += '\n  ' + attack.name
			
		return s
	
	# returns a string reporting the stats of the character
	def reportStats( self ):
		s = 'stats for ' + self.name + ':'
		s += '\n  HP (health points) ' + str( self.hp ) + '/' + str( self.totalHP )
		s += '\n  ATK (attack) ' + str( self.atk )
		s += '\n  DFN (defense) ' + str( self.dfn )
		s += '\n  SPD (speed) ' + str( self.spd )
		s += '\n  ACC (accuracy) ' + str( self.acc )
		s += '\n  time ' + str( self.time )
		return s
	
	def reportGrowthRates( self ):
		s = 'growth rates for ' + self.name + ':'
		s += '\n  HP (health points) ' + str( self.hpGR )
		s += '\n  ATK (attack) ' + str( self.atkGR )
		s += '\n  DFN (defense) ' + str( self.dfnGR )
		s += '\n  SPD (speed) ' + str( self.spdGR )
		s += '\n  ACC (accuracy) ' + str( self.accGR )
		s+= '\non every level-up, these amounts are added to the respective stats'
		return s
	
	# returns a string reporting the name and location of the character
	def toString( self ):
		return 'playable character ' + self.name + ' at (' + str( self.pos[0] ) + ', ' + str( self.pos[1] ) + ')'	

'''main function for testing'''
def main():
	
	# ---------copied from tutorial for initializing pyGame, making a screen
	
	# initialize pygame
	pygame.init()

	# initialize the fonts
	try:
		pygame.font.init()
	except:
		print "Fonts unavailable"
		sys.exit()
	
	# create a screen (width, height)
	screenSize = (800, 600)
	screen = pygame.display.set_mode( screenSize )
	
	pygame.display.set_caption( "shalala ... la de da" )
	
	print 'init screen'
	
	# ----------test code
	
	pos = [ 0, 0 ]
	wump = pygame.image.load( "wumpus.png" ).convert_alpha() # has to be called after pygame is initialized
	hunterL = pygame.image.load( "hunterL.png" ).convert_alpha()
	hunterR = pygame.image.load( "hunterR.png" ).convert_alpha()
	hunterF = pygame.image.load( "hunterF.png" ).convert_alpha()
	hunterB = pygame.image.load( "hunterB.png" ).convert_alpha()
	
	# section of code to test Thing class
	
	'''
	agnes = Thing( pos, wump )
	print agnes.toString()
	print 'agnes is at', agnes.getPosition()
	agnes.setPosition( 300, 200 )
	print 'agnes moves to', agnes.getPosition()
	
	screen.fill( (255, 255, 255) )
	agnes.draw( screen )
	pygame.display.update()
	
	raw_input( 'show next pos? type anything\n' )
	
	screen.fill( (255, 255, 255) )
	agnes.move( 100, -100 )
	agnes.draw( screen )
	pygame.display.update()
	'''
	
	# section of code to test Character class
	'''
	edna = Character( pos, wump, 'edna' )
	print edna.toString()
	print 'edna is at', edna.getPosition()
	edna.setPosition( 100, 200 )
	print 'edna moves to', edna.getPosition()
	
	screen.fill( (255, 255, 255) )
	edna.draw( screen )
	pygame.display.update()
	
	raw_input( 'give damage? type anything\n' )
	
	edna.takeDamage( 500 )
	print 'after an attack, edna is', edna.toString()
	
	screen.fill( (255, 255, 255) )
	edna.draw( screen )
	pygame.display.update()
	'''
	
	# section of code to test Enemy class
	'''
	edna = Enemy( pos, wump, 'edna' )
	print edna.toString()
	print 'edna is at', edna.getPosition()
	edna.setPosition( 100, 200 )
	print 'edna moves to', edna.getPosition()
	
	screen.fill( (255, 255, 255) )
	edna.draw( screen )
	pygame.display.update()
	
	raw_input( 'give damage? type anything\n' )
	
	edna.takeDamage( 500 )
	print 'after an attack, edna is', edna.toString()
	
	screen.fill( (255, 255, 255) )
	edna.draw( screen )
	pygame.display.update()
	'''
	
	# section of code to test PlayableCharacter class
	
	tempRect = pygame.Surface( ( 200, 200 ) )
	tempRect.fill( ( 255, 200, 255 ) )
	edna = Enemy( pos, tempRect, 'edna' )
	edna.setPosition( 100, 200 )
	
	# make image list
	imglist = [ hunterF, hunterB, hunterL, hunterR, hunterL ]
	priya = PlayableCharacter( pos, imglist, 'priya' )
	print 'priya bounds', priya.getBounds()
	'''
	print priya.toString()
	print 'initial', priya.reportStats()
	print 'initial', priya.reportGrowthRates()
	
	print '\nmodifying stats'
	priya.setTotalHP( 800 )
	priya.setCurrentHP( 500 )
	priya.setATK( 600 )
	priya.setDFN( 750 )
	priya.setSPD( 5 )
	priya.setACC( 9001 )
	priya.setTime( 24 )
	print 'becomes', priya.reportStats()
	
	print '\nmodifying stats to step up by 100s'
	priya.setAllStats( ( 100, 200, 300, 400, 500, 600 ) )
	print 'becomes', priya.reportStats()
	
	print '\nmodifying growth rates'
	priya.setHPGR( 50 )
	priya.setATKGR( 87 ) # Charles
	priya.setDFNGR( 63 ) # Zena
	priya.setSPDGR( 27 ) # Fatimah
	priya.setACCGR( 44 ) # Melody
	print 'becomes', priya.reportGrowthRates()
	
	print '\nmodifying growth rates to step up by 10s'
	priya.setAllGR( ( 10, 20, 30, 40, 50 ) )
	print 'becomes', priya.reportGrowthRates()
	
	priya.levelUp()
	print '\nafter leveling up,', priya.reportStats()
	'''
	# testing graphics for PlayableCharacter
	
	priya.move( 20, 40 )
	print 'new priya bounds', priya.getBounds()
	
	priya.setPosition( 400, 200 )
	print 'new priya bounds', priya.getBounds()
	
	screen.fill( (255, 255, 255) )
	edna.draw( screen )
	priya.draw( screen )
	pygame.display.update()
	
	# # # TEST ADDATTACK AFTER WRITING DEBUGGINGMETHOD
	
	# ----------main loop for window
	
	print 'enter main loop'
	
	battleMode = False
	tileSize = 50
	
	while 1:
		for event in pygame.event.get(): # does not account for holding down keys
			if event.type == pygame.KEYDOWN:
				if not battleMode:
					if event.key == pygame.K_UP:
						priya.goBackward( tileSize )
					elif event.key == pygame.K_DOWN:
						priya.goForward( tileSize )
					elif event.key == pygame.K_LEFT:
						priya.goLeft( tileSize )
					elif event.key == pygame.K_RIGHT:
						priya.goRight( tileSize )
				
				if event.key == pygame.K_b:
					if battleMode:
						battleMode = False
						priya.leaveBattle()
					else:
						battleMode = True
						priya.enterBattle()
				elif event.key == pygame.K_a:
					if battleMode:
						priya.attack( edna, 50 )
						#print 'attack! edna health', edna.hp
				elif event.key == pygame.K_z:
					if battleMode:
						edna.attack( priya, 50 )
						#print 'attack! priya health', priya.hp
			if event.type == pygame.QUIT:
				sys.exit()
		
		priya.collide( edna ) # test for collision with edna
		priya.update()
		
		screen.fill( (255, 255, 255) )
		edna.draw( screen )
		priya.draw( screen )
		pygame.display.update()
		
		
	
	
# 	while 1:
# 		for event in pygame.event.get():
# 			if event.type == pygame.QUIT:
# 				sys.exit()

if __name__ == '__main__':
	main()


