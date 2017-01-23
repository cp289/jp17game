# File: debuggingMethod.py
# Author: Charles Parham
#
# Note: stats should not be zero as this will likely cause division by zero errors.

import pygame, random

class DebuggingMethod:
	
	def __init__(self, name, time, damage):
		self.name = name
		
		#proposed min of 6, max of 9
		self.timeNeeded = time
		
		#what should the range be for the damage?
		self.damage = damage
		
		self.damageGiven = 0
		
	def attack(self, enemy, character): # Needs to be tested!
		# reset damage given
		self.damageGiven = 0
		
		# perform desired attack actions
		self.actions(enemy, character)
		
		self.report()
		
		# decrease time
		character.takeTime(self.timeNeeded)
		
#		if self.attackEffects(): # performs attack actions and determines whether attack requires accuracy
#			if random.random() < 0.5+(character.acc-enemy.spd)/(2*1000): # What should the highest value be for a stat?
#				enemy.takeDamage(self.damage*(character.atk/enemy.dfn))  # Likely to cause problems... adjust scale factor later.
	
	def enemyDamage(self, e, damage):
		self.damageGiven = damage
		e.takeDamage(damage)
	
	def characterDamage(self, c, damage):
		c.takeDamage(damage)
		self.damageGiven = -damage
	
	def report(self):
		print "Used attack " + self.name + ". Damage: " + str(self.damageGiven) + "\n"
	
	def actions(self, e, c):
		pass

# Use these attacks ?
class AskBruce(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Ask Bruce", 4, 700)
		
class Google(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Google Search", 1, 100)
# ??


# level 1 attacks
class AskSomeone(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Ask Someone", 4, 500) # affects all bugs?? No. Why would we select a single one?
		
	def actions(self, e, c):
		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
		else:
			print "Attack Missed."
		
class PrintStatements(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Use Print Statements", 3, 300)
		
class TakeBreak(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Take a Break", 3, 0)
		
	def actions(self, e, c):
		# Restore 40% max health.
		c.raiseHP(0.4)
	
class ReadProject(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Read Over Project", 2, 0)
		
	def actions(self, e, c):
		# boosts ACC and ATK for 2 turns
		c.addTempStat( 'acc', 100, 2 )
		c.addTempStat( 'acc', 100, 2 )

# / level 1 attacks


# Level 2
class ReferNotes(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Refer to Notes", 1, 100)
		
	def actions(self, e, c):
		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
		else:
			print "Attack Missed."

# Level 3
class ReadCode(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Read Code", 2, 0) # damage???
		
	def actions(self, e, c):
		# boosts SPD & DFN for 2 turns
		c.addTempStat( 'spd', 100, 2 )
		c.addTempStat( 'dfn', 100, 2 )

# Level 4
class ShareCode(DebuggingMethod):
	def __init__(self, game):
		DebuggingMethod.__init__(self, "Share Code", 3, 0) # damage?? 
		self.game = game
		self.oldArray = self.game.enemies
		self.newArray = self.game.livePlayers
		
	def actions(self, e, c):
		# boosts chosen partner's hp by 40%
		e.raiseHP(0.4)
		
	def newCursor(self):
		self.game.enemies = self.newArray

		prev = self.game.enemies[self.game.selectedEnemyIDX]
		rad = 10
		prev.deselect()

		# erase selection cursor
		eraseRect = pygame.Rect( ( prev.rightEdge - rad, prev.bottomEdge - rad ),
								   ( 2 * rad + 2, 2 * rad + 2 ) )
		self.game.stage.fillBattleBG( self.game.screen, eraseRect )
		
	def oldCursor(self):
		prev = self.game.enemies[self.game.selectedEnemyIDX]
		rad = 10
		prev.deselect()

		# erase selection cursor
		eraseRect = pygame.Rect( ( prev.rightEdge - rad, prev.bottomEdge - rad ),
								   ( 2 * rad + 2, 2 * rad + 2 ) )
		self.game.stage.fillBattleBG( self.game.screen, eraseRect )
		self.game.enemies = self.oldArray
		
# Level 5
class LookTime(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Look at Time", 3, 600)
		
	def actions(self, e, c):
		# has chance of damaging character...
		if random.random() < 0.4:
			self.characterDamage(c, self.damage)
		else:
			if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
				self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
			else:
				print "Attack Missed."

# Level 6
class UseInternet(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Use the Internet", 5, 200)
		
	def actions(self, e, c):
		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
		else:
			print "Attack Missed."
		
# Level 7
class CommentLines(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Comment Out Lines", 6, 700)
		
	def actions(self, e, c):
		# high chance of critical hit... What is a critical hit??
		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
		else:
			print "Attack Missed."

def main():
	attack=AskBruce() 


if __name__=='__main__':
	main()