# Melody Mao
# CS269, January 2017
# Debug Davis (temporary title)

# agents.py
# This file defines the Agent class and its child classes.
# The Agent class extends the pygame Sprite class, so that it can be handled in Groups.
# The position of an Agent is the upper left corner of its image/rect.
# Playable Characters increase their stats with every level-up.

import pygame
import sys

# some useful variables for the rest of this file
back, front, left, right = range( 4 )
green = ( 150, 255, 150 )


'''
This class represents any entity in the game that has a position on the screen,
including both moving characters and stationary objects.
'''
class Agent( pygame.sprite.Sprite ):
	
	# fields: position, image, rect
	
	# creates a new Agent at the given position
	def __init__( self, pos, img ):
		pygame.sprite.Sprite.__init__( self ) # call parent constructor
		
		self.pos = [ pos[0], pos[1] ]
		self.image = img
		
		self.rect = self.image.get_rect()
		self.rect.topleft = pos[0], pos[1]
	
	# return a clone of the position list
	def getPosition( self ):
		return self.pos[:]
	
	# change the position of the Agent to the given coordinates
	def setPosition( self, newx, newy ):
		# change position of image/rect
		self.rect.topleft = newx, newy
		
		# change pos field
		self.pos[0] = newx
		self.pos[1] = newy
	
	# change the position of the Agent by the given amounts in the x and y directions
	def move( self, dx, dy ):
		self.pos[0] += dx
		self.pos[1] += dy
		
		self.rect = self.rect.move( dx, dy )
	
	# draws the Agent at its current position on the given Surface
	def draw( self, screen ):
		screen.blit( self.image, self.rect )
	
	# returns a string reporting the position and dimensions of the Agent
	def toString( self ):
		s = 'an Agent at (' + str( self.pos[0] ) + ', ' + str( self.pos[1] ) + '), of width ' \
			+ str( self.rect.width ) + ' and height ' + str( self.rect.height )
		return s
	
'''
This class represents an Enemy that can attack players and take damage.
'''
class Enemy( Agent ):
	
	# fields: name, stats
	
	# creates a new Enemy at the given position with the given image, name,
	# and starting amount of HP
	# all stats are given a default value of 700
	def __init__( self, pos, img, name, hp = 700 ):
		Agent.__init__( self, pos, img ) # call parent constructor
		
		self.name = name
		
		# initialize stats
		self.totalHP = hp
		self.hp = hp
		self.atk = 700
		self.dfn = 700
		self.spd = 700
		self.acc = 700
		
		# rects for drawing health bar
		self.hpbarWidth = 70
		self.hpbarHeight = 10
		self.hpbarBG = pygame.Rect( ( pos[0], pos[1] + self.rect.height ), ( self.hpbarWidth, self.hpbarHeight ) )
		self.hpbarFG = pygame.Rect( ( pos[0] + 1, pos[1] + self.rect.height + 1 ),
			( self.hpbarWidth - 2, self.hpbarHeight - 2 ) )
		#print 'hpbar at', pos[0], ',', (pos[1]+ self.rect.height )
	
	# change the position of the Enemy to the given coordinates
	def setPosition( self, newx, newy ):
		Agent.setPosition( self, newx, newy ) # call parent class method
		
		# adjust position of health bar
		self.hpbarBG.topleft = newx, newy + self.rect.height
		self.hpbarFG.topleft = newx + 1, newy + self.rect.height + 1
		
	
	# change the position of the Enemy by the given amounts in the x and y directions
	def move( self, dx, dy ):
		Agent.move( self, dx, dy ) # call parent class method
		
		# adjust position of health bar
		self.hpbarBG = self.hpbarBG.move( dx, dy )
		self.hpbarFG = self.hpbarFG.move( dx, dy )
	
	# reduces the Enemy's HP by the given amount
	def takeDamage( self, amt ):
		self.hp -= amt
		
		if self.hp < 0: # if the damage would make the HP negative, just make it 0
			self.hp = 0
	
	# attacks the given PlayableCharacter target and does the given amount of damage
	def attack( self, target, dmg ):
		target.takeDamage( dmg )
	
	# 
	#def die( self ):
	'''I'm not quite sure what this does'''
	
	# draws the Enemy with a health bar at its current position on the given Surface
	def draw( self, screen ):
		screen.blit( self.image, self.rect )
		
		# draw health bar background (in black)
		pygame.draw.rect( screen, ( 0, 0, 0 ), self.hpbarBG )
		
		# draw health bar foreground based on current HP left
		newWidth = int( ( self.hpbarWidth - 2 ) * self.hp / self.startingHP )
		self.hpbarFG.width = newWidth
		pygame.draw.rect( screen, green, self.hpbarFG )
	
	# returns a string reporting the name and current HP of the Enemy
	def toString( self ):
		s = 'an Enemy named ' + self.name + ' with ' + str( self.hp ) + ' HP'
		return s

'''
This class represents a character that the player can control throughout the game.
Each character has stats, and can move around in exploring mode and attack in battle mode.
'''
class PlayableCharacter( Agent ):
	
	# fields: name, stats, growth rate, status portraits, attacks
	
	# creates a new PlayableCharacter with the given position, images, and name
	# images should be given in the following order: front, back, left, right, status
	# all images besides status portrait should be the same size
	# all stats and growth rates are given a default value
	def __init__( self, pos, imglist, name ):
		Agent.__init__( self, pos, imglist[0] ) # call parent constructor
		
		self.name = name
		self.level = 1
		
		# initialize stats
		self.totalHP = 700
		self.hp = 700
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
		self.inBattle = False # determines whether the player health bar is shown
		self.orientation = front
		
		# sprite images
		self.imgFront = imglist[0]
		self.imgBack = imglist[1]
		self.imgLeft = imglist[2]
		self.imgRight = imglist[3]
		self.imgStatus = imglist[4]
		
		# rects for drawing health bar
		self.hpbarWidth = 70
		self.hpbarHeight = 10
		self.hpbarBG = pygame.Rect( ( pos[0], pos[1] + self.rect.height ), ( self.hpbarWidth, self.hpbarHeight ) )
		self.hpbarFG = pygame.Rect( ( pos[0] + 1, pos[1] + self.rect.height + 1 ),
			( self.hpbarWidth - 2, self.hpbarHeight - 2 ) )
	
	# change the position of the Enemy to the given coordinates
	def setPosition( self, newx, newy ):
		Agent.setPosition( self, newx, newy ) # call parent class method
		
		# adjust position of health bar
		self.hpbarBG.topleft = newx, newy + self.rect.height
		self.hpbarFG.topleft = newx + 1, newy + self.rect.height + 1
		
	
	# change the position of the Enemy by the given amounts in the x and y directions
	def move( self, dx, dy ):
		Agent.move( self, dx, dy ) # call parent class method
		
		# adjust position of health bar
		self.hpbarBG = self.hpbarBG.move( dx, dy )
		self.hpbarFG = self.hpbarFG.move( dx, dy )
	
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
		print 'setting speed to', s
	
	# setter for ACC (accuracy) stat
	def setACC( self, a ):
		self.acc = a
		print 'setting accuracy to ', a
	
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
	def setACC( self, ag ):
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
		self.acc += self.self.accGR
	
	# sends the character into battle mode, with full HP, a randomized set of available attacks,
	# and orientation set to a side view
	def enterBattle( self ):
		self.inBattle = True
		self.orientation = left
		
		'''FILL IN CODE HERE AFTER CLARIFYING BATTLE FLOW'''
	
	# reduces the character's HP by the given amount
	def takeDamage( self, amt ):
		self.hp -= amt
		
		if self.hp < 0: # if the damage would make the HP negative, just make it 0
			self.hp = 0
	
	# attacks the given Enemy and does the given amount of damage
	def attack( self, target, dmg ):
		target.takeDamage( dmg )
	
	# die
	# def die()
	'''I'm not quite sure what this does'''
	
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
		
		screen.blit( self.image, self.rect )
		
		# only display health bar if player is in battle
		if self.inBattle:
			# draw health bar background (in black)
			pygame.draw.rect( screen, ( 0, 0, 0 ), self.hpbarBG )
		
			# draw health bar foreground based on current HP left
			newWidth = int( ( self.hpbarWidth - 2 ) * self.hp / self.startingHP )
			self.hpbarFG.width = newWidth
			pygame.draw.rect( screen, green, self.hpbarFG )
	
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
	
	# section of code to test Agent class
	'''
	
	agnes = Agent( pos, wump )
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
	edna = Enemy( pos, wump, 'edna' )
	edna.setPosition( 100, 200 )
	
	# make image list
	imglist = [ hunterF, hunterB, hunterL, hunterR, hunterL ]
	priya = PlayableCharacter( pos, imglist, 'priya' )
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
	
	
	
	
	# # # TEST ATTACK AFTER FINISHING PLAYABLE CHARACTER
	
	# ----------main loop for window
	
	print 'enter main loop'
	
	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

if __name__ == '__main__':
	main()


