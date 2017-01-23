#Zena Abulhab
#CS269j 
#Conversation Class
#Makes a conversation object with the given text
#and characters to say it
import sys
import re #used to split text including spaces
import pygame

black = (0,0,0)
red = (255,0,0)
white = (255,255,255)

#load and set textbox dimensions and location

class Conversation():
	def __init__(self, textboxImg, textboxCoord, cursor, window, charList, convoFont, nameFont, textFile):

		self.textboxImg = textboxImg
		self.cursor = cursor
		self.currentBoxIdx = 0
		self.convoNum = 0
		self.convoOver = False

		self.charList = charList

		self.window = window
		self.winWidth, self.winHeight = window.get_size()

		self.boxWidth, self.boxHeight = textboxImg.get_size()
		self.boxX, self.boxY = textboxCoord

		#where text in a convo is first blitted
		self.upperLeft = [self.winWidth-self.boxWidth+44, self.winHeight-self.boxHeight+63]
		self.nameBoxCenterLeft = [self.boxX+18, self.boxY-47]

		self.cursorCoords = (self.boxX + self.boxWidth - 40, self.boxY + self.boxHeight -cursor.get_height() - 20)

		self.convoFont = convoFont
		self.nameFont = nameFont

		self.lineSkipSpace = 40

		self.allConvos = self.makeConvos(textFile)

	def displayText(self, convoNum):
		print "CALLING DISPLAYTEXT"
		self.convoNum = convoNum
		self.convoOver = False
		# no more convo to display, meaning last box is being 
		# displayed right now
		if len(self.allConvos[convoNum])<(self.currentBoxIdx*2)+1:
		 	print "END OF CONVO"
		 	self.convoOver = True
		 	self.currentBoxIdx = 0
		else:
			# draw new dialogue box
			name = self.allConvos[self.convoNum][self.currentBoxIdx*2][:-1] # exclude ":"
			currentText = self.allConvos[self.convoNum][(self.currentBoxIdx*2)+1]
			print "CONVONUM: ", convoNum
			print "CURRENTTEXT: %s" % currentText


			#search for char portrait that will display when talking
			#and the coords of the name when placed in the textbox
			charHead = None
			nameSurf = None
			nameCoords = None
			headSize = None
			for char in self.charList:
				if char.name == name:
					if char.hasimgConvo == True:
						charHead = char.imgConvo
						headSize = char.imgConvo.get_size()
					if "_" in char.name:
						nameToUse = char.name.replace("_"," ")
					else:
						nameToUse = char.name
					nameSurf = self.nameFont.render(nameToUse, True, red)
					nameCoords = self.nameBoxCenterLeft[0] + char.namePos[0], \
						self.nameBoxCenterLeft[1] + char.namePos[1]
			#blit head and name
			if charHead != None:
				headCoords = (self.boxX, self.boxY - headSize[1]+50)
				self.window.blit(charHead, headCoords)

			# blit textbox
			self.window.blit(self.textboxImg,(self.boxX,self.boxY))

			if nameSurf == None:
				print "NO NAMESURF FSR"
			self.window.blit(nameSurf, (nameCoords[0], nameCoords[1]+50))


			# blit 3 lines of text, even if some are empty
			line0 = self.convoFont.render(currentText[0], True, black)
			line1 = self.convoFont.render(currentText[1], True, black)
			line2 = self.convoFont.render(currentText[2], True, black)
			self.window.blit(line0, (self.upperLeft[0],self.upperLeft[1]))
			self.window.blit(line1, (self.upperLeft[0],self.upperLeft[1]+self.lineSkipSpace))
			self.window.blit(line2, (self.upperLeft[0],self.upperLeft[1]+(2*self.lineSkipSpace)))

			#if not on last box
			if len(self.allConvos[self.convoNum]) > (self.currentBoxIdx*2)+2:
				self.window.blit(self.cursor, self.cursorCoords)

	def advanceText(self):
		#move to display next box, if there is one
		self.currentBoxIdx += 1
		self.displayText(self.convoNum)

	#opens the file and separates all of the conversations
	def makeConvos(self, filename):
		textFile = file(filename, "r") #read file
		lines = textFile.read().splitlines() #separate lines, excluding /n
		textFile.close()
		convoList = []
		newConvo = False
		linesList = [] #list of string lists for given lines;
		#refreshes every new convo

		#adds to the convo list
		for line in lines:
			#split into words, including spaces
			wordsList = re.split(r"(\s+)", line)
			#skip empty lines
			if len(line.strip()) == 0: 
				continue
			#end conversation
			elif wordsList[0] == "[END]":
				newConvo = False
				convoList.append(linesList)
				linesList = [] # clear lines list
			#new conversation
			elif wordsList[0] == "Convo":
				newConvo = True
				continue #go to next line
			#still in conversation
			elif newConvo == True:
				#append all the strings
				linesList.append(wordsList)
		
		return self.makeTextboxes(convoList)

	#splits all of the text to fit in a given textbox image
	def makeTextboxes(self, conversations):
		convList = [] #list of conversations to return at the end
		samePerson = False #if true, a "\" was used to connect lines of text

		#Adds lists of person-talking strings to each conversation and
		#joins lines otherwise separated in the file by a "\"
		for conversation in conversations:
			#represents list of each person's uninterrupted string of words, 
			#when the person talking stays the same
			wholeLineList = []
			wholeLine = "" 
			for line in conversation:
				
				for word in line:
					if len(word) > 0:
						if word[0] == "\\":
							samePerson = True
							#account for missing space
							wholeLine += " " + word[1:]
						else:
							wholeLine += word
				if samePerson != True:
					wholeLineList.append(wholeLine)
				else:
					wholeLineList[-1] += wholeLine #join to previous line
					samePerson = False
				wholeLine = "" #clear line

			convList.append(wholeLineList)	

		#divide all text into boxes to display
		maxLineWidth = self.boxWidth - 80 -self.cursor.get_width()
		boxesList = [] #holds lists of strings indicating dialogue strings per box
					   #and also holds the person speaking before it
		returnList = [] #list of convos (list of boxesLists)
		for conv in convList:
			for personTurn in conv:
				currentLine = 0
				currentWidth = 0 #current line width
				textboxString = ""
				wordsAndSpacesList = re.split(r"(\s+)", personTurn)
				personTalking = wordsAndSpacesList[0]
				#list of strings to blit to one box.
				#will be cleared and reused often
				blitList = ["","",""]
				for blitChar in wordsAndSpacesList[2:]:
					charSurface = self.convoFont.render(blitChar, True, black)
					charWidth = charSurface.get_width()
					currentWidth += charWidth

					if currentWidth > maxLineWidth:
						#move to new line
						currentLine += 1
						currentWidth = 0 #reset width
						#check if we need to make a new textbox
						if blitChar != " ": #don't start new line with a space
							currentWidth += charWidth #remember to add width of violating word to new line
						if currentLine < 3: #same box
							if blitChar != " ": #exclude spaces
								blitList[currentLine] += blitChar
						else: #different box
							#add person name and completed box to boxlist
							boxesList.extend([personTalking, blitList]) 
							currentLine = 0 #reset current line
							#new box
							blitList = ["","",""]
							if blitChar != " ":#exclude spaces
								blitList[currentLine] += blitChar
					else:
						#normally add to line
						#print "ADDING WORD " + word
						blitList[currentLine] += blitChar

					#account for blitting things that don't reach the end of a line
					if (wordsAndSpacesList.index(blitChar) == len(wordsAndSpacesList)-1): 
						boxesList.extend([personTalking, blitList])		
			returnList.append(boxesList)
			boxesList = []
		return returnList


#TESTING:

#allConvos = makeConvos("dialogue.txt")

# convo = Conversation(textbox)

# inDialogue = False
# while 1:
# 	for event in pygame.event.get():
# 		if event.type == pygame.QUIT:
# 					sys.exit()
# 		if event.type == pygame.KEYDOWN:
# 			if event.key == pygame.K_c:
# 				if inDialogue == False:
# 					inDialogue = True
# 					convo.displayText(2)
# 				else:
# 					convo.advanceText()
# 	pygame.display.update()
# pygame.quit()
# quit()
