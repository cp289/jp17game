# Unless you want to live a life full of pain,
#   make sure all audio files are of the form *.ogg and have a 
#   sample rate of 22050 Hz. Good luck.


import sys, pygame, time

pygame.init()

pygame.mixer.init()


screen=pygame.display.set_mode((400,400))

#Loading battle music

sound=pygame.mixer.Sound("sounds/battleMusic.ogg")

#Playing battle music

sound.play(loops=1000)

while 1:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			sys.exit()