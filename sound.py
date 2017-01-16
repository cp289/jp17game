import sys, pygame, time

pygame.init()

pygame.mixer.init()


screen=pygame.display.set_mode((400,400))

print "Loading battle music"

sound=pygame.mixer.Sound("sounds/battleMusic.ogg")

print "Playing battle music"

sound.play(loops=1000)

while 1:
	for event in pygame.event.get():
		pass