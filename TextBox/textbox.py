#Zena Abulhab
#CS269 J17
#Textbox class/structure outline
#Dialogue box testing
#Draws text box and dynamically places text inside
#by using the width of the text

import pygame
import time
import re #used to split text
import sys
pygame.mixer.init()
pygame.init()

#Define some colors
white = (255,255,255)
black = (0,0,0)
red = (255,0,0)
blue = (15,26,129)

display_width = 800
display_height = 600

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('textbox_test')

FPS = 30
clock=pygame.time.Clock()

boxLeftOffset = 50 #Distance from left edge of screen to where box will be
boxRightOffset = 30

textbox = pygame.image.load("GameTextbox.png").convert_alpha()
textbox = pygame.transform.scale(textbox, (display_width -boxRightOffset, display_height/3))

cursor = pygame.image.load("cursor.png").convert_alpha()
cursor = pygame.transform.scale(cursor, (15,25))

boxWidth = textbox.get_width()
boxHeight = textbox.get_height()
boxX = 12
boxY = (display_height - 10) - boxHeight
#offsets of text from sides, used to calculate corners
xOffset = 50 
yOffset = 70

textTopLeft = (boxX + xOffset, boxY + yOffset)
textTopRight = (boxX + boxWidth - xOffset, boxY + yOffset)
#textBottomLeft = (boxX + xOffset, boxY + boxHeight - yOffset)
textBottomRight = (boxX + boxWidth - xOffset, boxY + boxHeight - yOffset)

font = pygame.font.SysFont(None,35)
nameFont = pygame.font.SysFont(None,45)
dialogueColor = black

#inefficient for now because loop wouldn't work
zenaPic = pygame.image.load("ZenaHead.png").convert_alpha()
zenaPic = pygame.transform.scale(zenaPic, (300,300))
melodyPic = pygame.image.load("MelodyHead.png").convert_alpha()
melodyPic = pygame.transform.scale(melodyPic, (300,300))
fatimahPic = pygame.image.load("FatimahHead.png").convert_alpha()
fatimahPic = pygame.transform.scale(fatimahPic, (300,300))
charlesPic = pygame.image.load("CharlesHead.png").convert_alpha()
charlesPic = pygame.transform.scale(charlesPic, (300,300))

beep = pygame.mixer.Sound("beep.wav")

class Character():
	def __init__(self, name, portrait, nameX, nameY):
		self.name = name
		self.nameX = nameX
		self.nameY = nameY
		self.portrait = portrait
	def getPortrait(self):
		#returns portrait image
		return self.portrait
	def getName(self):
		#returns name string
		return self.name
	def getNameX(self):
		return self.nameX
	def getNameY(self):
		return self.nameY
	def getNameSurface(self):
		#returns surface object for name
		return nameFont.render(self.name, True, red)

zena = Character("Zena", zenaPic, textTopLeft[0]+6,textTopLeft[1]-63)
melody = Character("Melody", melodyPic, textTopLeft[0]-9,textTopLeft[1]-64)
fatimah = Character("Fatimah", fatimahPic, textTopLeft[0]-18,textTopLeft[1]-63)
charles = Character("Charles", charlesPic, textTopLeft[0]-17, textTopLeft[1]-63)

portraitCoord = (boxX+15, boxY+50) #the offsets are to make the placement more perfect

def gameLoop():
	gameExit = False
	gameDisplay.fill(white)
	startFont = font.render("Press C to begin conversation", True, blue)
	gameDisplay.blit(startFont,((display_width/2)-(startFont.get_width()/2),(display_height/2)-startFont.get_height()))
	finished = False #if true, all text has been read and the window will close

	#takes in character instance and string
	def textToBoxes(character, words, lastBox = False):
		line1loc = textTopLeft #where text will go

		#split words into list of words, and include spaces
		#as list items, as well
		wordsList = re.split(r"(\s+)", words)

		lineWidth = 0 #keeps track of how wide a line is

		currentLine = 0 #the line we are on
		maxLineWidth = textTopRight[0] - textTopLeft[0]
		newBox = False
		textboxList = [] #list to store all textbox lists
		printList = ["","",""] #list to build one textbox, 
		#which we will repeatedly use and clear to reuse.
		#I build the list, then add it to the textbox list 
		#when it is filled

		for word in wordsList:
			#need to start a new box on filled box or first word
			wordSurface = font.render(word, True, dialogueColor)
			wordWidth = wordSurface.get_width()
			wordHeight = wordSurface.get_height()
			lineWidth += wordWidth #see potential line width
			#check based on result
			if lineWidth > maxLineWidth:
				#if we need to move to a new line
				currentLine += 1
				lineWidth = 0 #reset line width to 0

				#check if we need to make a new textbox
				if word != " ": #don't start new line with a space
					lineWidth += wordWidth #remember to add width of violating word to new line
					if currentLine < 3: #same box
						printList[currentLine] += word
					else: #different box
						textboxList.append(printList) #add completed box to boxlist
						currentLine = 0 #reset current line
						#new box
						printList = ["","",""]
						printList[currentLine] += word

			else:
				#normally add to line
				#print "ADDING WORD " + word
				printList[currentLine] += word
			if (wordsList.index(word) == len(wordsList)-1): #account for last word not on last part of box
				textboxList.append(printList)
		returnSpace = 40			

		#actually draw the text
		#draw dialogue and name
		textBoxDisplay(textboxList, returnSpace, character, lastBox)

	def textBoxDisplay(boxes, space, character, cursorOff):
		Open = True
		boxnum = 0 
		while Open == True: #while loop until text was all displayed
			gameDisplay.fill(white) #fill BG (to cover previous words b/c box can't b/c transparent)
			#normally blit without waiting
			#draw portrait
			gameDisplay.blit(character.getPortrait(), (portraitCoord[0], portraitCoord[1]-character.getPortrait().get_height()))
			#draw textbox
			gameDisplay.blit(textbox, (boxX,boxY)) 
			#draw name
			gameDisplay.blit(character.getNameSurface(),(character.getNameX(), character.getNameY()))
			#draw the lines in the box
			for line in boxes[boxnum]:
				lineNumber = boxes[boxnum].index(line)
				lineSurface = font.render(line, True, dialogueColor)
				gameDisplay.blit(lineSurface,(textTopLeft[0],textTopLeft[1]+(lineNumber*space)))

				if cursorOff == False or (cursorOff == True and boxnum != (len(boxes)-1)):
					#won't display cursor if on last box of last character's lines
					gameDisplay.blit(cursor,(textBottomRight[0] + cursor.get_width()/2, textBottomRight[1] + cursor.get_height()))

			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_c:
						pygame.mixer.Sound.play(beep)
						pygame.mixer.music.stop()
						if boxnum == (len(boxes)-1): #on last box
							Open = False
							#print "LAST BOX PASSED"
						else:
							boxnum += 1
					elif event.key == pygame.K_q:
						sys.exit()
				elif event.type == pygame.QUIT:
					sys.exit()
			pygame.display.update()

	while not gameExit:
		#starting loop
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
					sys.exit()
			if event.type == pygame.KEYDOWN:
				#pressing c triggers the textbox
				if event.key == pygame.K_c:
					if finished == True:
						finished = False
						sys.exit()
					textToBoxes(zena, "This sentence should become too long and have to go to the next line. Still have to work on new box triggers tho. I like python, and so should all of you people. " +
						"This is a lot of text to write out. Help me think of things, y'all! Like, how much space do you think this is taking up right now? It's waaaaaaaay past the 80-char limit " + 
						"Stephanie likes...")
					textToBoxes(melody, "What am I doing here? I don't want to be here...I have to have a conversation to get out of here, right? Well...I like K-pop. And anime. I'm Melody. Bugs beware!!!")
					textToBoxes(fatimah, "What are y'all doing? Seems fun. Malto bene! Lalala~")
					textToBoxes(charles, "Hello. I've come here to have a conversation with everyone. My name is Charles McAwesomepants. I'm not a sophomore or a senior. I skipped 151 like a boss. I like turtles and coding turtles." +
						" Thank you. I'm going to say more things to fill up more of the box now. Good enough for you?")
					textToBoxes(zena, "...I'm tired. This conversation is over!", True)

					finishedFont = font.render("Your party's bonds have strengthened!", True, dialogueColor)
					gameDisplay.fill(white)
					gameDisplay.blit(finishedFont,((display_width/2)-(finishedFont.get_width()/2),(display_height/2)-finishedFont.get_height()))
					finished = True
				elif event.key == pygame.K_q:
					gameExit = True
		pygame.display.update()
		clock.tick(FPS)
	pygame.quit()
	quit()

gameLoop()