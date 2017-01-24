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

# draws game start screen
def showStartScreen( screen, buttons ):
	startScreen = pygame.image.load( 'images/Debug Davis Start Screen.png' ).convert_alpha()
	#bigFont = pygame.font.SysFont( 'Helvetica', 44, bold=True )
	#startText = bigFont.render( 'press s to start', True, white )

	screen.blit( startScreen, ( 0, 0 ) )
	pygame.draw.rect( screen, black, pygame.Rect( ( 100, 250 ), ( 600, 300 ) ) )
	#screen.blit( startText, ( screen.get_width() / 3, screen.get_height() / 2 ) )
	
	for button in buttons:
		button.draw( screen )
	
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
	print 'init screen'
	
	# make start screen buttons
	
	startImg = pygame.image.load( 'images/startUnselected.png' ).convert_alpha()
	startImgSel = pygame.image.load( 'images/startSelected.png' ).convert_alpha()
	startButton = Button( ( 200, 300 ), startImg, startImgSel, 'start' )
	startButton.select()
	
	instrImg = pygame.image.load( 'images/instrUnselected.png' ).convert_alpha()
	instrImgSel = pygame.image.load( 'images/instrSelected.png' ).convert_alpha()
	instrButton = Button( ( 200, 375 ), instrImg, instrImgSel, 'instructions' )
	
	selectedButton = 0
	buttons = [ startButton, instrButton ]
	showStartScreen( screen, buttons )
	
	# initialize sounds
	sound = Sound()
	
	# play start screen music
	sound.play("start")
	
	print 'start screen'
	
	# run a loop for start screen
	moveOn = False
	while not moveOn:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
					buttons[selectedButton].deselect()
					selectedButton = ( selectedButton + 1 ) % 2
					buttons[selectedButton].select()
				elif event.key == pygame.K_RETURN:
					if buttons[selectedButton].name == 'start':
						moveOn = True
						break
			if event.type == pygame.QUIT:
				exitGame()
		
		startButton.draw( screen )
		instrButton.draw( screen )
		pygame.display.update()
	
	game = stages.Game( screen, sound )
	game.loadHallwayStage() # possibly do this in Game constructor later
	game.loadRoboLabStage()
	game.loadMacLabStage()
	
	sound.stop("start")
	game.start()
	
	# loop for intro (hallway scene with unspecified students, conversation in my room)
	introDone = False
	while not introDone:
		if game.updateIntro():
			introDone = True
	
	game.enterHallwayStageRight()
	
	'''
	just load all stages to begin with (probably put a loading screen on while that's going)
	
	enter hallway stage
	
	run a loop with just update
	within update, if you enter another room, just call the enter for that stage
	just keep going...
	
	in beginning: macLabUnlocked = False
	if you walk into the door, trigger dialogue with Kimberly
	if you walk into the robotics lab, call enterRoboLabStage
	
	'''
	
	# run a loop for the robotics lab
	while 1:
		game.update()
	'''put the above loop inside another loop for while the stage is not finished'''
	
	# exit option for end screen?
	
	# after game end, keep screen until user closes window
	while 2:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exitGame()

if __name__ == '__main__':
	main()
