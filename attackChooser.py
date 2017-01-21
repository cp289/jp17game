# File: attackChooser.py
# Author: Charles Parham
# 
# Notes:
# 	background needed? (currently gray)
#
# Issues:
# 	Status screen destroys this
# 	need to handle leveling up
#	need to make the dashboard more visually apealing
# 	rename this file to 'dashboard'

import pygame, sys, agents

class AttackChooser:
	def __init__(self, parSurface):
		
		# initialize position and size
		self.pos = (0,500)
		self.dim = ( 800, 100 )
		
		# define rectangle
		self.rect = pygame.Rect(self.pos, self.dim)
		
		# initialize surface
		self.surface=pygame.Surface(self.dim)
		self.surface.fill((128,128,128))
		
		# initialize parent surface
		self.parSurface = parSurface
		
		# initialize font
		self.font = pygame.font.SysFont("Comic Sans", 40)
		self.atkText = self.font.render(" ", True, (255,255,255))
		
		# initialize display information
		self.chara = None
		self.attacks = []
		self.atkIndex = 0
		
	def attack(self):
		return self.attacks[self.atkIndex]
		
	def config(self, chara):
		# setup text elements
		self.chara = chara
		self.attacks = chara.attacks
		self.atkindex = 0
	
	def draw(self): # too much rendering ( in most cases, only text needs updating )
		self.parSurface.blit(self.surface, self.pos )
		
		name = self.font.render(self.chara.name, True, (255,255,255))
		self.parSurface.blit(self.surface, self.atkText.get_rect(), self.atkText.get_rect())
		self.atkText = self.font.render(self.attacks[self.atkIndex].name, True, (255,255,255))
		
		self.parSurface.blit(name, (0,500))
		self.parSurface.blit(self.atkText, (200,500))
		
		pygame.display.update(self.rect)
		
		
	def switchAtk(self, num):
		self.atkIndex = (self.atkIndex + num) % len(self.attacks)


def main():
	# making a screen setup for testing
	pygame.init()
	screen = pygame.display.set_mode( (900,600) )
	
	# initializing fonts
	pygame.font.init()
	
	# initializing a melody for testing
	playerL = pygame.image.load( 'images/melStandLeft.png' ).convert_alpha()
	playerR = pygame.image.load( 'images/melStandRight.png' ).convert_alpha()
	playerF = pygame.image.load( 'images/melStandFront.png' ).convert_alpha()
	playerB = pygame.image.load( 'images/melStandBack.png' ).convert_alpha()
	playerS = pygame.image.load( 'images/MelodyStatPic.png' ).convert_alpha()
	playerBattle = pygame.image.load( 'images/MelodyBattleSprite.png' ).convert_alpha()
	
	initpos = ( 300, 400 ) # hopefully the middle of the bottom
	battlePos = ( 700, 50 )
	imglist = [ playerF, playerB, playerL, playerR, playerS, playerBattle ]
	mel = agents.PlayableCharacter( initpos, battlePos, imglist, 'Melody' )
	mel.setAllStats( ( 500, 54, 44, 43, 50, 7 ) )
	# total HP, ATK, DFN, SPD, ACC, time
	mel.setAllGR( ( 0.8, 0.9, 0.85, 0.75, 0.7 ) )
	# HP, ATK, DFN, SPD, ACC
	
	# drawing an AttackChooser
	test = AttackChooser(screen)
	test.config(mel)
	test.draw()
	
	while 1:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				sys.exit()

if __name__ == "__main__":
	main()