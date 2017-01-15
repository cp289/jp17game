import shelve
import pygame
import sys

pygame.init()

display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('shelve_test')

class Character():
	def __init__(self, name, ATK):
		self.name = name
		self.ATK = ATK
	def getName(self):
		#returns name string
		return self.name
	def getATK(self):
		return self.ATK


zena = Character("Zena", 200)
zenaInfo = {"Name": zena.getName(), "ATK": zena.getATK()}

savedInfo = None

def gameLoop():
	gameExit = False
	print "CONTROLS:"
	print "C to set variable to save (DO THIS FIRST)"
	print "S to save"
	print "L to load"
	print "p to print info"
	while not gameExit:
		#starting loop
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				gameExit = True
			if event.type == pygame.KEYDOWN:
				#pressing c triggers the textbox
				if event.key == pygame.K_c:
					savedInfo = "SomethingSaved"
					print savedInfo
				elif event.key == pygame.K_s:
					shelfFile = shelve.open("savedGameFile") #creates a file to store variables in
					shelfFile["playerInfo"] = zenaInfo
					shelfFile["savedInfo"] = "savedInfo"
					shelfFile.close()
					print "SAVED INFO!"
				elif event.key == pygame.K_l:
					shelfFile = shelve.open("savedGameFile") #creates a file to store variables in
					shelfFile["playerInfo"] = zenaInfo
					try:
						shelfFile["savedInfo"] = savedInfo
					except:
						print "VARIABLE WASN'T CHANGED--PRESS C!"
					shelfFile.close()
					print "LOADED INFO!"
				elif event.key == pygame.K_p:
					print "Zena: " + zena.getName()
					try: 
						print "something saved: " + savedInfo
					except:
						print "No changed info-- PRESS C FIRST!"

	pygame.quit()
	quit()
gameLoop()