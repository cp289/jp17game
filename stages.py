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
from main import exitGame
from message import Message, MessageDisplay

# some useful variables for the rest of this file
back, front, left, right, none = range( 5 )
green = ( 150, 180, 160 )
white = ( 255, 255, 255 )
blue = ( 0, 1, 171 )

'''
This class represents one stage/room of the game.
It stores its furniture and walls as Things.
'''
class Stage:
	
	# fields: number battles to win, background images, list of Thing contents, Surface screen
	
	# creates a new Stage with the given number of battles to win and background image
	# optional to give starting player Position on stage and starting camera position (upper left corner)
	def __init__( self, name, numBattles, scale, bg, battleBG, bugs, enemyLevel = 1 ):
		self.name = name
		self.numBattles = numBattles
		self.battlesCompleted = 0
		self.background = bg
		self.battleBG = battleBG
		self.scale = scale
		
		self.contents = pygame.sprite.Group()
		self.doors = []
		self.bugImgs = bugs
		self.enemyLevel = enemyLevel # level of all enemies generated in this stage
		
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
		return self.battlesCompleted >= self.numBattles
	
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
	def __init__( self, screen, sound ):
		# create a screen (width, height)
		self.screenSize = ( screen.get_width(), screen.get_height() )
		self.screen = screen
		
		self.refresh = [] # list of rectangles that currently should be updated in the display
		self.tileSize = 50
		
		# game clock
		self.gameClock = pygame.time.Clock()
		
		# boolean fields for game state
		self.inBattle = False
		self.inStoryBattle = False # whether we're currently in a story battle
		self.holdBattle = False # whether battle screen should be held for animations to finish
		self.inDialogue = False
		self.onStatScreen = False
		
		# boolean fields for game progress
		self.inIntro = False
		self.hallwaySafe = False
		self.gotCharles = False
		self.charlesBattle = False # whether the battle with Charles' bugs has been triggered
		self.key2Battle = False # whether the battle for the second key has been triggered
		self.gotKey2 = False
		self.inBossBattle = False
		self.gameComplete = False # used by main.py to determine when to stop calling update
		
		self.mel = None
		self.fa = None
		self.zen = None
		self.cha = None
		self.initPlayers()
		self.player = self.mel
		self.allPlayers = [ self.mel, self.fa, self.zen ]
		
		# variables for battle mode
		self.battlesWon = 0
		self.battlesLost = 0
		self.timesFled = 0
		self.battleParticipants = [] # list to loop through for battle turns
		self.currentBattleTurn = -1 # stores index of current turn within battleParticipants
		self.livePlayers = [] # stores players who are currently alive so that enemies can choose targets easily
		self.storedPoints = 0 # amount of XP all live players will gain on winning the current battle
		
		self.enemies = [] # start out with no enemies, because not in battle
		self.selectedEnemyIDX = -1 # index of current selected enemy
		bossBugIMGorig = pygame.image.load( 'images/bugs/Boss Bug.png' ).convert_alpha()
		self.bossBugIMG = pygame.transform.scale( bossBugIMGorig, ( 283, 262 ) )
		
		self.camera = pygame.Rect( ( 0, 0 ), self.screenSize ) # represents current section of stage in view
		self.stage = None # set by calling the methods for entering stages
		self.hallwayStage = None # these three are created when the loading methods are called
		self.roboLabStage = None
		self.macLabStage = None
		
		# load specific screen backgrounds
		statBGorig = pygame.image.load( 'images/backgrounds/statScreenBG.png' ).convert_alpha()
		self.statBG = pygame.transform.scale( statBGorig, self.screenSize )
		self.statBGRect = pygame.Rect( ( 0, 0 ), ( self.screenSize[0], self.screenSize[1] ) )
		
		scale = 0.5
		bgOrig = pygame.image.load( 'images/backgrounds/Davis Hallway.png' ).convert_alpha()
		newDim = ( int( bgOrig.get_width() * scale ), int( bgOrig.get_height() * scale ) )
		self.hallwayBG = pygame.transform.scale( bgOrig, newDim ) # rescales the background image
		self.introBG = self.hallwayBG
		
		melRoomBGorig = pygame.image.load( 'images/backgrounds/Melody\'s Room.png' ).convert_alpha()
		ratio = float( self.screenSize[0] ) / melRoomBGorig.get_width()
		adjustedHeight = int( melRoomBGorig.get_height() * ratio )
		self.melRoomBG = pygame.transform.scale( melRoomBGorig, ( self.screenSize[0], adjustedHeight ) )
		
		bossBattleBGorig = pygame.image.load( 'images/backgrounds/FinalRoom.png' ).convert_alpha()
		self.bossBattleBG = pygame.transform.scale( bossBattleBGorig, self.screenSize )
		
		# makes boxes for the characters on the stat screen
		offset = 20
		boxWidth = ( self.statBGRect.width - 3 * offset ) / 2
		boxHeight = ( self.statBGRect.height - 3 * offset ) / 2
		self.melBox = pygame.Rect( ( offset, offset ), ( boxWidth, boxHeight ) )
		self.faBox = pygame.Rect( ( offset, 2 * offset + boxHeight ), ( boxWidth, boxHeight ) )
		self.zenBox = pygame.Rect( ( 2 * offset + boxWidth, offset ), ( boxWidth, boxHeight ) )
		self.chaBox = pygame.Rect( ( 2 * offset + boxWidth, 2 * offset + boxHeight ), ( boxWidth, boxHeight ) )
		
		# create fonts
		self.bigFont = pygame.font.SysFont( 'Helvetica', 44, bold=True )
		self.smallFont = pygame.font.SysFont( 'Helvetica', 18 )
		self.nameFont = pygame.font.SysFont( "Helvetica", 32, bold=True )
		self.convoFont = pygame.font.SysFont( "Helvetica", 28, bold=True )
		
		# load sound object
		self.sound = sound
		
		# init Conversation object
		self.initConvo()
		self.convoNum = 0
		
		# init Message object
		self.messages = MessageDisplay(self.screen)
		
		# load sound object
		self.sound = sound
		
		# mostly for testing
		self.timeStep = 0
	
	# creates the PlayableCharacters in the game
	def initPlayers( self ):
		
		# the given image list should contain six lists: standing, walking, battle, attacking, dying, and other
		# the standing list contains the standing images in the order: front, back, left, right
		# the walking, attacking, and dying lists are animation frames in orders
		# the battle list contains two frames for idle, and two frames for taking damage
		# the other list contains: status, conversation heads
		
		# Melody: 0.5, 0.2, 0.2, 0.5
		# Fatimah: 0.2, 0.1, 0.1, 0.1, 0.5
		# Zena: 0.5, 0.1, 0.1, 0.5
		# Charles: 0.5, 0.5, 0.2, 0.2, 0.5
		
		# load images
		playerL = pygame.image.load( 'images/Melody/Walk/Left/MelodyLeftStand.png' ).convert_alpha()
		playerR = pygame.image.load( 'images/Melody/Walk/Right/MelodyRightStand.png' ).convert_alpha()
		playerF = pygame.image.load( 'images/Melody/Walk/Down/MelodyDownStand.png' ).convert_alpha()
		playerB = pygame.image.load( 'images/Melody/Walk/Up/MelodyUpStand.png' ).convert_alpha()
		playerS = pygame.image.load( 'images/Melody/MelodyStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/Melody/MelodyHead.png" ).convert_alpha()
		standlist = ( playerF, playerB, playerL, playerR )
		walkF = 'images/Melody/Walk/Down/MelodyDownWalk'
		walkB = 'images/Melody/Walk/Up/MelodyUpWalk'
		walkL = 'images/Melody/Walk/Left/MelodyLeftWalk'
		walkR = 'images/Melody/Walk/Right/MelodyRightWalk'
		walklist = ( walkF, walkB, walkL, walkR )
		battlelist = 'images/Melody/Attack/MelodyIdle'
		attacklist = 'images/Melody/Attack/MelodyAttack'
		dielist = ( 'images/Melody/Death/MelodyDeath', ( 0.5, 0.2, 0.2, 0.5 ) )
		otherlist = ( playerS, playerC )
		
		# initialize mel
		initpos = ( 300, 400 )
		battlePos = ( 560, 50 )
		namePos = ( 25, -1 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.mel = agents.PlayableCharacter( initpos, battlePos, imglist, 'Melody', self, namePos )
		self.mel.setAllStats( ( 500, 54, 44, 43, 50, 12 ) )
		# total HP, ATK, DFN, SPD, ACC, time
		self.mel.setAllGR( ( 0.8, 0.9, 0.85, 0.75, 0.7 ) )
		# HP, ATK, DFN, SPD, ACC
		
		standlist = None
		walklist = None

		#initialize fa
		battlelist = 'images/Fatimah/Attack/FatimahIdle'
		attacklist = 'images/Fatimah/Attack/FatimahAttack'
		dielist = ( 'images/Fatimah/Death/FatimahDeath', ( 0.2, 0.1, 0.1, 0.1, 0.5 ) )
		playerS = pygame.image.load( 'images/Fatimah/FatimahStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/Fatimah/FatimahHead.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		battlePos = ( 460, 140 )
		namePos = ( 15, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.fa = agents.PlayableCharacter( initpos, battlePos, imglist, 'Fatimah', self, namePos)
		self.fa.setAllStats( ( 425, 46, 54, 51, 50, 11 ) )
		self.fa.setAllGR( ( 0.85, 0.9, 0.8, 0.7, 0.75 ) )
		
		# initialize zen
		battlelist = 'images/Zena/Attack/ZenaIdle'
		attacklist = 'images/Zena/Attack/ZenaAttack'
		dielist = ( 'images/Zena/Death/ZenaDeath', ( 0.5, 0.1, 0.1, 0.5 ) )
		playerS = pygame.image.load( 'images/Zena/ZenaStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/Zena/ZenaHead.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		battlePos = ( 360, 230 )
		namePos = ( 40, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.zen = agents.PlayableCharacter( initpos, battlePos, imglist, 'Zena', self, namePos )
		self.zen.setAllStats( ( 450, 49, 48, 54, 45, 14 ) )
		self.zen.setAllGR( ( 0.8, 0.75, 0.85, 0.9, 0.7 ) )
		
		# initialize cha
		battlelist = 'images/Charles/Attack/CharlesIdle'
		attacklist = 'images/Charles/Attack/CharlesAttack'
		dielist = ( 'images/Charles/Death/CharlesDeath', ( 0.5, 0.5, 0.2, 0.2, 0.5 ) )
		playerS = pygame.image.load( 'images/Charles/CharlesStatPic.png' ).convert_alpha()
		playerC = pygame.image.load( "images/Charles/CharlesHead.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		battlePos = ( 260, 289 )
		namePos = ( 20, 0 )
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.cha = agents.PlayableCharacter( initpos, battlePos, imglist, 'Charles', self, namePos )
		self.cha.setAllStats( ( 500, 44, 49, 44, 54, 12 ) )
		self.cha.setAllGR( ( 0.75, 0.7, 0.8, 0.9, 0.85 ) )
		
		"""
		Initialize non-playable characters who just take part in convos
		"""
		#initalize chaEvil
		playerC = pygame.image.load( "images/Charles/PossessedCharles.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		namePos = [ 9, 0 ]
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.chaEvil = agents.SpeakingCharacter( initpos, playerC, 'Charles?', namePos )
		
		#initialize bru
		playerC = pygame.image.load( "images/Bruce/BruceHead.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		namePos = [ 33, 0 ]
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.bru = agents.SpeakingCharacter( initpos, playerC, 'Bruce', namePos )
		
		#initialize bruEvil
		playerC = pygame.image.load( "images/Bruce/BruceHeadEvil.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		namePos = [ 24, 0 ]
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.bruEvil = agents.SpeakingCharacter( initpos, playerC, 'Bruce?', namePos )
		
		#initialize NPE
		playerC = pygame.image.load( "images/bugs/BossBugSilhouette.png" ).convert_alpha()
		otherlist = ( playerS, playerC )
		namePos = [ 44, 0 ]
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.NPE = agents.SpeakingCharacter( initpos, playerC, 'NPE', namePos )
		
		playerC = None 
		
		#initialize stu1
		otherlist = ( playerS, playerC )
		namePos = [ 1, 0 ]
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.stu1 = agents.SpeakingCharacter( initpos, playerC, 'Student_1', namePos )
		
		#initialize stu2
		otherlist = ( playerS, playerC )
		namePos = [ 1, 0 ]
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.stu2 = agents.SpeakingCharacter( initpos, playerC, 'Student_2', namePos )
		
		#initialize CSC
		otherlist = ( playerS, playerC )
		namePos = [ 15, 0 ]
		imglist = [ standlist, walklist, battlelist, attacklist, dielist, otherlist ]
		self.CSC = agents.SpeakingCharacter( initpos, playerC, 'CS_Child', namePos )
		
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
		
		# hallway bg is now initialized in constructor
		
		battleBGorig = pygame.image.load( 'images/backgrounds/Hallway Battle.png' ).convert_alpha()
		battleBG = pygame.transform.scale( battleBGorig, self.screenSize )
		
		bugImgs = [ pygame.image.load( 'images/bugs/Bug 0.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 10.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 11.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 100.png' ).convert_alpha()
						]
		
		self.hallwayStage = Stage( 'hallway', 1, scale, self.hallwayBG, battleBG, bugImgs )
		
		# create doors
		
		doorToRoboLab = agents.Door( ( 0, 1310 * scale ), ( 10, 140 * scale ), 'robotics lab' )
		self.hallwayStage.addDoor( doorToRoboLab )
		
		doorToMacLab = agents.Door( ( 2760 * scale, self.hallwayStage.height - 10 ), ( 100 * scale, 10 ), 'mac lab' )
		self.hallwayStage.addDoor( doorToMacLab )
		
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
	
	# changes current stage to hallway and places player and camera at starting positions
	def enterHallwayStageBottom( self ):
		self.stage = self.hallwayStage
		
		# set initial player and camera positions for this room
		self.camera.topleft = 2300 * self.stage.scale, 2065 * self.stage.scale
		initPos = ( 2760 * self.stage.scale, 2820 * self.stage.scale )
		
		self.player.setStagePos( initPos[0], initPos[1] )
		self.placePlayerOnScreen()
		
		self.player.goBackward( self.tileSize )
		
		self.hallwayStage.moveCamView( self.screen, self.refresh, self.camera )
		self.player.draw( self.screen )
		pygame.display.update()
		
		print 'enter hallway from bottom'
	
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
		
		self.roboLabStage = Stage( 'robotics lab', 4, scale, bg, battleBG, bugImgs, 2 )
		
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
		scale = 0.5
		
		bgOrig = pygame.image.load( 'images/backgrounds/Davis Mac Lab.png' ).convert_alpha()
		newDim = ( int( bgOrig.get_width() * scale ), int( bgOrig.get_height() * scale ) )
		bg = pygame.transform.scale( bgOrig, newDim ) # rescales the background image
		
		battleBGorig = pygame.image.load( 'images/backgrounds/Davis Mac Lab Battle.png' ).convert_alpha()
		battleBG = pygame.transform.scale( battleBGorig, self.screenSize )
		
		bugImgs = [ pygame.image.load( 'images/bugs/Bug 1010.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1011.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1100.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1101.png' ).convert_alpha()
						]

		self.macLabStage = Stage( 'mac lab', 5, scale, bg, battleBG, bugImgs, 4 )

		#def __init__( self, pos, dim, room ):
		doorToHallway = agents.Door( (  235 * scale, 800 * scale ), \
			( 150 * scale, 10 * scale ), 'hallway' )
		self.macLabStage.addDoor( doorToHallway )
		
		# create walls
		lWall = pygame.Surface( ( 5, self.macLabStage.height ) )
		lWall.set_alpha( 0 ) # set image transparency
		leftWall = agents.Thing( ( -5, 0 ), lWall )
		self.macLabStage.addThing( leftWall )
		
		rWall = pygame.Surface( ( 5, self.macLabStage.height ) )
		rWall.set_alpha( 0 ) # set image transparency
		rightWall = agents.Thing( ( self.macLabStage.width - 5, 0 ), rWall )
		self.macLabStage.addThing( rightWall )
		
		topWallHeight = 715 * scale
		self.macLabStage.setTopWallEdge( topWallHeight )
		tWall = pygame.Surface( ( self.macLabStage.width, topWallHeight ) )
		tWall.set_alpha( 0 ) # set image transparency
		topWall = agents.Thing( ( 0, 0 ), tWall )
		self.macLabStage.addThing( topWall )
	
		bWall = pygame.Surface( ( self.macLabStage.width, 5 ) )
		bWall.set_alpha( 0 ) # set image transparency
		bottomWall = agents.Thing( ( 0, self.macLabStage.height ), bWall )
		self.macLabStage.addThing( bottomWall )
		
		# tables in quadrants 1 and 2
		tTabDim = ( 2900 * scale, 150 * scale )
		tTabPos = ( 950 * scale, 800 * scale )
		tTable = pygame.Surface( tTabDim )
		topHalfTable = agents.Thing( tTabPos, tTable )
		self.macLabStage.addThing( topHalfTable )

		bTabDim = ( 290 * scale, 450 * scale )
		bTabPos = ( 960 * scale, 800 * scale )
		bTable = pygame.Surface( bTabDim )
		bottomHalfTable = agents.Thing( bTabPos, bTable )
		self.macLabStage.addThing( bottomHalfTable )
		
		bTabDim2 = ( 290 * scale, 450 * scale )
		bTabPos2 = ( 1875 * scale, 800 * scale )
		bTable2 = pygame.Surface( bTabDim2 )
		bottomHalfTable2 = agents.Thing( bTabPos2, bTable2 )
		self.macLabStage.addThing( bottomHalfTable2 )

		bTabDim3 = ( 290 * scale, 450 * scale )
		bTabPos3 = ( 2790 * scale, 800 * scale )
		bTable3 = pygame.Surface( bTabDim2 )
		bottomHalfTable3 = agents.Thing( bTabPos3, bTable3 )
		self.macLabStage.addThing( bottomHalfTable3 )

		bTabDim4 = ( 290 * scale, 1628 * scale )
		bTabPos4 = ( 3715 * scale, 800 * scale )
		bTable4 = pygame.Surface( bTabDim4 )
		bottomHalfTable4 = agents.Thing( bTabPos4, bTable4 )
		self.macLabStage.addThing( bottomHalfTable4 )

		# tables in center of background
		cTabDim = ( 820 * scale, 600 * scale )
		cTabPos = ( 669 * scale, 1725 * scale )
		cTable = pygame.Surface( cTabDim )
		centerTable = agents.Thing( cTabPos, cTable )
		self.macLabStage.addThing( centerTable )

		cTabDim2 = ( 820 * scale, 605 * scale )
		cTabPos2 = ( 2235 * scale, 1735 * scale )
		cTable2 = pygame.Surface( cTabDim2 )
		centerTable2 = agents.Thing( cTabPos2, cTable2 )
		self.macLabStage.addThing( centerTable2 )

		# tables in quadrants 3 and 4
		tTabDim2 = ( 290 * scale, 450 * scale )
		tTabPos2 = ( 960 * scale, 2820 * scale )
		tTable2 = pygame.Surface( tTabDim2 )
		topHalfTable2 = agents.Thing( tTabPos2, tTable2 )
		self.macLabStage.addThing( topHalfTable2 )

		tTabDim3 = ( 290 * scale, 450 * scale )
		tTabPos3 = ( 1875 * scale, 2820 * scale )
		tTable3 = pygame.Surface( tTabDim3 )
		topHalfTable3 = agents.Thing( tTabPos3, tTable3 )
		self.macLabStage.addThing( topHalfTable3 )

		tTabDim4 = ( 290 * scale, 450 * scale )
		tTabPos4 = ( 2790 * scale, 2820 * scale )
		tTable4 = pygame.Surface( tTabDim3 )
		topHalfTable4 = agents.Thing( tTabPos4, tTable4 )
		self.macLabStage.addThing( topHalfTable4 )

		tTabDim5 = ( 290 * scale, 450 * scale )
		tTabPos5 = ( 3715 * scale, 2820 * scale )
		tTable5 = pygame.Surface( tTabDim5 )
		topHalfTable5 = agents.Thing( tTabPos5, tTable5 )
		self.macLabStage.addThing( topHalfTable5 )

		bTabDim2 = ( 2900 * scale, 400 * scale )
		bTabPos2 = ( 960 * scale, 3096 * scale )
		bTable2 = pygame.Surface( bTabDim2 )
		bottomHalfTable2 = agents.Thing( bTabPos2, bTable2 )
		self.macLabStage.addThing( bottomHalfTable2 )

		# mac monitor that sticks out in bottom row of tables
		macMonDim = ( 180 * scale, 400 * scale )
		macMonPos = ( 2400 * scale, 3050 * scale )
		macMonSur = pygame.Surface( macMonDim )
		macMonitor = agents.Thing( macMonPos, macMonSur )
		self.macLabStage.addThing( macMonitor )

		# black box in left corner
		blackBoxDim = ( 340 * scale, 520 * scale )
		blackBoxPos = ( 0 * scale, 3130 * scale )
		blackBoxSur = pygame.Surface( blackBoxDim )
		blackBox = agents.Thing( blackBoxPos, blackBoxSur )
		self.macLabStage.addThing( blackBox )

		print 'loaded mac lab stage'
	
	# changes current stage to Mac lab and places player and camera at starting positions
	def enterMacLabStage( self ):
		self.stage = self.macLabStage
		
		# set initial player and camera positions for this room
		
		#self.camera.topleft = 2450 * self.stage.scale, 2850 * self.stage.scale # for scale 0.5
		#initPos = ( 3900 * self.stage.scale, 3672 * self.stage.scale )
		
		self.camera.topleft = 50 * self.stage.scale, 100 * self.stage.scale # for scale 0.4
		initPos = ( 275 * self.stage.scale, 500 * self.stage.scale )
			
		self.player.setStagePos( initPos[0], initPos[1] )
		self.placePlayerOnScreen()
		
		self.player.goForward( self.tileSize )
		
		self.macLabStage.moveCamView( self.screen, self.refresh, self.camera )
		self.player.draw( self.screen )
		pygame.display.update()
		
		print 'enter mac lab'
	
	# fills the given rectangle (or the entire screen) with the current intro background
	def fillIntroBG( self, rect = None ):
		if rect == None:
			self.screen.blit( self.introBG, ( 0, 0 ) )
			self.refresh.append( self.screen.get_rect() )
		else:
			self.screen.blit( self.introBG, rect, rect )
			self.refresh.append( rect )
	
	# enters intro
	def start( self ):
		self.inIntro = True
		self.fillIntroBG()
		self.enterDialogue()
		
		pygame.display.update()
		
		print 'start intro'
	
	# updates intro, returns whether intro is complete
	def updateIntro( self ):
		if not self.inDialogue:
			if self.convoNum == 1: # finished hallway conversation, move to my room
				self.screen.blit( self.melRoomBG, ( 0, 0 ) )
				self.introBG = self.melRoomBG
				self.enterDialogue()
			elif self.convoNum == 2: # completed both conversations
				self.inIntro = False
				return True
		else:
			self.updateDialogue()
		
		pygame.display.update( self.refresh )
		
		# clear out the refresh rects
		self.refresh = []
		
		# throttle the game speed to 30fps
		self.gameClock.tick(30)
		
		return False
		
		# if not in convo
		# if convo num is 1, return true
		# otherwise enterDialogue
		# update screen
	
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
			
			print 'created', name, 'at level', level
	
	# changes game state to battle mode
	def enterBattle( self, charles = False, canFlee = True ):
		# update display for background
		self.stage.fillBattleBG( self.screen )
		self.refresh.append( self.screen.get_rect() )
		
		# config messages
		self.messages.setBackground(self.stage.battleBG)
		
		# play battle music
		self.sound.stop('explora')
		self.sound.play("battleMusic", -1 )
		
		self.inBattle = True
		self.player.enterBattle(canFlee)
		self.fa.enterBattle(canFlee)
		self.zen.enterBattle(canFlee)
		
		# build list of battle participants
		self.battleParticipants= [ self.mel, self.fa, self.zen ]
		self.currentBattleTurn = 0
		
		self.livePlayers = [ self.mel, self.fa, self.zen ]
		
		# if Charles is currently playable
		if charles:
			self.cha.enterBattle(canFlee)
			self.battleParticipants.append( self.cha )
			self.livePlayers.append( self.cha )
		
		self.spawnEnemies( 3, self.stage.enemyLevel ) # number, level
		self.enemies[0].select()
		self.selectedEnemyIDX = 0
		
		
		# create dashboard
		self.dashboard = AttackChooser(self.screen)
		self.dashboard.config(self.livePlayers[self.currentBattleTurn])
		
		print 'enter battle'
		
		# reset stored points for new battle
		self.storedPoints = 0
		
		self.refresh.append( self.screen.get_rect() )
	
	# changes game state back to exploration mode
	def leaveBattle( self, win, charles = False ):
		# stop battle music
		self.sound.stop("battleMusic")
		self.sound.stop("enemy")
		
		# play win music
		if win:
			self.sound.play("win")
# 			while self.sound.busy():
# 				pass
		
		# return to exploration music
		self.sound.play('explora', -1)
		
		players = [self.mel, self.fa, self.zen]
		if charles == True:
			players.append(self.cha)
			
		#reset current time left
		for player in players:
			player.leaveBattleStatsReset()
			player.fillTime()
		
		self.inBattle = False
		self.holdBattle = False
		self.stage.moveCamView( self.screen, self.refresh, self.camera )
		self.stage.stepsTaken = 0 # reset steps
		
		# reset HP and time for all player characters
		for chara in players:
			chara.leaveBattle()
		
		self.enemies = [] # empty enemies list
		self.selectedEnemyIDX = -1
		self.battleParticipants = []
		
		if self.inStoryBattle:
			if not win: # if a story battle has been lost
				self.showReplayScreen()
				self.runReplayScreen()
				return # do not run checks below
			else: # otherwise no longer in story battle
				self.inStoryBattle = False
		
		if self.stage == self.hallwayStage: # if we're leaving the hallway battle, now make the hallway safe
			self.hallwaySafe = True
			self.enterDialogue() # enter convo 3
		elif self.charlesBattle and not self.gotCharles: # if leaving battle with Charles, unlock him
			self.gotCharles = True
			self.levelCharles()
			self.allPlayers.append( self.cha )
			self.enterDialogue() # convo 6
		elif self.stage == self.macLabStage and self.stage.battlesCompleted == 1 and self.convoNum == 8: # after first Mac lab battle
			self.enterDialogue() # convo 8
		elif self.key2Battle and not self.gotKey2:
			self.gotKey2 = True
			self.enterDialogue() # convo 10
		
		print 'leave battle'
	
	# Make Charles the same level as the average party level
	def levelCharles( self ):
		levelList = [ self.mel.level, self.fa.level, self.zen.level ]
		avg = sum( levelList ) / len( levelList )
		if avg != 1:
			for i in range( avg - 1 ):
				self.cha.levelUp( self )
				self.cha.increaseXP( 100 )
	
	# displays the given PlayableCharacter's stats at the given position on the stat screen
	def showCharaStats( self, chara, pos ):
		stats = chara.getStats()
		
		lines = [ chara.name ]
		lines.append( '   Time:          ' + str( stats[0] ) )
		lines.append( '   HP:            ' + str( stats[1] ) )
		lines.append( '   Confidence:    ' + str( stats[2] ) )
		lines.append( '   Passivity:     ' + str( stats[3] ) )
		lines.append( '   Concentration: ' + str( stats[4] ) )
		lines.append( '   Honesty:       ' + str( stats[5] ) )
		lines.append( '   EXP:           ' + str( stats[6] ) )
		lines.append( '   Level:         ' + str( stats[7] ) )
		
		for idx in range( len ( lines ) ):
			lineText = self.smallFont.render( lines[idx], True, white )
			lineHeight = 22
			linePos = ( pos[0], pos[1] + idx * lineHeight )
			self.screen.blit( lineText, linePos )
		
		lineWidth = 200
		self.screen.blit( chara.getStatusIMG(), ( pos[0] + lineWidth, pos[1] ) )
	
	# draws the current stat screen on the game window
	def showStatScreen( self, charles = False ):
		self.onStatScreen = True
		self.screen.blit( self.statBG, ( 0, 0 ), self.statBGRect )
		
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
	
	# sends the game into dialogue mode for the next stored dialogue
	def enterDialogue(self):
		#move to next convo every time enterDialogue is called
		#so that story moves sequentially
		self.inDialogue = True  

		if self.inIntro:
			self.fillIntroBG()
		elif self.inBossBattle:
			self.fillBossBattleBG()
		else:
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
		self.messages.update()
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
###########################################################################
#				if event.key == pygame.K_j:
#					self.gameComplete = True
###########################################################################
				if event.key == pygame.K_c:
					self.onStatScreen = True
					print 'show stat screen'
					self.showStatScreen( charles = self.gotCharles)
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
			
			if event.type == pygame.QUIT:
				exitGame()
		
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
					if self.stage.completed() and not self.charlesBattle:
						print 'story event: Charles!'
						self.enterDialogue() # convo with Charles
						return # so that characters aren't still drawn over convo
					else:
						self.enterHallwayStageLeft()
				elif self.stage == self.macLabStage and self.player.movement[0] == back:
					self.enterHallwayStageBottom()
			elif door.room == 'mac lab' and self.gotCharles: # only unlock Mac lab after unlocking Charles
				if self.player.movement[0] == front: # make sure player goes in right direction
					self.enterMacLabStage()
		
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
		
		else: # otherwise, player did not move at all, can trigger battle
			if self.stage == self.hallwayStage:
				if not self.hallwaySafe:
					self.enterDialogue() # convo 2 upon entering hallway, enters battle when done
					return # so that characters aren't still drawn over convo
				elif self.charlesBattle and self.key2Battle: # if both story battles in Davis have happened
					self.enterDialogue() # convo 11, which leads to the final boss battle
					return # so that characters aren't still drawn over convo
			elif self.stage == self.roboLabStage and self.stage.battlesCompleted == 0:
				self.enterDialogue() # convo 4 upon entering robotics lab for the first time
				return # so that characters aren't still drawn over convo
			elif self.stage == self.macLabStage:
				if self.stage.battlesCompleted == 0:
					self.enterDialogue() # convo 7 upon entering Mac lab for the first time
					return # so that characters aren't still drawn over convo
				elif self.stage.completed() and not self.key2Battle:
					print 'story event: battle for key 2!'
					self.enterDialogue() # convo 9 after completing Mac lab stage
					return # so that characters aren't still drawn over convo
				else:
					probBattle = ( self.stage.stepsTaken % 1000 ) / float( 1000 )
					if random.random() < probBattle:
						self.enterBattle( charles = self.gotCharles )
			else:
				probBattle = ( self.stage.stepsTaken % 1000 ) / float( 1000 )
				if random.random() < probBattle:
					self.enterBattle( charles = self.gotCharles )
		
		self.player.draw( self.screen )
		self.refresh.append( self.player.getRect() )
	
	# determines enemy attack for an enemy turn in battle
	# returns whether the turn ended the battle
	def enemyTurn( self ):
		# randomly select a livePlayer and attack
		target = random.choice( self.livePlayers )
		self.battleParticipants[self.currentBattleTurn].attack( target, 50 )
		#self.battleParticipants[self.currentBattleTurn].attack( target, 200 ) # to lose really easily
		
		# play attack sound
		self.sound.play('zong')
		
		if not target.isDead(): # if the target is still alive, pass on turn index
			self.passOnTurn()
		
		# if the attack was fatal, remove that character from the lists
		# do not pass on turn here, because removing player makes indices for enemies go one down
		else:
			self.messages.send(target.name+' died!',0.5)
			
			target.timesKilled += 1
			
			self.battleParticipants.remove( target )
			self.livePlayers.remove( target )
			
			# erase killed target
			eraseRect = target.battleRect.copy()
			eraseRect.width += 12
			eraseRect.height += 12
			self.stage.fillBattleBG( self.screen, eraseRect )
			self.refresh.append( eraseRect )
			
			target.die() # start target's death animation
			
			# if indices are now off (which happens when the attacker is the last in the participant list)
			if self.currentBattleTurn == len( self.battleParticipants ):
				self.currentBattleTurn = 0
				p = self.battleParticipants[self.currentBattleTurn]
				if p.getType() == 'PlayableCharacter':
					self.dashboard.config(p)
		
		if len( self.livePlayers ) == 0:
			print 'you lose the battle!'
			return True
		else:
			return False
	
	# moves the battle turn to the next character
	def passOnTurn( self ):
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
	
	# displays blue screen of death for when you lose a story battle
	def showReplayScreen( self ):
		self.screen.fill( blue )
		
		text = self.bigFont.render( 'YOU LOST.', True, white )
		text2 = self.bigFont.render( 'PRESS V TO REPLAY.', True, white )
		self.screen.blit( text, ( 200, 200 ) )
		self.screen.blit( text2, ( 200, 300 ) )
		
		pygame.display.update()
	
	# runs a loop until player presses v to restart the story battle
	def runReplayScreen( self ):
		replay = False
		while not replay:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_v:
						replay = True
						self.enterBattle( False, self.gotCharles )
				if event.type == pygame.QUIT:
					exitGame()
	
	# for wins: awards the currently stored amount of XP to all player characters who are still alive
	def awardXP( self ) :
		for chara in self.livePlayers:
			#level cap is 10
			if chara.level != 10:
				chara.increaseXP( self.storedPoints )
				# check for leveling up
				if chara.xp >= chara.level * 100:
					chara.levelUp(self)
					print 'leveled up', chara.name, 'to level', chara.level

	
	# parses keyboard input for battle mode and updates screen contents
	def updateBattle( self ):
		done = False
		
		if not self.holdBattle: # if battle has not been held (i.e. lost)
		
			#check if we can and should flee
			for player in self.livePlayers:
				if player.escaped == True:
					#self.messages.send("You Escaped!",0.5) causes erasing error
					player.escaped = False
					done = True
					self.leaveBattle(False, self.gotCharles)
					self.timesFled += 1
					return
		
			attacker = self.battleParticipants[self.currentBattleTurn]
			if attacker.getType() == 'PlayableCharacter':
				playerTurn = True
			else:
				playerTurn = False
				#print 'enemy turn'
		
			# parse keyboard/mouse input events
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN: # for initial key presses
				
					# if it's the player's turn, check for other input
					if playerTurn:
						if attacker.attacking == 0: # if they haven't input something they can use
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
							elif event.key == pygame.K_RIGHT:
								self.dashboard.switchAtk(1)
#################################################################################
							elif event.key == pygame.K_e: # temp battle win key
								self.awardXP()
								done = True
								print 'you win the battle!'
						
								self.battlesWon += 1
								self.leaveBattle( True, charles = self.gotCharles )
								print 'battles won:', self.battlesWon
						
								if self.inBossBattle: # won the boss battle! go to end screen
									self.enterDialogue() # trigger final congratulatory conversation
									return
						
								self.stage.addBattle()
#################################################################################
					
							# attack currently selected enemy
							elif event.key == pygame.K_v:
						
								#don't allow attack if cost is greater than time left
								if self.dashboard.attack().timeNeeded > attacker.time:
									self.messages.send("Not Enough Time!",0.5)
									return
								#don't allow stat-boost stacking
								if self.dashboard.attack().name == "Read Over Project":
									if attacker.ATKBoostTurnsLeft != 0:
										self.messages.send("Stats Already Boosted!",0.5)
										return
									if self.dashboard.attack().name == "Read Code":
										if attacker.DFNBoostTurnsLeft != 0:
											self.messages.send("Stats Already Boosted!",0.5)
											return          
						
								#don't allow restoring full HP
								if self.dashboard.attack().name == "Take a Break":
									if attacker.hp == attacker.totalHP:
										self.messages.send("HP Is Already Full!",0.5)
										return
								
								#don't allow restoring full time
								if self.dashboard.attack().name == "Cancel Plans":
									if attacker.time == attacker.maxTime:
										self.messages.send("Time Is Already Full!",0.5)
										return
						
								attacker.startAttack() # starts attack animation
			
				if event.type == pygame.QUIT:
					exitGame()
		
			# if player has attacked and animation is done
			if playerTurn and attacker.attacking == 2: # if player has chosen an attack and animation is finished
				target = self.enemies[self.selectedEnemyIDX]
				self.dashboard.attack().attack(target, self.battleParticipants[self.currentBattleTurn])
			
				print '----ENDING ATTACK----'
			
				self.passOnTurn()
				attacker.attacking = 0 # reset attacker's state
		
				# play attack sound
				self.sound.play('pew')
		
				# if attack killed target
				target = self.enemies[self.selectedEnemyIDX]
				if target.isDead():
					print '--died: ' + target.name
				
					attacker.killCount += 1
				
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
					self.refresh.append( eraseRect )
		
					if len( self.enemies ) != 0: # if still enemies, reselect first one
						self.enemies[0].select()
					else: # if all enemies are gone
						self.awardXP()
						done = True
						print 'you win the battle!'
				
						self.battlesWon += 1
						self.leaveBattle( True, charles = self.gotCharles )
						print 'battles won:', self.battlesWon
				
						if self.inBossBattle: # won the boss battle! go to end screen
							self.enterDialogue() # trigger final congratulatory conversation
							return
				
						self.stage.addBattle()
						print 'for', self.stage.name, 'battle', self.stage.battlesCompleted, 'out of', self.stage.numBattles
						if self.stage.completed():
							print 'stage', self.stage.name, 'has been completed'
		
			# if it's an enemy's turn, have it attack
			if not playerTurn:
				loss = self.enemyTurn()
				if loss: # if the enemy turn resulted in a loss, hold battle screen while animations finish
					self.holdBattle = True
		
		# if holding battle, check to see if animations have finished
		else:
			finished = True
			for chara in self.allPlayers: # if any of the players is not done, we are not finished
				if not chara.finishedDeath():
					finished = False
		
			# if death animations have finished, leave battle
			if finished:
				self.battlesLost += 1
				self.leaveBattle( False, self.gotCharles )
				done = True
		
		# if we're still on the battle screen
		if not done:
			# update screen contents
			for edna in self.enemies:
				edna.draw( self.screen )
				self.refresh.append( edna.getRect() )
			
			# updating players requires two loops, otherwise erasures mess up characters already drawn
			for priya in self.allPlayers: # erase previous frame of animation
				if not self.inBossBattle:
					self.stage.fillBattleBG( self.screen, priya.battleRect )
				else:
					self.fillBossBattleBG( priya.battleRect )
			for priya in self.allPlayers: # draw new frame
				priya.draw( self.screen )
				self.refresh.append( priya.battleRect )
			
			self.refresh.append( self.player.getRect() )
			for p in self.battleParticipants:
				self.refresh.append( p.hpbarBG )
	
	# parses keyboard input for stat screen mode and updates screen contents
	def updateStatScreen( self ):
		# parse keyboard/mouse input events
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN: # for initial key presses
				if event.key == pygame.K_c:
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
				exitGame()
	
	#continues to next box in dialogue	
	def updateDialogue(self):
		#print "IN UPDATE DIALOGUE"
		if self.gameConvo.convoOver == True:
			
			#print "EXITING DIALOGUE"
			self.inDialogue = False
			
			if self.inIntro:
				self.fillIntroBG()
			elif self.inBossBattle:
				self.fillBossBattleBG()
			else:
				self.stage.moveCamView( self.screen, self.refresh, self.camera )
				self.player.draw( self.screen )
				self.refresh.append( self.player.getRect() )
			
			if self.convoNum == 2:
				self.drawBattleGuide()
				self.runBattleGuide()
			elif self.convoNum == 4 or self.convoNum == 7:
				self.enterBattle( charles = self.gotCharles, canFlee = False ) # CANNOT FLEE
				self.inStoryBattle = True
			elif self.convoNum == 5:
				self.enterBattle( canFlee = False) # CANNOT FLEE
				self.charlesBattle = True # triggering Charles battle
				self.inStoryBattle = True
			elif self.convoNum == 9:
				self.enterBattle( charles = True, canFlee = False ) # CANNOT FLEE
				self.key2Battle = True # triggering battle for key 2
				self.inStoryBattle = True
			elif self.convoNum == 11:
				self.convoNum += 1
				self.enterCyberSystem()
			elif self.convoNum == 12:
				print 'SHOULD GET HERE'
				self.enterBossBattle()
				self.inStoryBattle = True
			elif self.convoNum == 13:
				self.gameComplete = True # congratulatory convo ends the game
			
			self.convoNum += 1
		else:
			
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_v:
						#print "UPDATING DIALOGUE"
						if self.gameConvo.convoOver != True:
							#print "STILL MORE TEXT"
							#draw BG again first
							if self.inIntro:
								self.fillIntroBG()
							elif self.inBossBattle:
								self.fillBossBattleBG()
							else:
								self.stage.moveCamView( self.screen, self.refresh, self.camera )
								self.player.draw( self.screen )

							self.gameConvo.advanceText()
						
				if event.type == pygame.QUIT:
					exitGame()
	
	# draws the initial battle guide
	def drawBattleGuide( self ):
		guideOrig = pygame.image.load( 'images/BattleGuide.png' ).convert_alpha()
		guide = pygame.transform.scale( guideOrig, self.screenSize )
		
		self.screen.blit( guide, ( 0, 0 ) )
		pygame.display.update()
	
	# runs a loop for the initial battle guide, exits into battle when user presses v
	def runBattleGuide( self ):
		done = False
		while not done:
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_v:
						done = True
						self.enterBattle( charles = self.gotCharles, canFlee = False ) # CANNOT FLEE
						self.inStoryBattle = True
				if event.type == pygame.QUIT:
					exitGame()
	
	# fills the given rectangle (or the entire screen) with the current intro background
	def fillBossBattleBG( self, rect = None ):
		if rect == None:
			self.screen.blit( self.bossBattleBG, ( 0, 0 ) )
			self.refresh.append( self.screen.get_rect() )
		else:
			self.screen.blit( self.bossBattleBG, rect, rect )
			self.refresh.append( rect )
	
	# sends game into CyberSystem location, triggers dialogue that leads into final boss battle
	def enterCyberSystem( self ):
		self.screen.blit( self.bossBattleBG, ( 0, 0 ) )
		self.inBossBattle = True
		self.inStoryBattle = True
		print 'story event: into the CyberSystem!'
		
		pygame.display.update()
		
		print 'convo should be 12, is', self.convoNum
		
		self.enterDialogue() # convo 12 with NPE
		
		self.convoNum -= 1 # should fix issue with convoNum resulting from back-to-back dialogues
	
	# sends everyone into battle mode and creates final boss
	def enterBossBattle( self ):
		print 'ENTER BOSS BATTLE'
		
		# config messages
		self.messages.setBackground( self.bossBattleBG )
		
		# play battle music
		self.sound.stop('explora')
		self.sound.play("enemy", -1 )
		
		self.inBattle = True
		self.player.enterBattle( False ) # no one is allowed to flree
		self.fa.enterBattle( False )
		self.zen.enterBattle( False )
		self.cha.enterBattle( False )
		
		bossBug = agents.Enemy( ( 10, 10 ), self.bossBugIMG, 'final boss', 18 )
		print 'at level', bossBug.level, 'boss bug has', bossBug.totalHP, 'HP'
		bossBug.totalHP = 8000
		bossBug.hp = 8000
		#bossBug = agents.Enemy( ( 10, 10 ), self.bossBugIMG, 'final boss', 2 ) # just to make testing easier
		
		# build list of battle participants
		self.battleParticipants= [ self.mel, self.fa, self.zen, self.cha, bossBug ]
		self.currentBattleTurn = 0
		self.livePlayers = [ self.mel, self.fa, self.zen, self.cha ]
		self.enemies = [ bossBug ]
		
		
		# create dashboard
		self.dashboard = AttackChooser(self.screen)
		self.dashboard.config(self.battleParticipants[self.currentBattleTurn])
		
		#print 'enter battle'
		
		# reset stored points for new battle
		self.storedPoints = 0
		
		self.refresh.append( self.screen.get_rect() )

	# reports the wins, losses, escapes, and
	# each characters kill and death counts,
	# as well as if all moves were unlocked
	def reportRecords( self ):
		
		# play end music
		self.sound.stop( "explora" )
		self.sound.stop( "battleMusic" )
		self.sound.stop( "enemy" )
		self.sound.play("end")
		
		allMovesUnlocked = False
		players = [self.mel, self.fa, self.zen, self.cha]
		melInfo = ['Melody:']
		faInfo = ['Fatimah:']
		zenInfo = ['Zena:']
		chaInfo = ['Charles:']

		# get individual player records
		for player in players:
			rightList = None
			if player.name == 'Melody':
				rightList = melInfo
			elif player.name == 'Fatimah':
				rightList = faInfo
			elif player.name == 'Zena':
				rightList = zenInfo
			elif player.name == 'Charles':
				rightList = chaInfo
			rightList.append('Killed ' + str(player.killCount) + ' enemies')
			rightList.append('Died ' + str(player.timesKilled) + ' times')

			# assign back to original list
			if player.name == 'Melody':
				melInfo = rightList
			elif player.name == 'Fatimah':
				faInfo = rightList
			elif player.name == 'Zena':
				zenInfo = rightList
			elif player.name == 'Charles':
				chaInfo = rightList	

			if player.numMovesUnlocked == 5:
				allMovesUnlocked = True

		# get general game records
		victoryList = ['Game Records: ']
		victoryList.append(  'Battles Won: ' + str( self.battlesWon ) )
		victoryList.append( 'Battles Lost: ' + str( self.battlesLost ) )
		victoryList.append( 'Times Fled: ' + str( self.timesFled ) )
		if allMovesUnlocked == True:
			victorylist.append('All moves were unlocked! Nice!')

		returnList = [victoryList, melInfo, faInfo, zenInfo, chaInfo]

		return returnList







