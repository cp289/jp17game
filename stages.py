# Melody Mao
# CS269, January 2017
# Debug Davis

# stages.py
# This file defines the Stage and Game classes.

import pygame
import sys
import agents
import random
from attackChooser import *
from sound import *
import conversation
from sound import *

# some useful variables for the rest of this file
back, front, left, right, none = range( 5 )
green = ( 150, 180, 160 )
white = ( 255, 255, 255 )

'''
This class represents one stage/room of the game.
It stores its furniture and walls as Things.
'''
class Stage:
	
	# fields: number battles to win, background images, list of Thing contents, Surface screen
	
	# creates a new Stage with the given number of battles to win and background image
	# optional to give starting player Position on stage and starting camera position (upper left corner)
	def __init__( self, name, numBattles, scale, bg, battleBG, bugs ):
		self.name = name
		self.numBattles = numBattles
		self.battlesCompleted = 0
		self.background = bg
		self.battleBG = battleBG
		self.scale = scale
		
		self.contents = pygame.sprite.Group()
		self.doors = []
		self.bugImgs = bugs
		
		# variables for dimensions of stage
		self.height = bg.get_rect().height
		self.width = bg.get_rect().width
		self.topWallEdge = 0 # y-coordinate for the bottom of the top wall
		
		self.stepsTaken = 0 # number of steps taken in this stage since the last battle
	
	# sets the field storing the bottom of the top walls
	def setTopWallEdge( self, e ):
		self.topWallEdge = e
	
	# add a wall or of piece of furniture to the stage
	def addThing( self, thing ):
		self.contents.add( thing )
	
	# add a door to another room
	def addDoor( self, door ):
		self.doors.append( door )
	
	# add 1 step to those recorded for this stage
	def addStep( self ):
		self.stepsTaken += 1
	
	# returns a randomly chosen bug image from the set for this stage
	def randomBug( self ):
		return random.choice( self.bugImgs )
	
	# add 1 to the number of battles completed in this stage
	def addBattle( self ):
		self.battlesCompleted += 1
	
	# returns whether this stage has been completed
	def completed( self ):
		return self.numBattles == self.battlesCompleted
	
	# returns whether the given character is within the given range of the left wall
	# for stopping camera view adjustment at the wall
	def approachingLeftWall( self, chara, dist ):
		return chara.getStagePos()[0] <= dist
	
	# returns whether the given character is within the given range of the right wall
	# for stopping camera view adjustment at the wall
	def approachingRightWall( self, chara, dist ):
		return self.width - chara.getStagePos()[0] - chara.rect.width <= dist + 10 # add 10 because the right wall is weird
	
	# returns whether the given character is within the given range of the top wall
	def approachingTopWall( self, chara, dist ):
		return chara.ghost.topleft[1] <= self.topWallEdge + dist
	
	# returns whether the given character is within the given range of the bottom wall
	# for stopping camera view adjustment at the wall
	def approachingBottomWall( self, chara, dist ):
		return self.height - chara.getStagePos()[1] - chara.rect.height <= dist
	# halts the given Character's movement if they are about to collide with anything in this Stage
	# returns whether a collision was detected
	def collide( self, chara ):
		collided = False
		
		for thing in self.contents:
			if chara.collide( thing ):
				collided = True
		
		return collided
	
	# returns the door the given character is at, if there is one
	# otherwise returns None
	def atDoor( self, chara ):
		for door in self.doors:
			#print 'checking door', door.rect
			if door.getRect().colliderect( chara.ghost ):
				return door
		
		return None
	
	# draws the section of the stage that is now in the camera view
	def moveCamView( self, screen, refresh, camrect ):
		screen.blit( self.background, ( 0, 0 ), camrect )
		refresh.append( screen.get_rect() )
	
	# draws the subsection of the stage background within the given rectangle
	# if camera is given, adjusts for camera view
	def fillBG( self, screen, refresh, rect = None, cam = None ):
		# draw the entire screen
		if ( rect == None and cam == None ):
			# now draw the surfaces to the screen using the blit function
			screen.blit( self.background, ( 0, 0 ) )
		
			refresh.append( screen.get_rect() )
	
		# draw a specific section
		else:
			adjustedRect = rect.move( cam.topleft[0], cam.topleft[1] ) # to make it fill in the correct section of the background
			screen.blit( self.background, rect, adjustedRect )
			
			refresh.append( rect )
			
			#print 'filled', rect
	
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
	
	# start a new Game
	def __init__( self, screen ):
		# create a screen (width, height)
		self.screenSize = ( screen.get_width(), screen.get_height() )
		self.screen = screen
		
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
		self.storedPoints = 0 # amount of XP all live players will gain on winning the current battle
		
		self.enemies = [] # start out with no enemies, because not in battle
		self.selectedEnemyIDX = -1 # index of current selected enemy
		
		self.camera = pygame.Rect( ( 0, 0 ), self.screenSize ) # represents current section of stage in view
		self.stage = None # set by calling the methods for entering stages
		self.hallwayStage = None # these three are created when the loading methods are called
		self.roboLabStage = None
		self.macLabStage = None
		
		# load specific screen backgrounds
		statBGorig = pygame.image.load( 'images/backgrounds/statScreenBG.png' ).convert_alpha()
		self.statBG = pygame.transform.scale( statBGorig, self.screenSize ) # force it to be square for now
		self.statBGRect = pygame.Rect( ( 20, 20 ), ( self.screenSize[0] - 40, self.screenSize[1] - 40 ) )
		
		# makes boxes for the characters on the stat screen
		offset = 20
		boxWidth = ( self.statBGRect.width - 3 * offset ) / 2
		boxHeight = ( self.statBGRect.height - 3 * offset ) / 2
		self.melBox = pygame.Rect( ( 2 * offset, 2 * offset ), ( boxWidth, boxHeight ) )
		self.faBox = pygame.Rect( ( 2 * offset, 3 * offset + boxHeight ), ( boxWidth, boxHeight ) )
		self.zenBox = pygame.Rect( ( 3 * offset + boxWidth, 2 * offset ), ( boxWidth, boxHeight ) )
		self.chaBox = pygame.Rect( ( 3 * offset + boxWidth, 3 * offset + boxHeight ), ( boxWidth, boxHeight ) )
		
		# create fonts
		self.bigFont = pygame.font.SysFont( 'Helvetica', 44, bold=True )
		self.smallFont = pygame.font.SysFont( 'Helvetica', 18 )
		self.nameFont = pygame.font.SysFont( "Helvetica", 32, bold=True )
		self.convoFont = pygame.font.SysFont( "Helvetica", 28, bold=True )
		
		# load sound object
		self.sound = Sound()
		
		# init Conversation object
		self.initConvo()
		self.convoNum = 0
		
		# load sound object
		self.sound = Sound()
		
		# mostly for testing
		self.timeStep = 0
	
	# creates the PlayableCharacters in the game
	def initPlayers( self ):
		
		# the given image list should contain six lists: standing, walking, battle, attacking, dying, and other
		# the standing list contains the standing images in the order: front, back, left, right
		# the walking, attacking, and dying lists are animation frames in orders
		# the battle list contains two frames for idle, and two frames for taking damage
		# the other list contains: status, conversation heads
		
		# load images
		playerL = pygame.image.load( 'images/Melody/Walk/Left/MelodyLeftStand.png' ).convert_alpha()
		playerR = pygame.image.load( 'images/Melody/Walk/Right/MelodyRightStand.png' ).convert_alpha()
		playerF = pygame.image.load( 'images/Melody/Walk/Down/MelodyDownStand.png' ).convert_alpha()
		playerB = pygame.image.load( 'images/Melody/Walk/Up/MelodyUpStand.png' ).convert_alpha()
		playerS = pygame.image.load( 'images/Melody/MelodyStatPic.png' ).convert_alpha()
		#playerBattle = pygame.image.load( 'images/Melody/MelodyBattleSprite.png' ).convert_alpha()
		playerC = pygame.image.load( "images/Melody/MelodyHead.png" ).convert_alpha()
		standlist = ( playerF, playerB, playerL, playerR )
		walkF = 'images/Melody/Walk/Down/MelodyDownWalk'
		walkB = 'images/Melody/Walk/Up/MelodyUpWalk'
		walkL = 'images/Melody/Walk/Left/MelodyLeftWalk'
		walkR = 'images/Melody/Walk/Right/MelodyRightWalk'
		walklist = ( walkF, walkB, walkL, walkR )
		battlelist = ( pygame.image.load( 'images/Melody/MelodyBattleSprite.png' ).convert_alpha() ) # TEMPORARY
		attacklist = None
		dielist = None
		otherlist = ( playerS, playerC )
		
		# initialize mel
		initpos = ( 300, 400 ) # hopefully the middle of the bottom
		battlePos = ( 700, 50 )
		namePos = ( 25, -1 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.mel = agents.PlayableCharacter( initpos, battlePos, imglist, 'Melody', namePos )
		self.mel.setAllStats( ( 500, 54, 44, 43, 50, 7 ) )
		# total HP, ATK, DFN, SPD, ACC, time
		self.mel.setAllGR( ( 0.8, 0.9, 0.85, 0.75, 0.7 ) )
		# HP, ATK, DFN, SPD, ACC
		
		standlist = None
		walklist = None
		battlelist = ( pygame.image.load( 'images/Fatimah/FatimahBattleSprite.png' ).convert_alpha() ) # TEMPORARY
		attacklist = None
		dielist = None
		playerS = pygame.image.load( 'images/Fatimah/FatimahStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/Fatimah/FatimahHead.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		
		#initialize fa
		battlePos = ( 600, 178 )
		namePos = ( 15, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.fa = agents.PlayableCharacter( initpos, battlePos, imglist, 'Fatimah', namePos )
		self.fa.setAllStats( ( 400, 44, 54, 51, 50, 6 ) )
		self.fa.setAllGR( ( 0.85, 0.9, 0.8, 0.7, 0.75 ) )
		
		# initialize zen
		battlelist = ( pygame.image.load( 'images/Zena/ZenaBattleSprite.png' ).convert_alpha() ) # TEMPORARY
		playerS = pygame.image.load( 'images/Zena/ZenaStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/Zena/ZenaHead.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		battlePos = ( 500, 306 )
		namePos = ( 40, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.zen = agents.PlayableCharacter( initpos, battlePos, imglist, 'Zena', namePos )
		self.zen.setAllStats( ( 450, 49, 48, 54, 45, 9 ) )
		self.zen.setAllGR( ( 0.8, 0.75, 0.85, 0.9, 0.7 ) )
		
		# initialize cha
		battlelist = ( pygame.image.load( 'images/Charles/CharlesBattleSprite.png' ).convert_alpha() ) # TEMPORARY
		playerS = pygame.image.load( 'images/Charles/CharlesStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/Charles/CharlesHead.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		battlePos = ( 400, 404 )
		namePos = ( 20, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.cha = agents.PlayableCharacter( initpos, battlePos, imglist, 'Charles', namePos )
		self.cha.setAllStats( ( 500, 44, 49, 44, 54, 7 ) )
		self.cha.setAllGR( ( 0.75, 0.7, 0.8, 0.9, 0.85 ) )
		
		"""
		Initialize non-playable characters who just take part in convos
		"""
		playerS = None
		otherlist = (playerS, playerC)
		battlePos = ( 0, 0 ) # doesn't matter anyways
		fillerImg = battlelist
		battlelist = fillerImg # needs image but never battles anyways

		#initalize chaEvil
		playerC = pygame.image.load( "images/Charles/PossessedCharles.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		namePos = ( 9, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.chaEvil = agents.PlayableCharacter( initpos, battlePos, imglist, 'Charles?', namePos )

		#initialize bru
		playerC = pygame.image.load( "images/Bruce/BruceHead.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		namePos = ( 33, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.bru = agents.PlayableCharacter( initpos, battlePos, imglist, 'Bruce', namePos )

		#initialize bruEvil
		playerC = pygame.image.load( "images/Bruce/BruceHeadEvil.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		namePos = ( 24, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.bruEvil = agents.PlayableCharacter( initpos, battlePos, imglist, 'Bruce?', namePos )

		#initialize NPE
		playerC = pygame.image.load( "images/bugs/BossBugSilhouette.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		namePos = ( 44, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.NPE = agents.PlayableCharacter( initpos, battlePos, imglist, 'NPE', namePos )

		playerC = None 

		#initialize stu1
		otherlist = ( playerS, playerC )
		namePos = ( 1, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.stu1 = agents.PlayableCharacter( initpos, battlePos, imglist, 'Student_1', namePos )

		#initialize stu2
		otherlist = ( playerS, playerC )
		namePos = ( 1, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.stu2 = agents.PlayableCharacter( initpos, battlePos, imglist, 'Student_2', namePos )

		#initialize CSC
		otherlist = ( playerS, playerC )
		namePos = ( 15, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.CSC = agents.PlayableCharacter( initpos, battlePos, imglist, 'CS_Child', namePos )
		
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
		talkingCharList = [self.mel, self.fa, self.zen, self.cha, self.chaEvil, self.bru, self.bruEvil, self.NPE, self.stu1, self.stu2, self.CSC ]

		dialogueFile = "Script.txt"

		self.gameConvo = conversation.Conversation(textbox, textboxCoord, cursor, self.screen, talkingCharList, self.convoFont, self.nameFont, dialogueFile)

		print "initialized convo system"
	
	# sets the player's onscreen position so that it matches its stage position,
	# based on the current camera view
	# returns previous player rect for erasure
	def placePlayerOnScreen( self ):
		pos = self.player.getStagePos()
		
		#prevRect = self.player.rect.copy()
		prevRect = self.player.eraseRect
		
		screenPos = ( pos[0] - self.camera.topleft[0], pos[1] - self.camera.topleft[1] )
		self.player.setScreenPos( screenPos[0], screenPos[1] )
		
		return prevRect
	
	# loads images for robotics lab stage and creates the furniture objects
	def loadHallwayStage( self ):
		scale = 0.5
		
		bgOrig = pygame.image.load( 'images/backgrounds/Davis Hallway.png' ).convert_alpha()
		newDim = ( int( bgOrig.get_width() * scale ), int( bgOrig.get_height() * scale ) )
		bg = pygame.transform.scale( bgOrig, newDim ) # rescales the background image
		
		battleBGorig = pygame.image.load( 'images/backgrounds/Hallway Battle.png' ).convert_alpha()
		battleBG = pygame.transform.scale( battleBGorig, self.screenSize )
		
		bugImgs = [ pygame.image.load( 'images/bugs/Bug 0.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 10.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 11.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 100.png' ).convert_alpha()
						]
		
		self.hallwayStage = Stage( 'hallway', 1, scale, bg, battleBG, bugImgs )
		
		# create doors
		
		doorToRoboLab = agents.Door( ( 0, 1365 * scale ), ( 10, 40 / scale ), 'robotics lab' )
		self.hallwayStage.addDoor( doorToRoboLab )
		
		# create walls
		
		lWall = pygame.Surface( ( 5, self.hallwayStage.height ) )
		lWall.set_alpha( 0 ) # set image transparency
		leftWall = agents.Thing( ( -5, 0 ), lWall )
		self.hallwayStage.addThing( leftWall )
		
		rWall = pygame.Surface( ( 5, self.hallwayStage.height ) )
		rWall.set_alpha( 0 ) # set image transparency
		rightWall = agents.Thing( ( self.hallwayStage.width - 5, 0 ), rWall )
		self.hallwayStage.addThing( rightWall )
		
		topWallHeight = 715 * scale
		self.hallwayStage.setTopWallEdge( topWallHeight )
		tWall = pygame.Surface( ( self.hallwayStage.width, topWallHeight ) )
		#tWall.fill( ( 100, 100, 50 ) )
		tWall.set_alpha( 0 ) # set image transparency
		topWall = agents.Thing( ( 0, 0 ), tWall )
		self.hallwayStage.addThing( topWall )
	
		bWall = pygame.Surface( ( self.hallwayStage.width, 5 ) )
		bWall.set_alpha( 0 ) # set image transparency
		bottomWall = agents.Thing( ( 0, self.hallwayStage.height ), bWall )
		self.hallwayStage.addThing( bottomWall )
		
		lChairDim = ( 370 * scale, 470 * scale )
		lChairPos = ( 445 * scale, 965 * scale )
		lChair = pygame.Surface( lChairDim )
		lChair.set_alpha( 0 )
		leftChair = agents.Thing( lChairPos, lChair )
		self.hallwayStage.addThing( leftChair )
		
		mChairDim = ( 370 * scale, 470 * scale )
		mChairPos = ( 1080 * scale, 990 * scale )
		mChair = pygame.Surface( mChairDim )
		mChair.set_alpha( 0 )
		middleChair = agents.Thing( mChairPos, mChair )
		self.hallwayStage.addThing( middleChair )
		
		rChairDim = ( 425 * scale, 375 * scale )
		rChairPos = ( 1520 * scale, 1610 * scale )
		rChair = pygame.Surface( rChairDim )
		rChair.set_alpha( 0 )
		rightChair = agents.Thing( rChairPos, rChair )
		self.hallwayStage.addThing( rightChair )
		
		lBoxDim = ( 350 * scale, 350 * scale )
		lBoxPos = ( 435 * scale, 1675 * scale )
		lBox = pygame.Surface( lBoxDim )
		lBox.set_alpha( 0 )
		leftBox = agents.Thing( lBoxPos, lBox )
		self.hallwayStage.addThing( leftBox )
		
		rBoxDim = ( 350 * scale, 350 * scale )
		rBoxPos = ( 940 * scale, 1820 * scale )
		rBox = pygame.Surface( rBoxDim )
		rBox.set_alpha( 0 )
		rightBox = agents.Thing( rBoxPos, rBox )
		self.hallwayStage.addThing( rightBox )
		
		iSofaDim = ( 1090 * scale, 430 * scale )
		iSofaPos = ( 410 * scale, 2430 * scale )
		iSofa = pygame.Surface( iSofaDim )
		iSofa.set_alpha( 0 )
		sofa = agents.Thing( iSofaPos, iSofa )
		self.hallwayStage.addThing( sofa )
		
		iTrashDim = ( 550 * scale, 170 * scale )
		iTrashPos = ( 2450 * scale, 715 * scale )
		iTrash = pygame.Surface( iTrashDim )
		iTrash.set_alpha( 0 )
		trash = agents.Thing( iTrashPos, iTrash )
		self.hallwayStage.addThing( trash )
		
		uTableDim = ( 510 * scale, 455 * scale )
		uTablePos = ( 2235 * scale, 1060 * scale )
		uTable = pygame.Surface( uTableDim )
		uTable.set_alpha( 0 )
		upTable = agents.Thing( uTablePos, uTable )
		self.hallwayStage.addThing( upTable )
		
		dTableDim = ( 520 * scale, 430 * scale )
		dTablePos = ( 2195 * scale, 1950 * scale )
		dTable = pygame.Surface( dTableDim )
		dTable.set_alpha( 0 )
		downTable = agents.Thing( dTablePos, dTable )
		self.hallwayStage.addThing( downTable )
		
		sLabDim = ( 2000 * scale, 2220 * scale )
		sLabPos = ( 3000 * scale, 0 * scale )
		sLab = pygame.Surface( sLabDim )
		sLab.set_alpha( 0 )
		smallLab = agents.Thing( sLabPos, sLab )
		self.hallwayStage.addThing( smallLab )
		
		print 'loaded hallway stage'
	
	# changes current stage to hallway and places player and camera at starting positions
	def enterHallwayStageRight( self ):
		self.stage = self.hallwayStage
		
		# set initial player and camera positions for this room
		self.camera.topleft = 3400 * self.stage.scale, 2000 * self.stage.scale
		initPos = ( 4800 * self.stage.scale, 2500 * self.stage.scale )
		
		self.player.setStagePos( initPos[0], initPos[1] )
		self.placePlayerOnScreen()
		
		self.player.goLeft( self.tileSize )
		
		self.hallwayStage.moveCamView( self.screen, self.refresh, self.camera )
		self.player.draw( self.screen )
		pygame.display.update()
		
		self.sound.play( 'explora', -1 )
		
		print 'enter hallway from right'
	
	# changes current stage to hallway and places player and camera at starting positions
	def enterHallwayStageLeft( self ):
		self.stage = self.hallwayStage
		
		# set initial player and camera positions for this room
		self.camera.topleft = 0 * self.stage.scale, 700 * self.stage.scale
		initPos = ( 10 * self.stage.scale, 1100 * self.stage.scale )
		
		self.player.setStagePos( initPos[0], initPos[1] )
		self.placePlayerOnScreen()
		
		self.player.goRight( self.tileSize )
		
		self.hallwayStage.moveCamView( self.screen, self.refresh, self.camera )
		self.player.draw( self.screen )
		pygame.display.update()
		
		print 'enter hallway from left'
	
	# loads images for robotics lab stage and creates the furniture objects
	def loadRoboLabStage( self ):
		scale = 0.4
		
		bgOrig = pygame.image.load( 'images/backgrounds/Davis Robotics Lab.png' ).convert_alpha()
		newDim = ( int( bgOrig.get_width() * scale ), int( bgOrig.get_height() * scale ) )
		bg = pygame.transform.scale( bgOrig, newDim ) # rescales the background image
		
		battleBGorig = pygame.image.load( 'images/backgrounds/Robotics Lab Battle.png' ).convert_alpha()
		battleBG = pygame.transform.scale( battleBGorig, self.screenSize )
		
		bugImgs = [ pygame.image.load( 'images/bugs/Bug 101.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 110.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 111.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1000.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1001.png' ).convert_alpha()
						]
		
		self.roboLabStage = Stage( 'robotics lab', 3, scale, bg, battleBG, bugImgs )
		
		# create door
		
		doorToHall = agents.Door( ( self.roboLabStage.width - 15, 3672 * scale ), \
			( 15, 378 * scale ), 'hallway' )
		self.roboLabStage.addDoor( doorToHall )
		
		# create walls
		
		lWall = pygame.Surface( ( 10, self.roboLabStage.height ) )
		lWall.set_alpha( 0 ) # set image transparency
		leftWall = agents.Thing( ( -5, 0 ), lWall )
		self.roboLabStage.addThing( leftWall )
	
		rWall = pygame.Surface( ( 10, self.roboLabStage.height ) )
		rWall.set_alpha( 0 ) # set image transparency
		rightWall = agents.Thing( ( self.roboLabStage.width - 5, 0 ), rWall )
		self.roboLabStage.addThing( rightWall )
		
		topWallHeight = 1110 * scale
		self.roboLabStage.setTopWallEdge( topWallHeight )
		tWall = pygame.Surface( ( self.roboLabStage.width, topWallHeight ) )
		#tWall.fill( ( 100, 100, 50 ) )
		tWall.set_alpha( 0 ) # set image transparency
		topWall = agents.Thing( ( 0, 0 ), tWall )
		self.roboLabStage.addThing( topWall )
	
		bWall = pygame.Surface( ( self.roboLabStage.width, 5 ) )
		bWall.set_alpha( 0 ) # set image transparency
		bottomWall = agents.Thing( ( 0, self.roboLabStage.height ), bWall )
		self.roboLabStage.addThing( bottomWall )
		
		# load furniture
		
		lTableDim = ( int( 700 * scale ), int( 1040 * scale ) )
		lTablePos = ( int( 960 * scale ), int( 860 * scale ) )
		lTable = pygame.Surface( lTableDim )
		#lTable.fill( ( 100, 100, 50 ) )
		lTable.set_alpha( 0 ) # set image transparency
		leftTable = agents.Thing( lTablePos, lTable )
		self.roboLabStage.addThing( leftTable )
	
		rTableDim = ( int( 700 * scale ), int( 1040 * scale ) )
		rTablePos = ( int( 2400 * scale ), int( 860 * scale ) )
		rTable = pygame.Surface( rTableDim )
		#rTable.fill( ( 100, 100, 50 ) )
		rTable.set_alpha( 0 ) # set image transparency
		rightTable = agents.Thing( rTablePos, rTable )
		self.roboLabStage.addThing( rightTable )
		
		rboardDim = ( int( 210 * scale ), int( 710 * scale ) )
		rboardPos = ( int( 265 * scale ), int( 2100 * scale ) )
		rboard = pygame.Surface( rboardDim )
		#rboard.fill( ( 100, 100, 50 ) )
		rboard.set_alpha( 0 ) # set image transparency
		board = agents.Thing( rboardPos, rboard )
		self.roboLabStage.addThing( board )
		
		lboardDim = ( int( 210 * scale ), int( 980 * scale ) )
		lboardPos = ( int( 30 * scale ), int( 2250 * scale ) )
		lboard = pygame.Surface( lboardDim )
		#lboard.fill( ( 100, 100, 50 ) )
		lboard.set_alpha( 0 ) # set image transparency
		otherboard = agents.Thing( lboardPos, lboard )
		self.roboLabStage.addThing( otherboard )
		
		bTableDim = ( int( 790 * scale ), int( 485 * scale ) )
		bTablePos = ( int( 925 * scale ), int( 3085 * scale ) )
		bTable = pygame.Surface( bTableDim )
		#bTable.fill( ( 100, 100, 50 ) )
		bTable.set_alpha( 0 ) # set image transparency
		bottomTable = agents.Thing( bTablePos, bTable )
		self.roboLabStage.addThing( bottomTable )
	
		lCouchDim = ( int( 785 * scale ), int( 480 * scale ) )
		lCouchPos = ( int( 2670 * scale ), int( 2530 * scale ) )
		lCouch = pygame.Surface( lCouchDim )
		#lCouch.fill( ( 100, 100, 50 ) )
		lCouch.set_alpha( 0 ) # set image transparency
		leftCouch = agents.Thing( lCouchPos, lCouch )
		self.roboLabStage.addThing( leftCouch )
	
		rCouchDim = ( int( 610 * scale ), int( 1080 * scale ) )
		rCouchPos = ( int ( 3440 * scale ), int( 1920 * scale ) )
		rCouch = pygame.Surface( rCouchDim )
		#rCouch.fill( ( 100, 100, 50 ) )
		rCouch.set_alpha( 0 ) # set image transparency
		rightCouch = agents.Thing( rCouchPos, rCouch )
		self.roboLabStage.addThing( rightCouch )
		
		print 'loaded robotics lab stage'
	
	# changes current stage to robotics lab and places player and camera at starting positions
	def enterRoboLabStage( self ):
		self.stage = self.roboLabStage
		
		# set initial player and camera positions for this room
		
		#self.camera.topleft = 2450 * self.stage.scale, 2850 * self.stage.scale # for scale 0.5
		#initPos = ( 3900 * self.stage.scale, 3672 * self.stage.scale )
		
		self.camera.topleft = 2050 * self.stage.scale, 2550 * self.stage.scale # for scale 0.4
		initPos = ( 3890 * self.stage.scale, 3600 * self.stage.scale )
		
		self.player.setStagePos( initPos[0], initPos[1] )
		self.placePlayerOnScreen()
		
		self.player.goLeft( self.tileSize )
		
		self.roboLabStage.moveCamView( self.screen, self.refresh, self.camera )
		self.player.draw( self.screen )
		pygame.display.update()
		
		print 'enter robotics lab'
	
	# loads images for Mac lab stage and creates the furniture objects
	def loadMacLabStage( self ):
		pass
	
	# changes current stage to Mac lab and places player and camera at starting positions
	def enterMacLabStage( self ):
		pass
	
	# creates the given number of Enemies, of the given level
	def spawnEnemies( self, num, level ):
		for i in range( num ):
			# position based on index i
			pos = ( 20, i * 145 + 20 )
			img = self.stage.randomBug()
			name = 'bug' + str( i )
			e = agents.Enemy( pos, img, name, level )
			
			self.enemies.append( e )
			self.battleParticipants.append( e )
	
	# changes game state to battle mode
	def enterBattle( self, charles = False ):
		# update display for background
		self.stage.fillBattleBG( self.screen )
		self.refresh.append( self.screen.get_rect() )
		
		# play battle music
		self.sound.stop('explora')
		self.sound.play("battleMusic", -1 )
		
		self.inBattle = True
		self.player.enterBattle()
		self.fa.enterBattle()
		self.zen.enterBattle()
		
		# build list of battle participants
		self.battleParticipants= [ self.mel, self.fa, self.zen ]
		self.currentBattleTurn = 0
# 		self.mel.attacking = True
		
		self.livePlayers = [ self.mel, self.fa, self.zen ]
		
		self.spawnEnemies( 3, 1 ) # number, level
		self.enemies[0].select()
		self.selectedEnemyIDX = 0
		
		
		# create dashboard
		self.dashboard = AttackChooser(self.screen)
		self.dashboard.config(self.battleParticipants[self.currentBattleTurn])
		self.dashboard.draw()
		
		print 'enter battle'
		
		# reset stored points for new battle
		self.storedPoints = 0
		
		# if Charles is currently playable
		if charles:
			self.cha.enterBattle()
			self.battleParticipants.append( self.cha )
			self.livePlayers.append( self.cha )
		
# 		for chara in self.livePlayers:
# 			print 'drew', chara.name, 'hp bar at', chara.hpbarBG
	
		self.refresh.append( self.screen.get_rect() ) # possible fix for health bar issues?
	
	# changes game state back to exploration mode
	def leaveBattle( self ):
		# stop battle music
		self.sound.stop("battleMusic")
		self.sound.play('explora', -1)
		
		self.inBattle = False
		self.stage.moveCamView( self.screen, self.refresh, self.camera )
		self.stage.stepsTaken = 0 # reset steps
		
		self.player.leaveBattle()
		
		self.enemies = [] # empty enemies list
		self.selectedEnemyIDX = -1
		self.battleParticipants = []
		print 'leave battle'
	
	# displays the given PlayableCharacter's stats at the given position on the stat screen
	def showCharaStats( self, chara, pos ):
		stats = chara.getStats()
		
		lines = [ chara.name ]
		lines.append( ' - time:     ' + str( stats[0] ) )
		lines.append( ' - hp:       ' + str( stats[1] ) )
		lines.append( ' - attack:   ' + str( stats[2] ) )
		lines.append( ' - defense:  ' + str( stats[3] ) )
		lines.append( ' - speed:    ' + str( stats[4] ) )
		lines.append( ' - accuracy: ' + str( stats[5] ) )
		lines.append( ' - xp:       ' + str( stats[6] ) )
		lines.append( ' - level:    ' + str( stats[7] ) )
		
		for idx in range( len ( lines ) ):
			lineText = self.smallFont.render( lines[idx], True, white )
			lineHeight = 22
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
	
	def enterDialogue(self):
		#move to next convo every time enterDialogue is called
		#so that story moves sequentially
		self.inDialogue = True  
		#self.stage.fillBG( self.screen, self.refresh ) # for code without scrolling
		self.stage.moveCamView( self.screen, self.refresh, self.camera )
		self.player.draw( self.screen )
		self.gameConvo.displayText( self.convoNum )
		print "ENTERED DIALOGUE"
	
	# updates the game for one time-step (when the player is playing through a stage)
	def update( self ):
		if self.onStatScreen:
			self.updateStatScreen()
		elif self.inBattle:
			self.updateBattle()
		elif self.inDialogue:   
			self.updateDialogue()
		else:
			self.updateExplore()
		
		pygame.display.update( self.refresh )
		
		# clear out the refresh rects
		self.refresh = []
		
		# throttle the game speed to 30fps
		self.gameClock.tick(30)
		
	# parses keyboard input for exploration mode and updates screen contents
	def updateExplore( self ):
		
		#print '\ntime step', self.timeStep # for testing
		self.timeStep += 1
		moved = False # whether the player moved this time-step
		keydown = False
		
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
					keydown = True
					break
				elif event.key == pygame.K_DOWN:
					self.player.goForward( self.tileSize )
					moved = True
					keydown = True
					break
				elif event.key == pygame.K_LEFT:
					self.player.goLeft( self.tileSize )
					moved = True
					keydown = True
					break
				elif event.key == pygame.K_RIGHT:
					self.player.goRight( self.tileSize )
					moved = True
					keydown = True
					break
				
				elif event.key == pygame.K_b: # temporary easy trigger for battle
					self.enterBattle()
					keydown = True
					break
				elif event.key == pygame.K_c: # temporary easy trigger for dialogue
					self.enterDialogue()
					return
			
			if event.type == pygame.QUIT:
				sys.exit()
		
		# for when the key is held down
		if not keydown: # only check if there isn't a new button down
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
		
		# stop movement if it leads to collision
		self.stage.collide( self.player )
			#print 'collided!'
		
		# check for entering a door
		door = self.stage.atDoor( self.player )
		if door != None:
			# if entering a door, determine which room the door leads to
			if door.room == 'robotics lab':
				if self.player.movement[0] == left: # make sure player is going in the correct direction
					self.enterRoboLabStage()
			elif door.room == 'hallway': # if entering the hallway, determine from which room
				if self.stage == self.roboLabStage and self.player.movement[0] == right:
					self.enterHallwayStageLeft()
		
		# update screen contents
		
		walked = self.player.update() # whether player actually walked across screen
		if walked:
			self.stage.addStep()
			
			# if player is going out of bounds, move camera view and player's onscreen position
			eraseRect = self.placePlayerOnScreen()
			newScreenPos = self.player.getPosition()
			
			buffer = 180 # distance from edge of screen at which it starts scrolling
			shift = 10 # distance the camera moves in one time-step when it scrolls (should match one step for player)
			
			# move camera to left
			if newScreenPos[0] <= buffer and not self.stage.approachingLeftWall( self.player, buffer ):
				self.camera = self.camera.move( -shift, 0 )
				self.stage.moveCamView( self.screen, self.refresh, self.camera )
			
			# move camera to right
			elif self.player.rightEdge >= self.screenSize[0] - buffer and not self.stage.approachingRightWall( self.player, buffer ):
				self.camera = self.camera.move( shift, 0 )
				self.stage.moveCamView( self.screen, self.refresh, self.camera )
			
			# move camera up
			elif newScreenPos[1] <= buffer and not self.stage.approachingTopWall( self.player, buffer ):
					self.camera = self.camera.move( 0, -shift )
					self.stage.moveCamView( self.screen, self.refresh, self.camera )
			
			# move camera down
			elif self.player.bottomEdge >= self.screenSize[1] - buffer and not self.stage.approachingBottomWall( self.player, buffer ):
				self.camera = self.camera.move( 0, shift )
				self.stage.moveCamView( self.screen, self.refresh, self.camera )
			
			# otherwise update display normally
			else:
				# erasing when moving up with no scrolling was incorrect for some reason
				if self.player.orientation == back:
					eraseRect = eraseRect.move( 0, 5 )
				
				self.stage.fillBG( self.screen, self.refresh, eraseRect, self.camera )
				self.refresh.append( self.player.getRect() )
			
			self.placePlayerOnScreen() # arrrrrrrrgh
		
		elif moved: # if player was given a movement command but did not walk
			eraseRect = self.placePlayerOnScreen()
			self.stage.fillBG( self.screen, self.refresh, eraseRect, self.camera )
			self.refresh.append( self.player.getRect() )
		
# 		else: # otherwise, player did not move at all, can trigger battle
# 			probBattle = ( self.stage.stepsTaken % 1000 ) / float( 1000 )
# 			if random.random() < probBattle:
# 				self.enterBattle()
		
		self.player.draw( self.screen )
		self.refresh.append( self.player.getRect() )
	
	# determines enemy attack for an enemy turn in battle
	# returns whether the turn ended the battle
	def enemyTurn( self ):
		# randomly select a livePlayer and attack
		target = random.choice( self.livePlayers )
		self.battleParticipants[self.currentBattleTurn].attack( target, 50 ) # to always win
		
		# play attack sound
		self.sound.play('zong')
		
		if not target.isDead(): # if the target is still alive, pass on turn index
			self.passOnTurn()
		
		# if the attack was fatal, remove that character from the lists
		# do not pass on turn here, because removing player makes indices for enemies go one down
		else:
			print '--died: ' + target.name
			
			self.battleParticipants.remove( target )
			self.livePlayers.remove( target )
			
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
			print 'you lose the battle!'
			return True
		else:
			return False
	
	# moves the battle turn to the next character
	def passOnTurn( self ):
# 		prev = self.battleParticipants[self.currentBattleTurn]
# 		if prev.getType() == 'PlayableCharacter':
# 			prev.attacking = False
		
		# pass on battle turn
		self.currentBattleTurn += 1
		if self.currentBattleTurn > len( self.battleParticipants ) - 1: # wrap around to front of list
			self.currentBattleTurn = 0
		
		if self.battleParticipants[self.currentBattleTurn].getType() == 'PlayableCharacter':
			# increment character's turn count
			self.battleParticipants[self.currentBattleTurn].turns += 1
			
			# update character's temp stats
			self.battleParticipants[self.currentBattleTurn].updateStats()
			
			# reconfigure dashboard
			self.dashboard.config(self.battleParticipants[self.currentBattleTurn])
			self.dashboard.draw() # is this necessary?
		
# 		next = self.battleParticipants[self.currentBattleTurn]
# 		if next.getType() == 'PlayableCharacter':
# 			next.attacking = True
		
# 		print '\ncurrent battle turn is', self.battleParticipants[self.currentBattleTurn].name + ',', \
# 			self.currentBattleTurn, 'out of', len( self.battleParticipants), 'left'
	
	# for wins: awards the currently stored amount of XP to all player characters who are still alive
	def awardXP( self ) :
		for chara in self.livePlayers:
			chara.increaseXP( self.storedPoints )
			
			# check for leveling up
			if chara.xp >= chara.level * 100:
				chara.levelUp(self)
				print 'leveled up', chara.name, 'to level', chara.level
	
	# parses keyboard input for battle mode and updates screen contents
	def updateBattle( self ):
		done = False
		
		attacker = self.battleParticipants[self.currentBattleTurn]
		if attacker.getType() == 'PlayableCharacter':
			playerTurn = True
			attacker.attacking = True # make blue box appear
		else:
			playerTurn = False
			#print 'enemy turn'
		
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
					elif event.key == pygame.K_LEFT:
						self.dashboard.switchAtk(-1)
						self.dashboard.draw()
					elif event.key == pygame.K_RIGHT:
						self.dashboard.switchAtk(1)
						self.dashboard.draw()
					
					
					# attack currently selected enemy
					elif event.key == pygame.K_a:
						target = self.enemies[self.selectedEnemyIDX]
						
						self.dashboard.attack().attack(target, self.battleParticipants[self.currentBattleTurn])
						
						attacker.attacking = False # make box disappear
						self.passOnTurn()
						
						# play attack sound
						self.sound.play('pew')
						
						# if attack killed target
						if target.isDead():
							print '--died: ' + target.name
							
							toRemove = self.enemies.pop( self.selectedEnemyIDX )
							self.battleParticipants.remove( toRemove )
							self.selectedEnemyIDX = 0 # reset selection to 0
							
							# add points for kill to stored total
							self.storedPoints += toRemove.level * 10
							
							# erase killed target
							eraseRect = toRemove.getRect()
							eraseRect.width += 12
							eraseRect.height += 12
							self.stage.fillBattleBG( self.screen, eraseRect )
						
							if len( self.enemies ) != 0: # if still enemies, reselect first one
								self.enemies[0].select()
							else: # if all enemies are gone
								self.awardXP()
								self.leaveBattle()
								done = True
								print 'you win the battle!'
								
								self.stage.addBattle()
								if self.stage.completed():
									print 'this stage has been completed'
			
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
						self.dashboard.draw()
					else: # redraw stage
						self.stage.fillBG( self.screen, self.refresh, self.statBGRect, self.camera)
						self.player.draw( self.screen )
						self.refresh.append( self.player.getRect() )
			
			if event.type == pygame.QUIT:
				sys.exit()
	
	#continues to next box in dialogue	
	def updateDialogue(self):
		#print "IN UPDATE DIALOGUE"
		if self.gameConvo.convoOver == True:
			#print "EXITING DIALOGUE"
			self.inDialogue = False
			#self.stage.fillBG( self.screen, self.refresh) # for code without scrolling
			self.stage.moveCamView( self.screen, self.refresh, self.camera )
			self.player.draw( self.screen )
			self.refresh.append( self.player.getRect() )
			self.convoNum += 1
		else:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_c:
						#print "UPDATING DIALOGUE"
						if self.gameConvo.convoOver != True:
							#print "STILL MORE TEXT"
							#draw BG again first
							#self.stage.fillBG( self.screen, self.refresh) # for code without scrolling
							self.stage.moveCamView( self.screen, self.refresh, self.camera )
							self.player.draw( self.screen )

							self.gameConvo.advanceText()
						
				if event.type == pygame.QUIT:
					sys.exit()





