 # Melody Mao
# CS269, January 2017
# Debug Davis

# main.py
# This file defines the top-level code for the game.

import pygame
import stages
import sys
import os
from sound import *

# some useful variables for the rest of this file
back, front, left, right, none = range( 5 )
green = ( 150, 180, 160 )
white = ( 255, 255, 255 )
black = ( 0, 0, 0 )

# represents a button on the start/end screens
class Button:
	
	# creates a new button at the given position with the given images and name
	def __init__( self, pos, img, imgSel, name ):
		self.pos = pos
		self.image = img
		self.imageSelected = imgSel
		self.name = name
		self.selected = False
	
	# sets this button to be selected
	def select( self ):
		self.selected = True
	
	# sets this button to be unselected
	def deselect( self ):
		self.selected = False
	
	# draws the button on the given screen Surface
	def draw( self, screen ):
		if self.selected:
			screen.blit( self.imageSelected, self.pos )
		else:
			screen.blit( self.image, self.pos )

# loads everything needed to run the game
def gameLoad(screen,sound):
	showLoadingScreen()
	game = stages.Game( screen, sound )
	game.loadHallwayStage() # possibly do this in Game constructor later
	game.loadRoboLabStage()
	game.loadMacLabStage()
	
	return game

# draws loading screen
def showLoadingScreen():
	pass

# draws game start screen
def showStartScreen( screen, buttons ):
	startScreen = pygame.image.load( 'images/start/Debug Davis Start Screen.png' ).convert_alpha()
	#bigFont = pygame.font.SysFont( 'Helvetica', 44, bold=True )
	#startText = bigFont.render( 'press s to start', True, white )

	screen.blit( startScreen, ( 0, 0 ) )
	pygame.draw.rect( screen, black, pygame.Rect( ( 100, 250 ), ( 600, 300 ) ) )
	#screen.blit( startText, ( screen.get_width() / 3, screen.get_height() / 2 ) )
	
	for button in buttons:
		button.draw( screen )
	
	pygame.display.update()

# draws instruction screen
def showInstructionScreen( screen ):
	instructionScreenOrig = pygame.image.load( 'images/start/StartInstructions.png' ).convert_alpha()
	instructionScreen = pygame.transform.scale( instructionScreenOrig, screen.get_size() )
	
	screen.blit( instructionScreen, ( 0, 0 ) )
	pygame.display.update()

# draws game end screen
def showEndScreen( screen, game ):
	screen.fill( green )

	font = game.bigFont
 
	# organize info
	records = game.reportRecords() 
	genInfo = records[0] #5 things
	melInfo = records[1] #3 things
	faInfo = records[2]
	zenInfo = records[3]
	chaInfo = records[4]

	screenWidth = game.screenSize[0]
	screenHeight = game.screenSize[1]
	midTop = ((screenWidth/2)-150, 0)
	midLeft = ( 30, screenHeight - 350)
	midRight = (screenWidth-400, screenHeight - 350)
	lineSkip = 50

	# blit info
	offset = 30 # space between characters' records
	lineNum = 0
	for info in genInfo:
		infoSurf = font.render(info, True, (0,0,0))
		screen.blit(infoSurf, (midTop[0], midTop[1]+ (lineSkip*lineNum)))
		lineNum += 1
	lineNum = 0
	for record in melInfo:
		recordSurf = font.render(record, True, (0,0,0))
		screen.blit( recordSurf, (midLeft[0], midLeft[1] + (lineSkip * lineNum)) )
		lineNum += 1
	for record in faInfo:
		recordSurf = font.render(record, True, (0,0,0))
		screen.blit( recordSurf, (midLeft[0], midLeft[1] + (lineSkip * lineNum)+offset) )
		lineNum += 1	
	lineNum = 0	
	for record in zenInfo:
		recordSurf = font.render(record, True, (0,0,0))
		screen.blit( recordSurf, (midRight[0], midRight[1] + (lineSkip * lineNum)) )
		lineNum += 1
	for record in chaInfo:
		recordSurf = font.render(record, True, (0,0,0))
		screen.blit( recordSurf, (midRight[0], midRight[1] + (lineSkip * lineNum)+offset) )
		lineNum += 1

	pygame.display.update()

def exitGame():
	print('cleaning up...')
	d = os.path.dirname(os.path.realpath(__file__))
	files = [ file for file in os.listdir(d) if file.endswith(".pyc") ]
	for file in files:
		os.remove(file)
	sys.exit()

# runs main game code
def main():
	# initialize pygame
	pygame.init()
	screenSize = ( 800, 600 )
	screen = pygame.display.set_mode( screenSize )

	# initialize the fonts
	try:
		pygame.font.init()
	except:
		print "Fonts unavailable"
		exitGame()
	
	pygame.display.set_caption( 'debugDavis()' )
	print 'Loading...'
	
	# show loading screen
	showLoadingScreen()
	
	# initialize sounds
	sound = Sound()
	
	# load game
	game = gameLoad(screen,sound)
	
	# make start screen buttons
	startImg = pygame.image.load( 'images/start/startUnselected.png' ).convert_alpha()
	startImgSel = pygame.image.load( 'images/start/startSelected.png' ).convert_alpha()
	startButton = Button( ( 200, 300 ), startImg, startImgSel, 'start' )
	startButton.select()
	
	instrImg = pygame.image.load( 'images/start/instrUnselected.png' ).convert_alpha()
	instrImgSel = pygame.image.load( 'images/start/instrSelected.png' ).convert_alpha()
	instrButton = Button( ( 200, 375 ), instrImg, instrImgSel, 'instructions' )
	
	selectedButton = 0
	buttons = [ startButton, instrButton ]
	showStartScreen( screen, buttons )
	
	# play start screen music
	sound.play("start",-1)
	print 'start screen'
	
	# run a loop for start screen
	moveOn = False
	onInstr = False
	while not moveOn:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
					buttons[selectedButton].deselect()
					selectedButton = ( selectedButton + 1 ) % 2
					buttons[selectedButton].select()
				elif event.key == pygame.K_RETURN:
					if onInstr:
						showStartScreen( screen, buttons )
						onInstr = False
					else:
						if buttons[selectedButton].name == 'start':
							moveOn = True
							break
						elif buttons[selectedButton].name == 'instructions':
							showInstructionScreen( screen )
							onInstr = True
			if event.type == pygame.QUIT:
				exitGame()
		
		if not onInstr:
			startButton.draw( screen )
			instrButton.draw( screen )
			pygame.display.update()
	
	# stop start screen music
	sound.stop("start")
	game.start()
	
	# loop for intro (hallway scene with unspecified students, conversation in my room)
	introDone = False
	while not introDone:
		if game.updateIntro():
			introDone = True
	
	game.enterHallwayStageRight()
	
	# loop for the rest of the game
	while not game.gameComplete:
		game.update()
	
	showEndScreen( screen, game )
	
	# after game end, keep screen until user closes window
	while 2:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exitGame()

if __name__ == '__main__':
	main()
