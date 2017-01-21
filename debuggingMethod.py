# File: debuggingMethod.py
# Author: Charles Parham
#
# Note: stats should not be zero as this will likely cause division by zero errors.

import random

class DebuggingMethod:
	
	def __init__(self, name, time, damage):
		self.name = name
		
		#proposed min of 6, max of 9
		self.timeNeeded = time
		
		#what should the range be for the damage?
		self.damage = damage
		
	def attack(self, enemy, character): # Needs to be tested!
		# perform desired attack actions
		self.actions(enemy, character)
		
		# decrease time
		character.takeTime(self.timeNeeded)
		
		self.reportDamage()
		
#		if self.attackEffects(): # performs attack actions and determines whether attack requires accuracy
#			if random.random() < 0.5+(character.acc-enemy.spd)/(2*1000): # What should the highest value be for a stat?
#				enemy.takeDamage(self.damage*(character.atk/enemy.dfn))  # Likely to cause problems... adjust scale factor later.
	
	def reportDamage(self):
		print "Used attack " + self.name + ". Damage: " + str(self.damage)
	
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
			e.takeDamage(self.damage*(c.atk/e.dfn))
		
		
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


class ReferNotes(DebuggingMethod): # Level 2
	def __init__(self):
		DebuggingMethod.__init__(self,"Refer to Notes", 1, 100)
		
	def actions(self, e, c):
		pass #

class ReadCode(DebuggingMethod): # Level 3
	def __init__(self):
		DebuggingMethod.__init__(self,"Read Code", 2, 0) # damage???
		
	def actions(self, e, c):
		pass # boosts SPD & DFN for 2 turns

class ShareCode(DebuggingMethod): # Level 4
	def __init__(self):
		DebuggingMethod.__init__(self, "Share Code", 3, 0) # damage??
		
	def actions(self, e, c):
		pass # boosts chosen partner's hp by 40%
		
class LookTime(DebuggingMethod): # Level 5
	def __init__(self):
		DebuggingMethod.__init__(self,"Look at Time", 3, 600) # damage??
		
	def actions(self, e, c):
		pass # has chance of damaging character...

class UseInternet(DebuggingMethod): # Level 6
	def __init__(self):
		DebuggingMethod.__init__(self,"Use the Internet", 5, 0) # damage??
		
	def actions(self, e, c):
		pass # damages all bugs slightly
		
class CommentLines(DebuggingMethod): # Level 7
	def __init__(self):
		DebuggingMethod.__init__(self,"Comment Out Lines", 6, 0) # damage??
		
	def actions(self, e, c):
		pass # high chance of critical hit... What is a critical hit??

def main():
	attack=AskBruce()


if __name__=='__main__':
	main()