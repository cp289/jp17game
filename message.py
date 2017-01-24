
import pygame, sys
from main import gameExit

class Message:
	def __init__(self, title, body):
		pass
		
	def draw(self):
		pass
		
class Mailbox:
	def __init__(self):
		self.hasMail = false
		self.message = None
		
	def sendMail(self, message):
		self.message = message
		self.hasMail = true
		
	def display(self):
		self.hasMail = false
		

def main():
	pygame.init()
	
	pygame.display.set_mode((800,600))
	
	
	while True:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				gameExit()
	
if __name__ == '__main__':
	main()