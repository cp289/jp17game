# Unless you want to live a life full of pain,
#   make sure all audio files are of the form *.ogg and have a 
#   sample rate of 22050 Hz. Good luck.


import sys, pygame, time

class Sound:
	def __init__(self):
		# Initialize pygame sound module
		pygame.mixer.init()
		
		# Load music files
		
		self.files={}
		
		self.battle=self.load([
			"battleMusic.ogg"
		])
		
	def load(self, files):
		for file in files:
			self.files.update({".".join(file.split(".")[0:-1]):pygame.mixer.Sound("sounds/"+file)})
		
	def play(self, name, loops=1):
		self.files[name].play(loops)
		
	def pause(self, name):
		pass


if __name__ == '__main__':
	pygame.init()
	sound=Sound()
	sound.play("battleMusic")
	while 1:
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				sys.exit()