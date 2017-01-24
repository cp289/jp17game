# File: message.py
# Author: Charles Parham
#

import pygame, sys, time

class Message:
	def __init__(self, body, sec):
		self.time = time.time() + sec
		self.body = body
		self.font = pygame.font.SysFont('Helvetica', 30)
		self.text = self.font.render(body, True, (0,0,0))
		self.surface = pygame.Surface((self.text.get_rect().w+50,self.text.get_rect().h+50))
		self.surface.fill((200,200,200))
		self.pos = (400 - self.text.get_rect().w/2, 0)
		self.rect = self.surface.get_rect().move(self.pos)
	
	# draw the message
	def draw(self, surface):
		self.surface.blit(self.text, (25,25))
		surface.blit(self.surface, self.pos)
		pygame.display.update(self.rect)
		
	# must take in the background surface as a parameter
	def erase(self, surface, background ):
		surface.blit(background, self.rect, self.rect)
		pygame.display.update(self.rect)

class MessageDisplay:
	def __init__(self, surface):
		self.hasMessage = False
		self.message = None
		self.surface = surface
		self.background = None
		self.drawn = False
		
	# registers a message to display for a given amount of time
	def send(self, text, time):
		self.message = Message(text, time)
		self.hasMessage = True
	
	# sets the background surface of 
	def setBackground(self, background):
		self.background = background
	
	# updates the background
	def update(self):
		if self.hasMessage:
			if not self.drawn:
				self.message.draw(self.surface)
				self.drawn = True
			if time.time() > self.message.time:
				self.hasMessage = False
				self.drawn = False
				self.message.erase(self.surface, self.background)
			
		

def main():
	pygame.init()
	pygame.font.init()
	
	screen = pygame.display.set_mode((800,600))
	
	disp = MessageDisplay(screen)
	disp.setBackground(screen)
	disp.send(Message('test',2))
	disp.send(Message('test2',3))
	while True:
		disp.update()
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				sys.exit()
	
if __name__ == '__main__':
	main()