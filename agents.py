# Melody Mao
# CS269, January 2017
# Debug Davis (temporary title)

# agents.py
# This file defines the Thing class and its child classes.
# The Thing class extends the pygame Sprite class, so that it can be handled in Groups.
# The position of an Thing is the upper left corner of its image/rect.
# Playable Characters increase their stats with every level-up.

# test code is now obsolete

import pygame
import sys
import random

# some useful variables for the rest of this file
back, front, left, right, none = range( 5 )
green = ( 150, 255, 150 )
red = ( 255, 150, 150 )
black = ( 0, 0, 0 )
bluegreen = ( 150, 170, 170 )

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
	def __init__( self, pos, img, name ):
		Thing.__init__( self, pos, img ) # call parent constructor
		
		self.name = name
		self.totalHP = 400
		self.hp = self.totalHP
		self.showHP = False
		self.level = 1
		
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
	
	# draws the Character with a health bar at its current position on the given Surface
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
	def __init__( self, pos, img, name, level ):
		Character.__init__( self, pos, img, name ) # call parent constructor
		self.showHP = True # Enemies only appear in battle, so always show HP
		self.level = level
		self.selected = False
		
		# initialize stats by taking level 1 value and adding randomly generated level-ups
		# to it based on the Enemy's level
		factor = level - 1 # how levels to increase stats by
		self.hp = 400 + int( random.random() * 50 * factor )
		self.atk = 50 + int( random.random() * 5 * factor )
		self.dfn = 50 + int( random.random() * 5 * factor )
		self.spd = 50 + int( random.random() * 5 * factor )
		self.acc = 50 + int( random.random() * 5 * factor )
	
	# returns a string indicating the type of Character
	def getType( self ):
		return 'Enemy'
	
	# sets this Enemy to be selected
	def select( self ):
		self.selected = True
	
	# sets this Enemy to be unselected
	def deselect( self ):
		self.selected = False
	
	# draws the Enemy at its current position on the given Surface
	def draw( self, screen ):
		Character.draw( self, screen ) # call parent method
		
		# draw pointer if selected
		if self.selected:
			radius = 10
			arrowPos = ( self.rightEdge - radius, self.bottomEdge - radius )
			arrowBottom = ( self.rightEdge - radius, self.bottomEdge + radius + 1 )
			arrowRight = ( self.rightEdge + radius + 1, self.bottomEdge - radius )
			points = [ arrowPos, arrowBottom, arrowRight ]
			
			pygame.draw.polygon( screen, black, points )
			
			inRadius = 9
			innerPos = ( self.rightEdge - inRadius, self.bottomEdge - inRadius )
			innerBottom = ( self.rightEdge - inRadius, self.bottomEdge + inRadius )
			innerRight = ( self.rightEdge + inRadius, self.bottomEdge - inRadius )
			innerPoints = [ innerPos, innerBottom, innerRight ]
			
			pygame.draw.polygon( screen, bluegreen, innerPoints )
	
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
	# all stats and growth rates are given a default value, use setAllStats and setAllGR to specialize
	def __init__( self, pos, battlePos, imglist, name, stagePos = None ):
		Character.__init__( self, pos, imglist[0], name ) # call parent constructor
		
		# self.pos is location on screen
		self.battlePos = [ battlePos[0], battlePos[1] ] # location on screen when in battle mode
		self.explorePos = [ pos[0], pos[1] ] # stores last exploring position when character goes into battle mode
		if stagePos == None:
			self.stagePos = [ pos[0], pos[1] ]
		else:
			self.stagePos = [ stagePos[0], stagePos[1] ]
		
		# initialize stats
		self.time = 6
		self.atk = 50
		self.dfn = 50
		self.spd = 50
		self.acc = 50
		self.xp = 0
		
		# initialize growth rates
		self.hpGR = 0.8
		self.atkGR = 0.8
		self.dfnGR = 0.8
		self.spdGR = 0.8
		self.accGR = 0.8
		self.statStep = 5 # how much a stat can increase in one level-up
		self.hpStep = 55 # how much HP can increase in one level-up
		
		# initialize attack list as empty
		self.attacks = [] # all attacks the character is capable of
		self.currentAttacks = [] # attacks the character can currently choose from (a subset of self.attacks)
		
		# variables for current player state
		self.orientation = front
		
		# variables for player movement
		self.movement = [ 0, 0 ] # current stored movement to follow: direction, distance left to go
		self.step = 10 # how far the character moves in one time-step, if it is currently moving
		
		# variables for ghost (collision-handling)
		self.ghostSide = self.rect.height / 3 # represents the length of one side of the ghost box
		self.ghost = pygame.Rect( ( 0, 0 ), ( self.rect.width, self.ghostSide ) ) # represents the position of the character one time-step later
		self.resetGhost()
		
		# sprite images
		self.imgFront = imglist[0]
		self.imgBack = imglist[1]
		self.imgLeft = imglist[2]
		self.imgRight = imglist[3]
		self.imgStatus = imglist[4]
		self.imgBattle = imglist[5]
	
	# returns the current position onstage of the character
	def getStagePos( self ):
		return self.stagePos[:]
	
	# returns a tuple of this character's stats, in the following order:
	# time, hp, attack, defense, speed, accuracy, xp, level
	def getStats( self ):
		return ( self.time, self.totalHP, self.atk, self.dfn, self.spd, self.acc, self.xp, self.level )
	
	# returns the status image for this character
	def getStatusIMG( self ):
		return self.imgStatus
	
	# returns a string indicating the type of Character
	def getType( self ):
		return 'PlayableCharacter'
	
	# puts the ghost directly on top of the character's current position
	def resetGhost( self ):
		newx = self.stagePos[0]
		newy = self.stagePos[1] + 2 * self.ghostSide
		self.ghost.topleft = newx, newy
	
	# change the screen position of the PlayableCharacter to the given coordinates
	def setScreenPos( self, newx, newy ):
		Character.setPosition( self, newx, newy ) # call parent method
	
	# change the stage position of the PlayableCharacter to the given coordinates
	def setStagePos( self, newx, newy ):
		self.stagePos = [ newx, newy ]
	
	# change the stage position of the PlayableCharacter by the given amounts in the x and y directions
	def move( self, dx, dy ):
		self.stagePos[0] += dx
		self.stagePos[1] += dy
	
	# send the character towards the left, updating orientation
	# tile size should be a multiple of the player step size
	def goLeft( self, tileSize ):
		self.movement[0] = left
		self.movement[1] = tileSize
		self.orientation = left
		self.resetGhost()
		self.ghost = self.ghost.move( -self.step, 0 )
	
	# send the character towards the right
	# tile size should be a multiple of the player step size
	def goRight( self, tileSize ):
		self.movement[0] = right
		self.movement[1] = tileSize
		self.orientation = right
		self.resetGhost()
		self.ghost = self.ghost.move( self.step, 0 )
	
	# send the character towards the front
	# tile size should be a multiple of the player step size
	def goForward( self, tileSize ):
		self.movement[0] = front
		self.movement[1] = tileSize
		self.orientation = front
		self.resetGhost()
		self.ghost = self.ghost.move( 0, self.step )
	
	# send the character towards the back
	# tile size should be a multiple of the player step size
	def goBackward( self, tileSize ):
		self.movement[0] = back
		self.movement[1] = tileSize
		self.orientation = back
		self.resetGhost()
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
				self.resetGhost()
				if self.movement[0] == front:
					self.ghost = self.ghost.move( 0, self.step )
				elif self.movement[0] == back:
					self.ghost = self.ghost.move( 0, -self.step )
				elif self.movement[0] == left:
					self.ghost = self.ghost.move( -self.step, 0 )
				elif self.movement[0] == right:
					self.ghost = self.ghost.move( self.step, 0 )
			
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
					self.resetGhost()
					# print 'collided with the top!'
					return True
				elif self.movement[0] == back:
					self.movement[1] = 0
					self.resetGhost()
					# print 'collided with the bottom!'
					return True
				elif self.movement[0] == left:
					self.movement[1] = 0
					self.resetGhost()
					# print 'collided with the right!'
					return True
				elif self.movement[0] == right:
					self.movement[1] = 0
					self.resetGhost()
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
	
	# increases the character's XP by the given amount
	def increaseXP( self, amt ):
		self.xp += amt
	
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
	
	# level up the character, using growth rates to determine which stats
	# will be leveled up
	# HP increases by 55 at a time, all others by 5
	def levelUp( self ):
		self.level += 1
		
		# increase stats based on growth rates
		if random.random() < self.hpGR:
			self.totalHP += self.hpStep
		
		if random.random() < self.atkGR:
			self.atk += self.statStep
		
		if random.random() < self.dfnGR:
			self.dfn += self.statStep
		
		if random.random() < self.spdGR:
			self.spd += self.statStep
		
		if random.random() < self.accGR:
			self.acc += self.statStep
	
	# sends the character into battle mode, with full HP, a randomized set of available attacks,
	# and orientation set to a side view
	def enterBattle( self ):
		self.showHP = True
		self.image = self.imgBattle
		
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
		# determine which image to use based on current orientation (only in exploration mode)
		if not self.showHP:
			if self.orientation == front:
				self.image = self.imgFront
			elif self.orientation == back:
				self.image = self.imgBack
			elif self.orientation == left:
				self.image = self.imgLeft
			elif self.orientation == right:
				self.image = self.imgRight
		
		#pygame.draw.rect( screen, (215, 200, 255), self.ghost ) # for seeing where the ghost is
		
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
		s += '\n XP ' + str( self.xp )
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




