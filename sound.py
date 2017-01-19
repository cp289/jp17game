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
			"enemyMusic.ogg"
		])
	
	# Loads list of music files in the sounds/ directory
	def load(self, files):
		for file in files:
			self.files.update({".".join(file.split(".")[0:-1]):pygame.mixer.Sound("sounds/"+file)})
	
	# Plays music file where `name' is the filename without the file extension
	def play(self, name, loops=1):
		self.files[name].play(loops)
		
	# Pauses the specified sound
	def pause(self, name):
		pass

# Main method
def main():
	pygame.init()
	sound=Sound()
	sound.play("enemyMusic")
	while 1:
		for event in pygame.event.get():
			if event.type==pygame.QUIT:
				sys.exit()

if __name__ == '__main__':
	main()