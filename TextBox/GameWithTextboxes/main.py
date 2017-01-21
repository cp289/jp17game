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
import conversation

# some useful variables for the rest of this file
back, front, left, right, none = range( 5 )
green = ( 150, 180, 160 )
white = ( 255, 255, 255 )

'''
This class represents one stage/room of the game.
It stores its furniture and walls as Things.
'''
class Stage:
	
	# fields: number battles to win, background image, list of Thing contents, Surface screen
	
	# creates a new Stage with the given number of battles to win and background image
	def __init__( self, numBattles, bg, battleBG ):
		self.numBattles = numBattles
		self.battlesCompleted = 0
		self.background = bg
		self.battleBG = battleBG
		#self.contents = [] # initialize list of Thing contents as empty
		self.contents = pygame.sprite.Group()
	
	# add a wall or of piece of furniture to the stage
	def addThing( self, thing ):
		self.contents.add( thing )
	
	# add 1 to the number of battles completed in this stage
	def addBattle( self ):
		self.battlesCompleted += 1
	
	# returns whether this stage has been completed
	def completed( self ):
		return self.numBattles == self.battlesCompleted
	
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
	
	# fills in the given rectangular section of the given screen with the battle background
	# if no rect given, fills the entire screen
	def fillBattleBG( self, screen, rect = None ):
		if rect == None:
			screen.blit( self.battleBG, ( 0, 0 ) )
		else:
			screen.blit( self.battleBG, rect, rect )

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
		
		self.mel = None
		self.fa = None
		self.zen = None
		self.cha = None
		self.initPlayers()
		self.player = self.mel
		
		# variables for battle mode
		self.battleParticipants = [] # list to loop through for battle turns
		self.currentBattleTurn = -1 # stores index of current turn within battleParticipants
		self.livePlayers = [] # stores players who are currently alive so that enemies can choose targets easily
		self.storedPoints = 0 # amount of XP all live players will gain on winning
		
		self.bugImgs = [ pygame.image.load( "images/bug1.png" ).convert_alpha(),
						 pygame.image.load( "images/bug2.png" ).convert_alpha(),
						 pygame.image.load( "images/bug3.png" ).convert_alpha(),
						 pygame.image.load( "images/bug4.png" ).convert_alpha(),
						 pygame.image.load( "images/bug5.png" ).convert_alpha(),
						 pygame.image.load( "images/bug6.png" ).convert_alpha()
						]
		self.enemies = []
		self.selectedEnemyIDX = -1 # index of current selected enemy
		
		self.stage = None # set by calling the methods for entering stages
		self.stage1 = None # these three are created when the loading methods are called
		self.stage2 = None
		self.stage3 = None
		
		# load specific screen backgrounds
		statBGorig = pygame.image.load( 'images/statScreenBG.png' ).convert_alpha()
		self.statBG = pygame.transform.scale( statBGorig, self.screenSize ) # force it to be square for now
		self.statBGRect = pygame.Rect( ( 20, 20 ), ( self.screenSize[0] - 40, self.screenSize[1] - 40 ) )
		
		# makes boxes for the characters on the stat screen
		offset = 20
		boxWidth = ( self.statBGRect.width - 4 * offset ) / 2
		boxHeight = ( self.statBGRect.height - 4 * offset ) / 2
		self.melBox = pygame.Rect( ( 2 * offset, 2 * offset ), ( boxWidth, boxHeight ) )
		self.faBox = pygame.Rect( ( 2 * offset, 3 * offset + boxHeight ), ( boxWidth, boxHeight ) )
		self.zenBox = pygame.Rect( ( 3 * offset + boxWidth, 2 * offset ), ( boxWidth, boxHeight ) )
		self.chaBox = pygame.Rect( ( 3 * offset + boxWidth, 3 * offset + boxHeight ), ( boxWidth, boxHeight ) )
		
		# create fonts
		self.bigFont = pygame.font.SysFont( "Helvetica", 44, bold=True )
		self.smallFont = pygame.font.SysFont( 'Helvetica', 20 )
		self.nameFont = pygame.font.SysFont( "Helvetica", 36, bold=True )
		self.convoFont = pygame.font.SysFont( "Helvetica", 30, bold=True )

		self.initConvo()
		self.convoNum = 0

	
	# creates the PlayableCharacters in the game
	def initPlayers( self ):
		# load images
		playerL = pygame.image.load( "images/melStandLeft.png" ).convert_alpha()
		playerR = pygame.image.load( "images/melStandRight.png" ).convert_alpha()
		playerF = pygame.image.load( "images/melStandFront.png" ).convert_alpha()
		playerB = pygame.image.load( "images/melStandBack.png" ).convert_alpha()
		playerS = pygame.image.load( 'images/MelodyStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/MelodyHead.png" ).convert_alpha()
		playerBattle = pygame.image.load( 'images/MelodyBattleSprite.png' ).convert_alpha()
		
		# initialize mel
		initpos = ( 300, 400 ) # hopefully the middle of the bottom
		battlePos = ( 600, 100 )
		imglist = [ playerF, playerB, playerL, playerR, playerS, playerBattle, playerC ]
		self.mel = agents.PlayableCharacter( initpos, battlePos, imglist, 'Melody')
		
		playerF = pygame.image.load( "images/FatimahBattleSprite.png" ).convert_alpha() # not actually the front picture
		playerB = None
		playerL = None
		playerR = None
		playerS = pygame.image.load( "images/FatimahStatPic.png" ).convert_alpha()
		playerC = pygame.image.load( "images/FatimahHead.png" ).convert_alpha()
		playerBattle = playerF
		
		#initialize fa
		battlePos = ( 600, 300 )
		imglist = [ playerF, playerB, playerL, playerR, playerS, playerBattle, playerC ]
		self.fa = agents.PlayableCharacter( initpos, battlePos, imglist, 'Fatimah' )
		
		# initialize zen
		playerF = pygame.image.load( 'images/ZenaBattleSprite.png' ).convert_alpha() # not actually the front picture
		playerS = pygame.image.load( 'images/ZenaStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/ZenaHead.png" ).convert_alpha()
		playerBattle = playerF
		battlePos = ( 600, 500 )
		imglist = [ playerF, playerB, playerL, playerR, playerS, playerBattle, playerC ]
		self.zen = agents.PlayableCharacter( initpos, battlePos, imglist, 'Zena' )
		
		
		# initialize cha
		playerF = pygame.image.load( 'images/CharlesBattleSprite.png' ).convert_alpha() # not actually the front picture
		playerS = pygame.image.load( 'images/CharlesStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/CharlesHead.png" ).convert_alpha()
		playerBattle = playerF
		battlePos = ( 600, 700 )
		imglist = [ playerF, playerB, playerL, playerR, playerS, playerBattle, playerC ]
		self.cha = agents.PlayableCharacter( initpos, battlePos, imglist, 'Charles' )
		
		print 'initialized playable characters'

	#loads textbox images and makes a Conversation object
	def initConvo(self):
		textboxWidth = self.screenSize[0]
		textboxHeight = int(self.screenSize[1]/3)
		textboxCoord = (self.screenSize[0]-textboxWidth, self.screenSize[1]-textboxHeight)

		# load and scale textbox image
		textbox = pygame.image.load( "images/GameTextbox.png" ).convert_alpha()
		textbox = pygame.transform.scale(textbox, (textboxWidth, textboxHeight))

		cursor = pygame.image.load( "images/cursor.png" ).convert_alpha()

		# list of all people who will need textboxes
		# these are PlayableCharacter objects
		talkingCharList = [self.mel, self.fa, self.zen, self.cha ]

		dialogueFile = "dialogue.txt"

		self.gameConvo = conversation.Conversation(textbox, textboxCoord, cursor, self.screen, talkingCharList, self.convoFont, self.nameFont, dialogueFile)

		print "initialized convo system"
	
	# draws game start screen
	def showStartScreen( self ):
		startScreen = pygame.Surface( self.screenSize )
		startScreen.fill( ( 100, 120, 100 ) )
		startText = self.bigFont.render( 'press s to start', True, white )
	
		self.screen.blit( startScreen, ( 0, 0 ) )
		self.screen.blit( startText, ( self.screenSize[0] / 3, self.screenSize[1] / 2 ) )
		pygame.display.update()
	
	# displays the given PlayableCharacter's stats at the given position on the stat screen
	def showCharaStats( self, chara, pos ):
		stats = chara.getStats()
		
		lines = [ chara.name ]
		lines.append( ' - hp:       ' + str( stats[0] ) )
		lines.append( ' - attack:   ' + str( stats[1] ) )
		lines.append( ' - defense:  ' + str( stats[2] ) )
		lines.append( ' - speed:    ' + str( stats[3] ) )
		lines.append( ' - accuracy: ' + str( stats[4] ) )
		lines.append( ' - xp:       ' + str( stats[5] ) )
		
		for idx in range( len ( lines ) ):
			lineText = self.smallFont.render( lines[idx], True, white )
			lineHeight = 25
			linePos = ( pos[0], pos[1] + idx * lineHeight )
			self.screen.blit( lineText, linePos )
		
		lineWidth = 170
		self.screen.blit( chara.getStatusIMG(), ( pos[0] + lineWidth, pos[1] ) )
	
	# draws the current stat screen on the game window
	def showStatScreen( self, charles = False ):
		self.onStatScreen = True
		self.screen.blit( self.statBG, ( 20, 20 ), self.statBGRect )
		
		'''might be better to put these directly in the background'''
		# draw in boxes
		pygame.draw.rect( self.screen, green, self.melBox )
		pygame.draw.rect( self.screen, green, self.faBox )
		pygame.draw.rect( self.screen, green, self.zenBox )
		pygame.draw.rect( self.screen, green, self.chaBox )
		
		offset = 20
		melPos = self.melBox.topleft[0] + offset, self.melBox.topleft[1] + offset
		self.showCharaStats( self.player, melPos )
		
		faPos = self.faBox.topleft[0] + offset, self.faBox.topleft[1] + offset
		self.showCharaStats( self.fa, faPos )
		
		zenPos = self.zenBox.topleft[0] + offset, self.zenBox.topleft[1] + offset
		self.showCharaStats( self.zen, zenPos )
		
		if charles:
			chaPos = self.chaBox.topleft[0] + offset, self.chaBox.topleft[1] + offset
			self.showCharaStats( self.cha, chaPos )
		
		self.refresh.append( self.statBGRect )
	
	# sets the stored stage field to the Stage object representing stage 1 and draws it on the game screen
	def loadStage1( self ):
		bgOrig = pygame.image.load( "images/Davis Robotics Lab.png" ).convert_alpha()
		bg = pygame.transform.scale( bgOrig, self.screenSize ) # rescales the background image
		
		battleBGorig = pygame.image.load( 'images/Robotics Lab.png' ).convert_alpha()
		battleBG = pygame.transform.scale( battleBGorig, self.screenSize )
		
		self.stage1 = Stage( 1, bg, battleBG )
		
		lWall = pygame.Surface( ( 5, self.screenSize[1] ) )
		lWall.set_alpha( 0 ) # set image transparency
		leftWall = agents.Thing( ( -5, 0 ), lWall )
		self.stage1.addThing( leftWall )
	
		rWall = pygame.Surface( ( 5, self.screenSize[1] ) )
		rWall.set_alpha( 0 ) # set image transparency
		rightWall = agents.Thing( ( self.screenSize[0], 0 ), rWall )
		self.stage1.addThing( rightWall )
	
		tWall = pygame.Surface( ( self.screenSize[0], 207 ) )
		tWall.set_alpha( 0 ) # set image transparency
		topWall = agents.Thing( ( 0, 0 ), tWall )
		self.stage1.addThing( topWall )
	
		bWall = pygame.Surface( ( self.screenSize[0], 5 ) )
		bWall.set_alpha( 0 ) # set image transparency
		bottomWall = agents.Thing( ( 0, self.screenSize[1] ), bWall )
		self.stage1.addThing( bottomWall )
	
		lTableDim = ( int( 700 * self.scale ), int( 1040 * self.scale ) )
		lTablePos = ( int( 960 * self.scale ), int( 860 * self.scale ) )
		lTable = pygame.Surface( lTableDim )
		#lTable.fill( ( 100, 100, 50 ) )
		lTable.set_alpha( 0 ) # set image transparency
		leftTable = agents.Thing( lTablePos, lTable )
		self.stage1.addThing( leftTable )
	
		rTableDim = ( int( 700 * self.scale ), int( 1040 * self.scale ) )
		rTablePos = ( int( 2400 * self.scale ), int( 860 * self.scale ) )
		rTable = pygame.Surface( rTableDim )
		#rTable.fill( ( 100, 100, 50 ) )
		rTable.set_alpha( 0 ) # set image transparency
		rightTable = agents.Thing( rTablePos, rTable )
		self.stage1.addThing( rightTable )
	
		iboardDim = ( int( 380 * self.scale ), int( 1100 * self.scale ) )
		iboardPos = ( int( 100 * self.scale ), int( 2100 * self.scale ) )
		iboard = pygame.Surface( iboardDim )
		#iboard.fill( ( 100, 100, 50 ) )
		iboard.set_alpha( 0 ) # set image transparency
		board = agents.Thing( iboardPos, iboard )
		self.stage1.addThing( board )
	
		bTableDim = ( int( 790 * self.scale ), int( 485 * self.scale ) )
		bTablePos = ( int( 925 * self.scale ), int( 3085 * self.scale ) )
		bTable = pygame.Surface( bTableDim )
		#bTable.fill( ( 100, 100, 50 ) )
		bTable.set_alpha( 0 ) # set image transparency
		bottomTable = agents.Thing( bTablePos, bTable )
		self.stage1.addThing( bottomTable )
	
		lCouchDim = ( int( 785 * self.scale ), int( 480 * self.scale ) )
		lCouchPos = ( int( 2670 * self.scale ), int( 2530 * self.scale ) )
		lCouch = pygame.Surface( lCouchDim )
		#lCouch.fill( ( 100, 100, 50 ) )
		lCouch.set_alpha( 0 ) # set image transparency
		leftCouch = agents.Thing( lCouchPos, lCouch )
		self.stage1.addThing( leftCouch )
	
		rCouchDim = ( int( 610 * self.scale ), int( 1080 * self.scale ) )
		rCouchPos = ( int ( 3440 * self.scale ), int( 1920 * self.scale ) )
		rCouch = pygame.Surface( rCouchDim )
		#rCouch.fill( ( 100, 100, 50 ) )
		rCouch.set_alpha( 0 ) # set image transparency
		rightCouch = agents.Thing( rCouchPos, rCouch )
		self.stage1.addThing( rightCouch )
		
		print 'loaded stage 1'
	
	def enterStage1( self ):
		self.stage = self.stage1
		self.stage.draw( self.screen )
		
		self.player.setPosition( 650, 550 )
		self.player.draw( self.screen )
		pygame.display.update()
	
	# creates the given number of Enemies, of the given level
	def spawnEnemies( self, num, level ):
		for i in range( num ):
			# position based on index i
			pos = ( 100, i * 250 + 50 )
			img = random.choice( self.bugImgs )
			name = 'bug' + str( i )
			e = agents.Enemy( pos, img, name, level )
			self.enemies.append( e )
			self.battleParticipants.append( e )
	
	def enterDialogue(self):
		#move to next convo every time enterDialogue is called
		#so that story moves sequentially
		self.inDialogue = True  
		self.stage.fillBG( self.screen, self.refresh)
		self.player.draw( self.screen )
		self.gameConvo.displayText(self.convoNum)
		print "ENTERED DIALOGUE"
		#is it drawing melody again??


	# changes game state to battle mode
	def enterBattle( self, charles = False ):
		# update display for background
		self.stage.fillBattleBG( self.screen )
		self.refresh.append( self.screen.get_rect() )
		
		self.inBattle = True
		self.player.enterBattle()
		self.fa.enterBattle()
		self.zen.enterBattle()
		
		# build list of battle participants
		self.battleParticipants= [ self.mel, self.fa, self.zen ]
		self.currentBattleTurn = 0
		
		self.livePlayers = [ self.mel, self.fa, self.zen ]
		
		self.spawnEnemies( 3, 1 ) # 3 enemies of level 1
		self.enemies[0].select()
		self.selectedEnemyIDX = 0
		print 'enter battle'
		
		# reset stored points for new battle
		self.storedPoints = 0
		
		# if Charles is currently playable
		if charles:
			self.cha.enterBattle()
			self.battleParticipants.append( self.cha )
			self.livePlayers.append( self.cha )
	
	# changes game state back to exploration mode
	def leaveBattle( self ):
		self.inBattle = False
		self.stage.fillBG( self.screen, self.refresh )
		self.player.leaveBattle()
		self.enemies = [] # empty enemies list
		self.selectedEnemyIDX = -1
		self.battleParticipants = []
		print 'leave battle'
	
	# updates the game for one time-step (when the player is playing through a stage)
	def update( self ):
		if self.onStatScreen:
			self.updateStatScreen()
		elif self.inBattle:
			self.updateBattle()
		##################ZENA ADDED##################
		elif self.inDialogue:   
			self.updateDialogue()
		##############################################
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
					return # so that characters aren't still drawn over stat screens
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
					self.enterBattle()
				elif event.key == pygame.K_c:
					self.enterDialogue()
					return
			
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
	
	# determines enemy attack for an enemy turn in battle
	# returns whether the turn ended the battle
	def enemyTurn( self ):
		# randomly select a livePlayer and attack
		target = random.choice( self.livePlayers )
		#self.battleParticipants[self.currentBattleTurn].attack( target, 100 ) # to always lose
		self.battleParticipants[self.currentBattleTurn].attack( target, 50 ) # to always win
		
		if not target.isDead(): # if the target is still alive, pass on turn index
			self.passOnTurn()
		
		# if the attack was fatal, remove that character from the lists
		# do not pass on turn here, because removing player makes indices for enemies go one down
		else:
			print '--died: ' + target.name
			
			self.battleParticipants.remove( target )
			self.livePlayers.remove( target )
			
			#print 'turn stays at', self.currentBattleTurn, 'out of', len( self.battleParticipants )
			
			# erase killed target
			eraseRect = target.getRect()
			eraseRect.width += 12
			eraseRect.height += 12
			self.stage.fillBattleBG( self.screen, eraseRect )
			self.refresh.append( eraseRect )
			
			# if indices are now off (which happens when the attacker is the last in the participant list)
			if self.currentBattleTurn == len( self.battleParticipants ):
				self.currentBattleTurn = 0
		
		if len( self.livePlayers ) == 0:
			print 'you lose!'
			return True
		else:
			return False
	
	# moves the battle turn to the next character
	def passOnTurn( self ):
		# pass on battle turn
		self.currentBattleTurn += 1
		if self.currentBattleTurn > len( self.battleParticipants ) - 1: # wrap around to front of list
			self.currentBattleTurn = 0
		print '\ncurrent battle turn is', self.battleParticipants[self.currentBattleTurn].name + ',', \
			self.currentBattleTurn, 'out of', len( self.battleParticipants), 'left'
	
	# for wins: awards the currently stored amount of XP to all player characters who are still alive
	def awardXP( self ) :
		for chara in self.livePlayers:
			chara.increaseXP( self.storedPoints )
	
	# parses keyboard input for battle mode and updates screen contents
	def updateBattle( self ):
		done = False
		
		attacker = self.battleParticipants[self.currentBattleTurn]
		if attacker.getType() == 'PlayableCharacter':
			playerTurn = True
			attacker.attacking = True # make blue box appear
		else:
			playerTurn = False
			print 'enemy turn'
		
		# parse keyboard/mouse input events
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN: # for initial key presses
				if event.key == pygame.K_s: # show stat screen
					self.onStatScreen = True
					print 'show stat screen'
					self.showStatScreen()
					return # so that characters aren't still drawn over stat screen
				
				# if it's the player's turn, check for other input
				if playerTurn:
					#print 'player turn'
					
					# change enemy selection
					if event.key == pygame.K_UP:
						newIDX = self.selectedEnemyIDX - 1
						if newIDX > -1:
							prev = self.enemies[self.selectedEnemyIDX]
							rad = 10
							prev.deselect()
							
							# erase selection cursor
							eraseRect = pygame.Rect( ( prev.rightEdge - rad, prev.bottomEdge - rad ),
													   ( 2 * rad + 2, 2 * rad + 2 ) )
							self.stage.fillBattleBG( self.screen, eraseRect )
						
							self.selectedEnemyIDX -= 1
							self.enemies[self.selectedEnemyIDX].select()
						elif newIDX == -1:
							prev = self.enemies[self.selectedEnemyIDX]
							rad = 10
							prev.deselect()
							
							# erase selection cursor
							eraseRect = pygame.Rect( ( prev.rightEdge - rad, prev.bottomEdge - rad ),
													   ( 2 * rad + 2, 2 * rad + 2 ) )
							self.stage.fillBattleBG( self.screen, eraseRect )
						
							self.selectedEnemyIDX = len( self.enemies ) - 1
							self.enemies[self.selectedEnemyIDX].select()
					elif event.key == pygame.K_DOWN:
						newIDX = self.selectedEnemyIDX + 1
						if newIDX < len( self.enemies ):
							prev = self.enemies[self.selectedEnemyIDX]
							rad = 10
							prev.deselect()
							
							# erase selection cursor
							eraseRect = pygame.Rect( ( prev.rightEdge - rad, prev.bottomEdge - rad ),
													   ( 2 * rad + 2, 2 * rad + 2 ) )
							self.stage.fillBattleBG( self.screen, eraseRect )
						
							self.selectedEnemyIDX += 1
							self.enemies[self.selectedEnemyIDX].select()
						elif newIDX == len( self.enemies ):
							prev = self.enemies[self.selectedEnemyIDX]
							rad = 10
							prev.deselect()
							
							# erase selection cursor
							eraseRect = pygame.Rect( ( prev.rightEdge - rad, prev.bottomEdge - rad ),
													   ( 2 * rad + 2, 2 * rad + 2 ) )
							self.stage.fillBattleBG( self.screen, eraseRect )
						
							self.selectedEnemyIDX = 0
							self.enemies[self.selectedEnemyIDX].select()
				
					# attack currently selected enemy
					elif event.key == pygame.K_a:
						target = self.enemies[self.selectedEnemyIDX]
						attacker.attack( target, 50 )
						
						attacker.attacking = False # make box disappear
						self.passOnTurn()
						
						# if attack killed target
						if target.isDead():
							print '--died: ' + target.name
							
							toRemove = self.enemies.pop( self.selectedEnemyIDX )
							self.battleParticipants.remove( toRemove )
							self.selectedEnemyIDX = 0 # reset selection to 0
							
							# add points for kill to stored total
							self.storedPoints += toRemove.level
						
							# erase killed target
							eraseRect = toRemove.getRect()
							eraseRect.width += 12
							eraseRect.height += 12
							self.stage.fillBattleBG( self.screen, eraseRect )
						
							if len( self.enemies ) != 0: # if still enemies, reselect first one
								self.enemies[0].select()
							else: # if all enemies are gone
								print 'you win!'
								self.awardXP()
								self.leaveBattle()
								'''add code here to increase XP'''
								done = True
			
			if event.type == pygame.QUIT:
				sys.exit()
		
		# if it's an enemy's turn, have it attack
		if not playerTurn:
			loss = self.enemyTurn()
			if loss: # if the enemy turn resulted in a loss, the battle is done
				self.leaveBattle()
				done = True
		
		# if we're still on the battle screen
		if not done:
			# update screen contents
			for edna in self.battleParticipants:
				edna.draw( self.screen )
				self.refresh.append( edna.getRect() )
		
			#self.player.draw( self.screen )
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
						self.stage.fillBattleBG( self.screen, self.statBGRect )
						self.refresh.append( self.statBGRect )
					else: # redraw stage
						self.stage.fillBG( self.screen, self.refresh, self.statBGRect)
						self.player.draw( self.screen )
						self.refresh.append( self.player.getRect() )
			
			if event.type == pygame.QUIT:
				sys.exit()

	#continues to next box in dialogue	
	def updateDialogue(self):
		#print "IN UPDATE DIALOGUE"
		if self.gameConvo.convoOver == True:
			print "EXITING DIALOGUE"
			self.inDialogue = False
			self.stage.fillBG( self.screen, self.refresh)
			self.player.draw( self.screen )
			self.refresh.append( self.player.getRect() )
			self.convoNum += 1
		else:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_c:
						print "UPDATING DIALOGUE"
						if self.gameConvo.convoOver != True:
							print "STILL MORE TEXT"
							#draw BG again first
							self.stage.fillBG( self.screen, self.refresh)
							self.player.draw( self.screen )

							self.gameConvo.advanceText()
						
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
	game.enterStage1()
	
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