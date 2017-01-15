# Melody Mao
# CS269, January 2017
# Debug Davis (temporary title)

# main.py
# This file defines the Stage and Game classes.
# It also contains the top-level code for the game, in a main function.

# to run, call like this:
# main.py

import pygame
import sys
import agents
import random

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
	# returns whether a collision was detected
	def collide( self, chara ):
		collided = False
		
		for thing in self.contents:
			if chara.collide( thing ):
				collided = True
		
		return collided
	
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

'''
This class represents a single game.
It stores the current stage and other top-level game state objects.
'''
class Game:
	
	# fields: current stage, whether in battle mode, whether in dialogue, enemies
	
	# start a new Game on stage 1
	def __init__( self ):
		# create a screen (width, height)
		self.screenSize = (750, 750)
		self.screen = pygame.display.set_mode( self.screenSize )
		self.scale = float( self.screenSize[0] ) / 4050 # may be obsolete later when we have the camera thing working
		# scale assumes window is square
		
		pygame.display.set_caption( "debugDavis()" )
		
		print 'init screen'
		self.refresh = [] # list of rectangles that currently should be updated in the display
		self.tileSize = 50
		
		# game clock
		self.gameClock = pygame.time.Clock()
		
		# boolean fields for game state
		self.inBattle = False
		self.inDialogue = False
		self.onStatScreen = False
		
		self.player = self.initPlayer()
		
		# start out with no enemies, because not in battle
		#self.enemies = pygame.sprite.RenderUpdates()
		self.enemies = []
		self.bugImgs = [ pygame.image.load( "images/bug1.png" ).convert_alpha(),
						 pygame.image.load( "images/bug2.png" ).convert_alpha(),
						 pygame.image.load( "images/bug3.png" ).convert_alpha(),
						 pygame.image.load( "images/bug4.png" ).convert_alpha(),
						 pygame.image.load( "images/bug5.png" ).convert_alpha(),
						 pygame.image.load( "images/bug6.png" ).convert_alpha()
						]
		
		self.stage = None # set by calling the stage-loading methods
		
		# load specific screen backgrounds
		self.statBG = pygame.image.load( 'images/statScreenBG.png' ).convert_alpha()
		self.statBGRect = pygame.Rect( ( 20, 20 ), ( self.screenSize[0] - 40, self.screenSize[1] - 40 ) )
		self.battleBG = pygame.Surface( self.screenSize ) # replace with an image later
		self.battleBG.fill( ( 100, 100, 120 ) )
		
	
	# returns the PlayableCharacter for the main character
	def initPlayer( self ):
		# load images
		playerL = pygame.image.load( "images/melStandLeft.png" ).convert_alpha()
		playerR = pygame.image.load( "images/melStandRight.png" ).convert_alpha()
		playerF = pygame.image.load( "images/melStandFront.png" ).convert_alpha()
		playerB = pygame.image.load( "images/melStandBack.png" ).convert_alpha()
		
		# initialize player
		initpos = ( 300, 400 ) # hopefully the middle of the bottom
		battlePos = ( 600, 100 )
		imglist = [ playerF, playerB, playerL, playerR, playerL ]
		return agents.PlayableCharacter( initpos, battlePos, imglist, 'player' )
	
	# draws game start screen
	def showStartScreen( self ):
		# create a font
		afont = pygame.font.SysFont( "Helvetica", 44, bold=True )
		
		startScreen = pygame.Surface( self.screenSize )
		startScreen.fill( ( 100, 120, 100 ) )
		startText = afont.render( 'press s to start', True, ( 255, 255, 255 ) )
	
		self.screen.blit( startScreen, ( 0, 0 ) )
		self.screen.blit( startText, ( self.screenSize[0] / 3, self.screenSize[1] / 2 ) )
		pygame.display.update()
	
	# draws the current stat screen on the game window
	def showStatScreen( self ):
		self.onStatScreen = True
		self.screen.blit( self.statBG, ( 20, 20 ), self.statBGRect )
		self.refresh.append( self.statBGRect )
	
	# sets the stored stage field to the Stage object representing stage 1 and draws it on the game screen
	def loadStage1( self ):
		bgOrig = pygame.image.load( "images/Davis Robotics Lab.png" ).convert_alpha()
		bg = pygame.transform.scale( bgOrig, self.screenSize ) # rescales the background image
		
		self.stage = Stage( 1, bg )
		
		lWall = pygame.Surface( ( 5, self.screenSize[1] ) )
		lWall.set_alpha( 0 ) # set image transparency
		leftWall = agents.Thing( ( -5, 0 ), lWall )
		self.stage.addThing( leftWall )
	
		rWall = pygame.Surface( ( 5, self.screenSize[1] ) )
		rWall.set_alpha( 0 ) # set image transparency
		rightWall = agents.Thing( ( self.screenSize[0], 0 ), rWall )
		self.stage.addThing( rightWall )
	
		tWall = pygame.Surface( ( self.screenSize[0], 207 ) )
		tWall.set_alpha( 0 ) # set image transparency
		topWall = agents.Thing( ( 0, 0 ), tWall )
		self.stage.addThing( topWall )
	
		bWall = pygame.Surface( ( self.screenSize[0], 5 ) )
		bWall.set_alpha( 0 ) # set image transparency
		bottomWall = agents.Thing( ( 0, self.screenSize[1] ), bWall )
		self.stage.addThing( bottomWall )
	
		lTableDim = ( int( 700 * self.scale ), int( 1040 * self.scale ) )
		lTablePos = ( int( 960 * self.scale ), int( 860 * self.scale ) )
		lTable = pygame.Surface( lTableDim )
		#lTable.fill( ( 100, 100, 50 ) )
		lTable.set_alpha( 0 ) # set image transparency
		leftTable = agents.Thing( lTablePos, lTable )
		self.stage.addThing( leftTable )
	
		rTableDim = ( int( 700 * self.scale ), int( 1040 * self.scale ) )
		rTablePos = ( int( 2400 * self.scale ), int( 860 * self.scale ) )
		rTable = pygame.Surface( rTableDim )
		#rTable.fill( ( 100, 100, 50 ) )
		rTable.set_alpha( 0 ) # set image transparency
		rightTable = agents.Thing( rTablePos, rTable )
		self.stage.addThing( rightTable )
	
		iboardDim = ( int( 380 * self.scale ), int( 1100 * self.scale ) )
		iboardPos = ( int( 100 * self.scale ), int( 2100 * self.scale ) )
		iboard = pygame.Surface( iboardDim )
		#iboard.fill( ( 100, 100, 50 ) )
		iboard.set_alpha( 0 ) # set image transparency
		board = agents.Thing( iboardPos, iboard )
		self.stage.addThing( board )
	
		bTableDim = ( int( 790 * self.scale ), int( 485 * self.scale ) )
		bTablePos = ( int( 925 * self.scale ), int( 3085 * self.scale ) )
		bTable = pygame.Surface( bTableDim )
		#bTable.fill( ( 100, 100, 50 ) )
		bTable.set_alpha( 0 ) # set image transparency
		bottomTable = agents.Thing( bTablePos, bTable )
		self.stage.addThing( bottomTable )
	
		lCouchDim = ( int( 785 * self.scale ), int( 480 * self.scale ) )
		lCouchPos = ( int( 2670 * self.scale ), int( 2530 * self.scale ) )
		lCouch = pygame.Surface( lCouchDim )
		#lCouch.fill( ( 100, 100, 50 ) )
		lCouch.set_alpha( 0 ) # set image transparency
		leftCouch = agents.Thing( lCouchPos, lCouch )
		self.stage.addThing( leftCouch )
	
		rCouchDim = ( int( 610 * self.scale ), int( 1080 * self.scale ) )
		rCouchPos = ( int ( 3440 * self.scale ), int( 1920 * self.scale ) )
		rCouch = pygame.Surface( rCouchDim )
		#rCouch.fill( ( 100, 100, 50 ) )
		rCouch.set_alpha( 0 ) # set image transparency
		rightCouch = agents.Thing( rCouchPos, rCouch )
		self.stage.addThing( rightCouch )
		
		self.stage.draw( self.screen )
		self.player.draw( self.screen )
		pygame.display.update()
	
	# fills in the given rectangular section with the battle background
	# if no rect given, fills the entire screen
	def fillBattleBG( self, rect = None ):
		if rect == None:
			self.screen.blit( self.battleBG, ( 0, 0 ) )
		else:
			self.screen.blit( self.battleBG, rect, rect )
	
	# creates the given number of Enemies, of the given level
	def spawnEnemies( self, num, level ):
		for i in range( num ):
			# position based on index i
			pos = ( 100, i * 250 )
			img = random.choice( self.bugImgs )
			name = 'bug' + str( i )
			self.enemies.append( agents.Enemy( pos, img, name, level ) )
	
	# updates the game for one time-step (when the player is playing through a stage)
	def update( self ):
		if self.onStatScreen:
			self.updateStatScreen()
		elif self.inBattle:
			self.updateBattle()
		else:
			self.updateExplore()
		
		pygame.display.update( self.refresh )
		
		# clear out the refresh rects
		self.refresh = []
		
		# throttle the game speed to 30fps
		self.gameClock.tick(30)
		
	# parses keyboard input for exploration mode and updates screen contents
	def updateExplore( self ):
		moved = False # whether the player moved this time-step
		
		# parse keyboard/mouse input events
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN: # for initial key presses
				if event.key == pygame.K_s:
					self.onStatScreen = True
					print 'show stat screen'
					self.showStatScreen()
				
				elif event.key == pygame.K_UP:
					self.player.goBackward( self.tileSize )
					moved = True
				elif event.key == pygame.K_DOWN:
					self.player.goForward( self.tileSize )
					moved = True
				elif event.key == pygame.K_LEFT:
					self.player.goLeft( self.tileSize )
					moved = True
				elif event.key == pygame.K_RIGHT:
					self.player.goRight( self.tileSize )
					moved = True
				
				elif event.key == pygame.K_b:
					# update display for background
					self.fillBattleBG()
					self.refresh.append( self.screen.get_rect() )
					
					self.inBattle = True
					self.player.enterBattle()
					
					self.spawnEnemies( 3, 1 ) # 3 enemies of level 1
					print 'enter battle'
			
			if event.type == pygame.QUIT:
				sys.exit()
		
		# for when the key is held down
		keysdown = pygame.key.get_pressed()
		if keysdown[pygame.K_UP]:
			self.player.goBackward( self.tileSize )
			moved = True
		elif keysdown[pygame.K_DOWN]:
			self.player.goForward( self.tileSize )
			moved = True
		elif keysdown[pygame.K_LEFT]:
			self.player.goLeft( self.tileSize )
			moved = True
		elif keysdown[pygame.K_RIGHT]:
			self.player.goRight( self.tileSize )
			moved = True
	
		self.stage.collide( self.player ) # stop movement if it leads to collision
			#print 'collided!'
		
		# update screen contents
		
		tempRect = self.player.getRect()
		walked = self.player.update()
		if moved or walked: # if player moved, update those parts of the screen
			#print 'moving player'
			self.stage.fillBG( self.screen, self.refresh, tempRect )
			self.refresh.append( self.player.getRect() )
		
		self.player.draw( self.screen )
		self.refresh.append( self.player.getRect() )
	
	# parses keyboard input for battle mode and updates screen contents
	def updateBattle( self ):
		attackedEnemy = False
		attackedPlayer = False
		
		# parse keyboard/mouse input events
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN: # for initial key presses
				if event.key == pygame.K_s: # show stat screen
					self.onStatScreen = True
					print 'show stat screen'
					self.showStatScreen()
				
				elif event.key == pygame.K_b: # leave battle
					self.inBattle = False
					self.stage.fillBG( self.screen, self.refresh )
					self.player.leaveBattle()
					self.enemies = [] # empty enemies list
					print 'leave battle'
				
				elif event.key == pygame.K_a:
					self.player.attack( self.enemies[0], 50 )
					print 'attack edna!'
					
					if self.enemies[0].isDead():
						print 'you win!'
				elif event.key == pygame.K_z:
					self.enemies[0].attack( self.player, 50 )
					print 'attack player!'
					
					if self.player.isDead():
						print 'you lose!'
			
			if event.type == pygame.QUIT:
				sys.exit()
		
		# update screen contents
		for edna in self.enemies:
			edna.draw( self.screen )
			self.refresh.append( edna.getRect() )
		
		self.player.draw( self.screen )
		self.refresh.append( self.player.getRect() )
	
	# parses keyboard input for stat screen mode and updates screen contents
	def updateStatScreen( self ):
		# parse keyboard/mouse input events
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN: # for initial key presses
				if event.key == pygame.K_s:
					self.onStatScreen = False
					print 'leave stat screen'
					
					if self.inBattle: # redraw battle screen
						self.fillBattleBG( self.statScreenRect )
						self.refresh.append( self.statScreenRect )
					else: # redraw stage
						self.stage.fillBG( self.screen, self.refresh, self.statScreenRect)
			
			if event.type == pygame.QUIT:
				sys.exit()

# runs main game code
def main():
	# initialize pygame
	pygame.init()

	# initialize the fonts
	try:
		pygame.font.init()
	except:
		print "Fonts unavailable"
		sys.exit()
	
	# init game
	game = Game()
	game.showStartScreen()
	
	# run a loop for start screen
	moveOn = False
	while not moveOn:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_s:
					print 'leave start screen'
					moveOn = True
			if event.type == pygame.QUIT:
				sys.exit()
	
	print 'enter stage 1'
	game.loadStage1()
	
	# run a loop with the first stage
	while 1:
		game.update()
	'''put the above loop inside another loop for while the stage is not finished'''
	
	# when that loop is done, load stage 2
	
	# etc
	
	# exit option for end screen?
	
	# after game end, keep screen until user closes window
	while 2:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

if __name__ == '__main__':
	main()