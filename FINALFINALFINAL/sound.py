# File: sound.py
# Author: Charles Parham
#
# Unless you want to live a life full of pain,
#   make sure all audio files are of the form *.ogg and have a 
#   sample rate of 22050 Hz. Good luck.


import sys, pygame, time

class Sound:
	def __init__(self):
		# Initialize pygame sound module
		pygame.mixer.init()
		
		# Load music files
		
		# Dictionary of extensionless filenames and pygame Sound objects
		self.files={}
		
		# Load a list of sound files in the sounds/ directory
		self.battle=self.load([
			"battleMusic.ogg",
			"enemy.ogg",
			"explora.wav",
			"bonk.ogg",
			"zong.ogg",
			"pew.ogg",
			"start.ogg",
			"win.ogg",
			"end.ogg"
		])
	
	# Loads list of music files in the sounds/ directory
	def load(self, files):
		for file in files:
			self.files.update({".".join(file.split(".")[0:-1]):pygame.mixer.Sound("sounds/"+file)})
	
	# Plays music file where `name' is the filename without the file extension
	def play(self, name, loops=0):
		self.files[name].play(loops)
		
	# Pauses specified music
	def pause(self, name):
		pygame.mixer.pause()
		
	# Stops the specified sound
	def stop(self, name):
		self.files[name].fadeout(500)
	
	# returns whether the mixer is playing sound
	def busy(self):
		return pygame.mixer.get_busy()

# Main method
def main():
	pygame.init()
	screen = pygame.display.set_mode((800,600))
	sound=Sound()
	sound.play("enemyMusic")
	while 1:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_p:
					sound.pause("enemyMusic")
				if event.key == pygame.K_o:
					sound.play("enemyMusic")
				if event.key == pygame.K_s:
					sound.stop("enemyMusic")
			if event.type==pygame.QUIT:
				sys.exit()

if __name__ == '__main__':
	main()
