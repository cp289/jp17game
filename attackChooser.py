# File: attackChooser.py
# Author: Charles Parham
# 

import pygame, sys, agents, random

class AttackChooser:
	def __init__(self, parSurface):
		
		# initialize position and size
		self.pos = (0,500)
		self.dim = ( 800, 100 )
		
		self.atkPos = (self.pos[0] + 205, self.pos[1] + 10)
		self.descPos = (self.pos[0] + 330, self.pos[1] + 55)
		self.namePos = (self.pos[0] + 19, self.pos[1] + 7)
		self.charTimePos = (self.pos[0] + 19, self.pos[1] + 60)
		self.atkTimePos = (self.pos[0] + 210, self.pos[1] + 55)
		
		# define rectangle
		self.rect = pygame.Rect(self.pos, self.dim)
		
		# initialize surface
		self.surface=pygame.Surface(self.dim)
		self.surface.fill((128,128,128))
		
		# initialize parent surface
		self.parSurface = parSurface
		
		# initialize fonts
		self.font = pygame.font.SysFont("helvetica", 33)
		self.descFont = pygame.font.SysFont("helvetica", 18)
		self.nameFont = pygame.font.SysFont("helvetica", 40)
		self.charTimeFont = pygame.font.SysFont("helvetica", 15)
		
		# initialize text
		self.atkText = self.font.render(" ", True, (255,255,255))
		self.descText = self.descFont.render(" ", True, (255,255,255))
		self.nameText = self.nameFont.render(" ", True, (0, 255, 0))
		self.charTimeText = self.charTimeFont.render(" ", True, (255,255,255))
		self.atkTimeText = self.descFont.render(" ", True, (255,255,255))
		
		# initialize display information
		self.chara = None
		self.attacks = []
		self.atkIndex = 0
	
	# returns the attack at the current index
	def attack(self):
		return self.attacks[self.atkIndex]
		
	# configures the attack chooser for a given character
	def config(self, chara):
		# setup text elements
		self.chara = chara

		self.attacks = chara.availableAttacks #random 4 attacks + 2 mandatory ones

		self.atkIndex = 0
		
		self.atkText = self.font.render(self.attack().name, True, (0,0,205))

		self.descText = self.descFont.render(self.attack().desc, True, (255,255,255))
		
		self.nameText = self.nameFont.render(self.chara.name, True, (0, 255, 0))
		
		self.charTimeText = self.charTimeFont.render("Time: "+str(chara.time)+"/"+str(self.chara.maxTime), True, (255,255,255))
		
		self.atkTimeText = self.descFont.render("(Time Cost: "+str(self.attack().timeNeeded)+")", True, (255,255,255))
		
		print('config time: ')

		self.atkRect = pygame.Rect(
				self.atkPos,
				(self.atkText.get_rect().w,self.atkText.get_rect().h)
			)

		self.descRect = pygame.Rect(
				self.descPos,
				(self.descText.get_rect().w, self.descText.get_rect().h)
			)
			
		self.charTimeRect = pygame.Rect(
				self.charTimePos,
				(self.charTimeText.get_rect().w, self.charTimeText.get_rect().h)
			)
		
		self.atkTimeRect = pygame.Rect(
				self.atkTimePos,
				(self.atkTimeText.get_rect().w, self.atkTimeText.get_rect().h)
			)
		self.draw()
	
	def updateTime(self): # No erasing yet...
		# erase old time
		self.parSurface.blit(self.surface, self.pos, self.charTimeRect)
		oldCharTimeRect = self.charTimeRect
		
		# update time value
		self.charTimeText = self.charTimeFont.render(str(self.chara.time)+"/"+str(self.chara.maxTime), True, (255,255,255))
		
		self.charTimeRect = pygame.Rect(
				self.charTimePos,
				(self.charTimeText.get_rect().w, self.charTimeText.get_rect().h)
			)
		
		# update display
		pygame.display.update(self.charTimeRect if self.charTimeRect.w > oldCharTimeRect.w else oldCharTimeRect)
	
	# draws the attack chooser
	def draw(self): 
		# draw self.surface
		self.parSurface.blit(self.surface, self.pos )
		
		# draw attack text
		self.parSurface.blit(self.atkText, self.atkRect)

		# draw atk description text
		self.parSurface.blit(self.descText, self.descRect)
		
		# draw name
		self.parSurface.blit(self.nameText, self.namePos)
		
		# draw charTime
		self.parSurface.blit(self.charTimeText, self.charTimePos)
		
		# draw atkTime
		self.parSurface.blit(self.atkTimeText, self.atkTimePos)
		
		pygame.display.update(self.rect)
		
	# switches the selected attack
	def switchAtk(self, num):
		if self.attack().name == "Share Code":
			self.attack().oldCursor()
		
		# update attack index
		self.atkIndex = (self.atkIndex + num) % len(self.attacks)
		
		# erase old attack and description text
		self.parSurface.blit(self.surface, self.atkRect, self.atkRect)
		self.parSurface.blit(self.surface, self.atkTimeRect, self.atkTimeRect)
		self.parSurface.blit(self.surface, self.descRect, self.descRect)
		oldAtkRect = self.atkRect
		oldAtkTimeRect = self.atkTimeRect
		oldDescRect = self.descRect
		
		# redraw attack and description text
		self.atkText = self.font.render(self.attack().name, True, (0, 0, 205))
		self.descText = self.descFont.render(self.attack().desc, True, (255,255,255))
		self.atkTimeText = self.descFont.render('(Time Cost: '+str(self.attack().timeNeeded)+')', True, (255,255,255))

		self.atkRect = pygame.Rect(
				self.atkPos,
				(self.atkText.get_rect().w,
				self.atkText.get_rect().h)
			)
		self.descRect = pygame.Rect(
				self.descPos,
				(self.descText.get_rect().w,
				self.descText.get_rect().h)
			)
		self.atkTimeRect = pygame.Rect(
				self.atkTimePos,
				(self.atkTimeText.get_rect().w, self.atkTimeText.get_rect().h)
			)

		# actually blit the new text
		self.parSurface.blit(self.atkText, self.atkRect)
		self.parSurface.blit(self.atkTimeText, self.atkTimeRect)
		self.parSurface.blit(self.descText, self.descRect)
		
		# update display
		pygame.display.update(oldAtkRect if oldAtkRect.w > self.atkRect.w else self.atkRect)
		pygame.display.update(oldAtkTimeRect if oldAtkTimeRect > self.atkRect.w else self.atkRect)
		pygame.display.update(oldDescRect if oldDescRect.w > self.descRect.w else self.descRect)
		
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
	mel = agents.PlayableCharacter( initpos, battlePos, imglist, 'Melody', None, namePos )
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