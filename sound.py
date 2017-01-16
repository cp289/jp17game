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