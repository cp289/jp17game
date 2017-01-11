# Melody Mao
# CS269, January 2017
# Debug Davis (temporary title)

# testmain.py
# This file defines the Stage

# to run, call like this:
# testmain.py

import pygame
import sys
import agents

# some useful variables for the rest of this file
back, front, left, right, none = range( 5 )

'''
This class represents one stage/room of the game.
It stores its furniture and walls as Things.
'''
class Stage:
	
	# fields: number battles to win, background image, list of Thing contents, Surface screen
	
	# creates a new Stage with the given number of battles to win and background image
	def __init__( self, numBattles, bg ):
		self.numBattles = numBattles
		self.background = bg
		#self.contents = [] # initialize list of Thing contents as empty
		self.contents = pygame.sprite.Group()
	
	# add a wall or of piece of furniture to the stage
	def addThing( self, thing ):
		self.contents.add( thing )
	
	# halts the given Character's movement if they are about to collide with anything in this Stage
	def collide( self, chara ):
		for thing in self.contents:
			chara.collide( thing )
	
	# draws the Stage and its contents on the given Surface
	def draw( self, screen ):
		screen.blit( self.background, ( 0, 0 ) )
		self.contents.draw( screen )
	
	# draws the subsection of the stage background within the given rectangle
	def fillBG( self, screen, refresh, rect = None ):
		# draw the entire screen
		if ( rect == None ):
			# now draw the surfaces to the screen using the blit function
			screen.blit( self.background, ( 0, 0 ) )
		
			refresh.append( screen.get_rect() )
	
		# draw a specific section
		else:
			screen.blit( self.background, rect, rect )
		
			refresh.append( rect )
	
class Game:
	
	# fields: current stage, whether in battle mode, whether in dialogue, enemies
	
	# start a new Game on stage 1
	def __init__( self ):
		# boolean fields for game state
		self.inBattle = False
		self.inDialogue = False
		
		self.stage = self.loadStage1()
		
		# start out with no enemies, because not in battle
		self.enemies = pygame.sprite.RenderUpdates()
		
	
	# returns the Stage object representing stage 1
	def loadStage1( self ):
		
		
		return

# loadStage( stage ): load first background, initial player position
# spawnEnemy

def test():
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
	
	pygame.display.set_caption( "shooosh:doof" )
	
	print 'init screen'
	
	# ---------
	
	# load images
	wump = pygame.image.load( "wumpus.png" ).convert_alpha() # has to be called after pygame is initialized
	hunterL = pygame.image.load( "hunterL.png" ).convert_alpha()
	hunterR = pygame.image.load( "hunterR.png" ).convert_alpha()
	hunterF = pygame.image.load( "hunterF.png" ).convert_alpha()
	hunterB = pygame.image.load( "hunterB.png" ).convert_alpha()
	tableOrig = pygame.image.load( "table.png" ).convert_alpha()
	table = pygame.transform.scale( tableOrig, ( 205, 180 ) )
	octopusOrig = pygame.image.load( "octopus.png" ).convert_alpha()
	octopus = pygame.transform.scale( octopusOrig, ( 151, 180 ) )
	bgOrig = pygame.image.load( "orange6.png" ).convert_alpha()
	bg = pygame.transform.scale( bgOrig, screenSize )
	
	# initialize player
	initpos = ( 300, 400 ) # hopefully the middle of the bottom
	imglist = [ hunterF, hunterB, hunterL, hunterR, hunterL ]
	priya = agents.PlayableCharacter( initpos, imglist, 'priya' )
	
	# initialize stage
	stage = Stage( 1, bg )
	orion = agents.Thing( ( 500, 300 ), octopus )
	tyrion = agents.Thing( ( 200, 100 ), table )
	stage.addThing( orion )
	stage.addThing( tyrion )
	
	# ----------main loop for window
	
	print 'enter main loop'
	
	stage.draw( screen )
	priya.draw( screen )
	pygame.display.update()
	
	battleMode = False
	tileSize = 50
	
	refresh = []
	
	while 1:
		
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN: # for initial key presses
				if not battleMode:
					if event.key == pygame.K_UP:
						priya.goBackward( tileSize )
					elif event.key == pygame.K_DOWN:
						priya.goForward( tileSize )
					elif event.key == pygame.K_LEFT:
						priya.goLeft( tileSize )
					elif event.key == pygame.K_RIGHT:
						priya.goRight( tileSize )
				
# 				if event.key == pygame.K_b:
# 					if battleMode:
# 						battleMode = False
# 						priya.leaveBattle()
# 					else:
# 						battleMode = True
# 						priya.enterBattle()
# 				elif event.key == pygame.K_a:
# 					if battleMode:
# 						priya.attack( edna, 50 )
# 				elif event.key == pygame.K_z:
# 					if battleMode:
# 						edna.attack( priya, 50 )
			if event.type == pygame.QUIT:
				sys.exit()
		
		# for when the key is held down
		if not battleMode:
			keysdown = pygame.key.get_pressed()
			if keysdown[pygame.K_UP]:
				priya.goBackward( tileSize )
			if keysdown[pygame.K_DOWN]:
				priya.goForward( tileSize )
			if keysdown[pygame.K_LEFT]:
				priya.goLeft( tileSize )
			if keysdown[pygame.K_RIGHT]:
				priya.goRight( tileSize )
		
		stage.collide( priya ) # stop movement if it leads to collision
		
		tempRect = priya.getRect()
		if priya.update(): # if priya moved, update those parts of the screen
			stage.fillBG( screen, refresh, tempRect )
			refresh.append( priya.getRect() )
		
		priya.draw( screen )
		pygame.display.update( refresh )
		
		# clear out the refresh rects
		refresh = []
	
	
if __name__ == '__main__':
	test()



