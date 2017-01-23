# File: attackChooser.py
# Author: Charles Parham
# 
# Notes:
# 	background needed? (currently gray)
#
# Issues:
#	need to make the dashboard more visually apealing
# 	rename this file to 'dashboard'
#
# Bugs:
# 	Index out of bounds error occasionally when toggling target enemies
#	Cursor remains on characters after switching attack type from "share code"
#	  potentially related: characters die twice causing a list remove error.


import pygame, sys, agents, random

class AttackChooser:
	def __init__(self, parSurface):
		
		# initialize position and size
		self.pos = (0,500)
		self.dim = ( 800, 100 )
		
		self.atkPos = (self.pos[0] + 200, self.pos[1] + 0)
		
		# define rectangle
		self.rect = pygame.Rect(self.pos, self.dim)
		
		# initialize surface
		self.surface=pygame.Surface(self.dim)
		self.surface.fill((128,128,128))
		
		# initialize parent surface
		self.parSurface = parSurface
		
		# initialize font
		self.font = pygame.font.SysFont("helvetica", 40)
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

		self.attacks = chara.attacks #random 4 from them if you want

		self.atkIndex = 0
		
		self.atkText = self.font.render(self.attack().name, True, (255,255,255))
		self.atkRect = pygame.Rect(
				self.atkPos,
				(self.atkText.get_rect().w,
				self.atkText.get_rect().h)
			)
	
	def draw(self): # too much rendering ( in most cases, only text needs updating )
		# draw self.surface
		self.parSurface.blit(self.surface, self.pos )
		
		# draw attack text
		self.parSurface.blit(self.atkText, self.atkRect)
		
		# draw name
		name = self.font.render(self.chara.name, True, (255,255,255))
		self.parSurface.blit(name, (0,500))
		
		pygame.display.update(self.rect)
		
	def switchAtk(self, num):
		if self.attack().name == "Share Code":
			self.attack().oldCursor()
		
		# update attack index
		self.atkIndex = (self.atkIndex + num) % len(self.attacks)
		
		# erase old attack text
		self.parSurface.blit(self.surface, self.atkRect)
		oldRect = self.atkRect
		
		# redraw attack text
		self.atkText = self.font.render(self.attack().name, True, (255,255,255))
		self.atkRect = pygame.Rect(
				self.atkPos,
				(self.atkText.get_rect().w,
				self.atkText.get_rect().h)
			)
		self.parSurface.blit(self.atkText, self.atkRect)
		
		# update display
		pygame.display.update(oldRect if oldRect.w > self.atkRect.w else self.atkRect)
		
		if self.attack().name == "Share Code":
			self.attack().newCursor()


def main():
	# making a screen setup for testing
	pygame.init()
	screen = pygame.display.set_mode( (900,600) )
	
	# initializing fonts
	pygame.font.init()
	
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
	mel = agents.PlayableCharacter( initpos, battlePos, imglist, 'Melody', namePos )
	mel.setAllStats( ( 500, 54, 44, 43, 50, 7 ) )
	# total HP, ATK, DFN, SPD, ACC, time
	mel.setAllGR( ( 0.8, 0.9, 0.85, 0.75, 0.7 ) )
	# HP, ATK, DFN, SPD, ACC
	
	standlist = None
	walklist = None
	battlelist = ( pygame.image.load( 'images/Fatimah/FatimahBattleSprite.png' ).convert_alpha() ) # TEMPORARY
	attacklist = None
	dielist = None
	playerS = pygame.image.load( 'images/Fatimah/FatimahStatPic.png' ).convert_alpha()
	playerC = pygame.image.load( "images/Fatimah/FatimahHead.png" ).convert_alpha()
	otherlist = ( playerS, playerC )
	
	# drawing an AttackChooser
	test = AttackChooser(screen)
	test.config(mel)
	test.draw()
	
	while 1:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				sys.exit()
			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_LEFT:
					test.switchAtk(-1)
				if e.key == pygame.K_RIGHT:
					test.switchAtk(1)

if __name__ == "__main__":
	main()