import sys, pygame

pygame.init()

pygame.mixer.init()

print "Loading battle music"

battleMusic=pygame.mixer.Sound("sounds/battleMusic.wav")

print "Playing battle music"

battleMusic.play()

while 1:
	pass