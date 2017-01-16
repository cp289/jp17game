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

# fills screen with the given battle background
def loadBattleBG( screen, bg ):
	screen.blit( bg, ( 0, 0 ) )

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
	
	# create a game clock
	gameClock = pygame.time.Clock()
	
	# create a screen (width, height)
	screenSize = (750, 750)
	screen = pygame.display.set_mode( screenSize )
	scale = float( screenSize[0] ) / 4050
	
	pygame.display.set_caption( "debugDavis()" )
	
	print 'init screen'
	
	# ---------
	
	# load images
	hunterL = pygame.image.load( "melStandLeft.png" ).convert_alpha()
	hunterR = pygame.image.load( "melStandRight.png" ).convert_alpha()
	hunterF = pygame.image.load( "melStandFront.png" ).convert_alpha()
	hunterB = pygame.image.load( "melStandBack.png" ).convert_alpha()
	bug1 = pygame.image.load( "bug1.png" ).convert_alpha()
	bgOrig = pygame.image.load( "Davis Robotics Lab.png" ).convert_alpha()
	bg = pygame.transform.scale( bgOrig, screenSize )
	
	# initialize player
	initpos = ( 300, 400 ) # hopefully the middle of the bottom
	battlePos = ( 600, 100 )
	imglist = [ hunterF, hunterB, hunterL, hunterR, hunterL ]
	player = agents.PlayableCharacter( initpos, battlePos, imglist, 'player' )
	
	# initialize stage
	stage = Stage( 1, bg )
	#orion = agents.Thing( ( 500, 300 ), octopus )
	#tyrion = agents.Thing( ( 200, 100 ), table )
	#stage.addThing( orion )
	#stage.addThing( tyrion )
	
	lWall = pygame.Surface( ( 5, screenSize[1] ) )
	lWall.set_alpha( 0 ) # set image transparency
	leftWall = agents.Thing( ( -5, 0 ), lWall )
	stage.addThing( leftWall )
	
	rWall = pygame.Surface( ( 5, screenSize[1] ) )
	rWall.set_alpha( 0 ) # set image transparency
	rightWall = agents.Thing( ( screenSize[0], 0 ), rWall )
	stage.addThing( rightWall )
	
	tWall = pygame.Surface( ( screenSize[0], 207 ) )
	tWall.set_alpha( 0 ) # set image transparency
	topWall = agents.Thing( ( 0, 0 ), tWall )
	stage.addThing( topWall )
	
	bWall = pygame.Surface( ( screenSize[0], 5 ) )
	bWall.set_alpha( 0 ) # set image transparency
	bottomWall = agents.Thing( ( 0, screenSize[1] ), bWall )
	stage.addThing( bottomWall )
	
	lTableDim = ( int( 700 * scale ), int( 1040 * scale ) )
	lTablePos = ( int( 960 * scale ), int( 860 * scale ) )
	lTable = pygame.Surface( lTableDim )
	#lTable.fill( ( 100, 100, 50 ) )
	lTable.set_alpha( 0 ) # set image transparency
	leftTable = agents.Thing( lTablePos, lTable )
	stage.addThing( leftTable )
	
	rTableDim = ( int( 700 * scale ), int( 1040 * scale ) )
	rTablePos = ( int( 2400 * scale ), int( 860 * scale ) )
	rTable = pygame.Surface( rTableDim )
	#rTable.fill( ( 100, 100, 50 ) )
	rTable.set_alpha( 0 ) # set image transparency
	rightTable = agents.Thing( rTablePos, rTable )
	stage.addThing( rightTable )
	
	iboardDim = ( int( 380 * scale ), int( 1100 * scale ) )
	iboardPos = ( int( 100 * scale ), int( 2100 * scale ) )
	iboard = pygame.Surface( iboardDim )
	#iboard.fill( ( 100, 100, 50 ) )
	iboard.set_alpha( 0 ) # set image transparency
	board = agents.Thing( iboardPos, iboard )
	stage.addThing( board )
	
	bTableDim = ( int( 790 * scale ), int( 485 * scale ) )
	bTablePos = ( int( 925 * scale ), int( 3085 * scale ) )
	bTable = pygame.Surface( bTableDim )
	#bTable.fill( ( 100, 100, 50 ) )
	bTable.set_alpha( 0 ) # set image transparency
	bottomTable = agents.Thing( bTablePos, bTable )
	stage.addThing( bottomTable )
	
	lCouchDim = ( int( 785 * scale ), int( 480 * scale ) )
	lCouchPos = ( int( 2670 * scale ), int( 2530 * scale ) )
	lCouch = pygame.Surface( lCouchDim )
	#lCouch.fill( ( 100, 100, 50 ) )
	lCouch.set_alpha( 0 ) # set image transparency
	leftCouch = agents.Thing( lCouchPos, lCouch )
	stage.addThing( leftCouch )
	
	rCouchDim = ( int( 610 * scale ), int( 1080 * scale ) )
	rCouchPos = ( int ( 3440 * scale ), int( 1920 * scale ) )
	rCouch = pygame.Surface( rCouchDim )
	#rCouch.fill( ( 100, 100, 50 ) )
	rCouch.set_alpha( 0 ) # set image transparency
	rightCouch = agents.Thing( rCouchPos, rCouch )
	stage.addThing( rightCouch )
	
	battleBG = pygame.Surface( screenSize )
	battleBG.fill( ( 100, 100, 120 ) )
	
	# ----------not for stage, but for the game as a whole
	
	# create a font
	afont = pygame.font.SysFont( "Helvetica", 44, bold=True )
	
	# render a surface with some text
	text = none
	win = afont.render( "YOU WIN", True, ( 255, 255, 255 ) )
	lose = afont.render( "YOU LOSE", True, ( 255, 255, 255 ) )
	
	# ----------main loop for window
	
	print 'enter main loop'
	
	stage.draw( screen )
	player.draw( screen )
	pygame.display.update()
	
	tileSize = 50
	#enemies = pygame.sprite.RenderUpdates() # subclass of Group that allows for more efficient rendering
	edna = None
	
	battleMode = False
	moved = False
	endGame = False
	
	refresh = []
	
	while 1:
		
		if endGame:
			break
		
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN: # for initial key presses
				if not battleMode:
					if event.key == pygame.K_UP:
						player.goBackward( tileSize )
						moved = True
					elif event.key == pygame.K_DOWN:
						player.goForward( tileSize )
						moved = True
					elif event.key == pygame.K_LEFT:
						player.goLeft( tileSize )
						moved = True
					elif event.key == pygame.K_RIGHT:
						player.goRight( tileSize )
						moved = True
					elif event.key == pygame.K_b:
						battleMode = True
						loadBattleBG( screen, battleBG )
						player.enterBattle()
						#enemies.add( agents.Enemy( ( 400, 400 ), bug1, 'edna' ) )
						edna = agents.Enemy( ( 100, 200 ), bug1, 'edna' )
						print 'enter battle'
				else:
					if event.key == pygame.K_b:
						battleMode = False
						stage.fillBG( screen, refresh )
						player.leaveBattle()
						#refresh.append( player.getRect() )
						#enemies.empty()
						edna = None
						print 'leave battle'
					elif event.key == pygame.K_a:
						player.attack( edna, 50 )
						print 'attack edna!'
						
						if edna.isDead():
							print 'you win!'
							text = win
							endGame = True
					elif event.key == pygame.K_z:
						edna.attack( player, 50 )
						print 'attack player!'
						
						if player.isDead():
							print 'you lose!'
							text = lose
							endGame = True
			if event.type == pygame.QUIT:
				sys.exit()
		
		if not battleMode:
			# for when the key is held down
			keysdown = pygame.key.get_pressed()
			if keysdown[pygame.K_UP]:
				player.goBackward( tileSize )
			if keysdown[pygame.K_DOWN]:
				player.goForward( tileSize )
			if keysdown[pygame.K_LEFT]:
				player.goLeft( tileSize )
			if keysdown[pygame.K_RIGHT]:
				player.goRight( tileSize )
		
			stage.collide( player ) # stop movement if it leads to collision
				#print 'collided!'
			
			tempRect = player.getRect()
			player.update()
			if moved: # if player moved, update those parts of the screen
				#print 'moving player'
				stage.fillBG( screen, refresh, tempRect )
				#print 'erasing rect:', tempRect
				refresh.append( player.getRect() )
		
		if edna != None:
			edna.draw( screen )
			refresh.append( edna.getRect() )
		player.draw( screen )
		
		if endGame:
			screen.blit( text, ( screenSize[0] / 3, screenSize[1] / 2 ) )
		
		pygame.display.update( refresh )
		
		# clear out the refresh rects
		refresh = []
		
		# throttle the game speed to 30fps
		gameClock.tick(30)
	
	print 'end game'
	
	# after game end, keep screen until user closes window
	while 2:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()
	
if __name__ == '__main__':
	test()



