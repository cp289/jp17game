# Melody Mao
# CS269, January 2017
# Debug Davis

# main.py
# This file defines the top-level code for the game.

import pygame
import stages

'''
SCREEN PLANNING
button class? with position, image, draw, selected
if selected, draw > cursor to left
run in loop: check for arrow keys left/right and enter
'''

# some useful variables for the rest of this file
back, front, left, right, none = range( 5 )
green = ( 150, 180, 160 )
white = ( 255, 255, 255 )

# draws game start screen
def showStartScreen( screen ):
	startScreen = pygame.Surface( ( 800, 600 ) )
	startScreen.fill( ( 100, 120, 100 ) )
	bigFont = pygame.font.SysFont( 'Helvetica', 44, bold=True )
	startText = bigFont.render( 'press s to start', True, white )

	screen.blit( startScreen, ( 0, 0 ) )
	screen.blit( startText, ( screen.get_width() / 3, screen.get_height() / 2 ) )
	pygame.display.update()

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
		sys.exit()
	
	showStartScreen( screen )
	
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
	
	game = stages.Game( screen )
	game.loadHallwayStage() # possibly do this in Game constructor later
	game.loadRoboLabStage()
	
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




