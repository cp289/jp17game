# File: debuggingMethod.py
# Author: Charles Parham
#
# Note: stats should not be zero as this will likely cause division by zero errors.

import pygame, random

#Define Colors:
# 

class DebuggingMethod:
	
	def __init__(self, name, time, damage):
		self.name = name
		
		#proposed min of 6, max of 9
		self.timeNeeded = time
		
		#what should the range be for the damage?
		self.damage = damage

		#add in attack color
		
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
		c.takeDamage(damage, cannotDie = True)
		self.damageGiven = -damage
	
	def report(self):
		print "Used attack " + self.name + ". Damage: " + str(self.damageGiven) + "\n"
	
	def actions(self, e, c):
		pass

# level 1 attacks
class AskSomeone(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Ask Someone", 4, 500)
		self.desc = "Ask for help to damage a bug."
		
	def actions(self, e, c):
		#if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
		self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
		#else:
			#print "Attack Missed."
		
class PrintStatements(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Use Print Statements", 3, 300)
		self.desc = "May do decent damage to one bug."
		
	def actions(self, e, c):
		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
		else:
			print "Attack Missed."
		
class TakeBreak(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Take a Break", 3, 0)
		self.desc = "Restores 40% of HP."
		
	def actions(self, e, c):
		# Restore 40% max health.
		c.raiseHP(0.4)
	
class ReadProject(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Read Over Project", 2, 0)
		self.desc = "Boosts ACC and ATK for 2 turns."
		
	def actions(self, e, c):
		# boosts ACC and ATK for 2 turns
		if c.ATKBoostTurnsLeft == 0:
			c.ATKBoostTurnsLeft = 3
			c.addTempStat( 'acc', 100 )
			c.addTempStat( 'atk', 100 )


# Not debugging methods, but always present battle actions

# Exit the battle with a random chance
class Flee(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self, "Flee", 0, 0)
		self.desc = "Change your major."
	def actions(self, e, c):
		#chance to flee
		if random.random() < 0.6:
			c.escaped = True
		else:
			print "COULDN'T ESCAPE!"

# Restores all of the player's time
class RestoreTime(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self, "Cancel Plans", 0, 0)
		self.desc = "Rework your schedule. Restores your character's time fully."
	def actions(self, e, c):
		c.fillTime()

# / other battle actions

# / level 1 attacks


# Level 2
class ReferNotes(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Refer to Notes", 1, 100)
		self.desc = "Helps you damage bug a bit."
		
	def actions(self, e, c):
		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
		else:
			print "Attack Missed."

# Level 3
class ReadCode(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Read Code", 2, 0)
		self.desc = "Boosts SPD and DEF for 2 turns."
		
	def actions(self, e, c):
		# boosts SPD & DFN for 2 turns
		print "READ CODE"
		if c.DFNBoostTurnsLeft == 0:
			#keep different from 3 turns for acc/atk
			c.DFNBoostTurnsLeft = 2 
			c.addTempStat( 'spd', 100 )
			c.addTempStat( 'dfn', 100 )

# Level 4
class ShareCode(DebuggingMethod):
	def __init__(self, game):
		DebuggingMethod.__init__(self, "Share Code", 3, 0) # damage?? 
		self.game = game
		self.desc = "Restores chosen partner's HP by 40%."
		
	def actions(self, e, c):
		# boosts chosen partner's hp by 40%
		e.raiseHP(0.4)
		self.oldCursor()
		
	def newCursor(self):
		self.oldArray = self.game.enemies
		self.newArray = self.game.livePlayers
		
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
		self.game.selectedEnemyIDX = 0

# keeping just in case
# class ShareCode(DebuggingMethod):
# 	def __init__(self, game):
# 		DebuggingMethod.__init__(self, "Share Code", 3, 0)
# 		self.game = game
# 		self.desc = "Restores chosen partner's HP by 40%."
# 		self.oldArray = self.game.enemies
# 		self.newArray = self.game.livePlayers
# 		
# 	def actions(self, e, c):
# 		# boosts chosen partner's hp by 40%
# 		e.raiseHP(0.4)
# 		
# 	def newCursor(self):
# 		self.game.enemies = self.newArray
# 
# 		prev = self.game.enemies[self.game.selectedEnemyIDX]
# 		rad = 10
# 		prev.deselect()
# 
# 		# erase selection cursor
# 		eraseRect = pygame.Rect( ( prev.rightEdge - rad, prev.bottomEdge - rad ),
# 								   ( 2 * rad + 2, 2 * rad + 2 ) )
# 		self.game.stage.fillBattleBG( self.game.screen, eraseRect )
# 		
# 	def oldCursor(self):
# 		prev = self.game.enemies[self.game.selectedEnemyIDX]
# 		rad = 10
# 		prev.deselect()
# 
# 		# erase selection cursor
# 		eraseRect = pygame.Rect( ( prev.rightEdge - rad, prev.bottomEdge - rad ),
# 								   ( 2 * rad + 2, 2 * rad + 2 ) )
# 		self.game.stage.fillBattleBG( self.game.screen, eraseRect )
# 		self.game.enemies = self.oldArray
		
# Level 5
class LookTime(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Look at the Clock", 3, 600)
		self.desc = "Does more damage the more time you have."
		
	def actions(self, e, c):

		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			#make damage lower for lower time
			actualDamage = self.damage + self.damage*(c.time/c.maxTime)
			print "ACTUAL DAMAGE: %s" % actualDamage
			self.enemyDamage(e, actualDamage*(float(c.atk)/e.dfn))
		else:
			print "Attack Missed."

# Level 6
class UseInternet(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Use the Internet", 5, 200)
		self.desc = "Damage bug, but take damage if you get distracted."
		
	def actions(self, e, c):
		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))

			# has chance of damaging character in addition to enemy
			if random.random() < 0.4:
				self.characterDamage(c, self.damage)
		else:
			print "Attack Missed."
		
# Level 7
class CommentLines(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Comment Out Lines", 6, 700)
		self.desc = "Does high damage and has critical hit chance."
		
	def actions(self, e, c):
		# high chance of critical hit... What is a critical hit??
		if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
			self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
			#critical hit chance; attacks again
			if random.random() < 0.5+(c.acc-e.spd)/(2*1000):
				self.enemyDamage(e, self.damage*(float(c.atk)/e.dfn))
				print "CRITICAL HIT!"
		else:
			print "Attack Missed."

def main():
	attack=AskBruce() 


if __name__=='__main__':
	main()