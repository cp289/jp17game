# Melody Mao
# CS269, January 2017
# Debug Davis (temporary title)

# agents.py
# This file defines 
# The Agent class extends the pygame Sprite class, so that it can be handled in Groups.
# The position of an Agent is the upper left corner of its image/rect.

import pygame
import sys

back, front, left, right = range( 4 )

# This class represents any entity in the game that has a position on the screen,
# including both moving characters and stationary objects.
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
	

# This class represents an Enemy that can attack players and take damage.
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
	
	# change the position of the Agent to the given coordinates
	def setPosition( self, newx, newy ):
		Agent.setPosition( self, newx, newy ) # call parent class method
		
		# adjust position of health bar
		self.hpbarBG.topleft = newx, newy + self.rect.height
		self.hpbarFG.topleft = newx + 1, newy + self.rect.height + 1
		
	
	# change the position of the Agent by the given amounts in the x and y directions
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
	
	# 
	#def die( self ):
	
	# attacks the given PlayableCharacter target and does the given amount of damage
	def attack( self, target, dmg ):
		target.takeDamage( dmg )
	
	# draws the Enemy at its current position on the given Surface
	def draw( self, screen ):
		screen.blit( self.image, self.rect )
		
		# draw health bar background (in black)
		pygame.draw.rect( screen, ( 0, 0, 0 ), self.hpbarBG )
		
		# draw health bar foreground based on current HP left
		newWidth = int( ( self.hpbarWidth - 2 ) * self.hp / self.startingHP )
		self.hpbarFG.width = newWidth
		pygame.draw.rect( screen, ( 200, 255, 200 ), self.hpbarFG )
	
	# returns a string reporting the name and current HP of the Enemy
	def toString( self ):
		s = 'an Enemy named ' + self.name + ' with ' + str( self.hp ) + ' HP'
		return s

# This class represents a character that the player can control throughout the game.
# Each character has stats, and can move around in exploring mode and attack in battle mode.
class PlayableCharacter( Agent ):
	
	# fields: name, stats, growth rate, status portraits, attacks
	
	# creates a new PlayableCharacter with the given position, images, and name
	# images should be given in the following order: front, back, left, right, status
	# all images besides status portrait should be the same size
	# all stats and growth rates are given a default value
	def __init__( self, pos, imglist, name ):
		Agent.__init__( self, pos, imglist[0] ) # call parent constructor
		
		self.name = name
		
		# initialize stats
		self.totalHP = 700
		self.hp = 700
		self.atk = 700
		self.dfn = 700
		self.spd = 700
		self.acc = 700
		self.time = 5
		
		# initialize growth rates
		self.atkGR = 0.05
		self.dfnGR = 0.05
		self.spdGR = 0.05
		self.accGR = 0.05
		
		# initialize attack list as empty
		self.attacks = []
		self.currentAttacks = [] # POSSIBLY RECONSIDER THIS IMPLEMENTATION, AND HAVE A LIST OF POSSIBLE ATTACKS ELSEWHERE
		
		# variables for current player state
		self.inBattle = False
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
		
	
	
	
	# setters for all stats and growth rates
	# setter for all stats at once (in the order above)
	# setter for all growth rates at once (in the order above)
	# add attack
	# enterBattle, reset HP, choose current attacks, set orientation to side view
	# attack
	# takeDamage
	# die
	# draw method draws based on current orientation and battle state
	# toString

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
	
	# # # TEST ATTACK AFTER FINISHING PLAYABLE CHARACTER
	
	# ----------main loop for window
	
	print 'enter main loop'
	
	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

if __name__ == '__main__':
	main()


