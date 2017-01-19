
# Note: stats should not be zero as this will likely cause division by zero errors.

import random

class DebuggingMethod:
	
	def __init__(self, name, time, damage):
		self.name=name
		
		#proposed min of 6, max of 9
		self.time_needed=time
		
		#what should the range be for the damage?
		self.damage=damage
		
	def attack(self, enemy, character): # Needs to be tested!
		if random.random() < 0.5+(character.acc-enemy.spd)/(2*1000): # What should the highest value be for a stat?
			enemy.takeDamage(self.damage*(character.atk/enemy.dfn))  # Likely to cause problems... adjust scale factor later.
	
	def attackEffects():
		pass

class AskBruce(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Ask Bruce", 4, 700)
		
class AskSomeone(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Ask Someone", 5, 500)
		
class PrintStatements(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Use Print Statements", 3, 300)
		
class Google(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Google Search", 1, 100)

class TakeBreak(DebuggingMethod):
	def __init__(self):
		DebuggingMethod.__init__(self,"Take a Break", 3, 0)
		
	def attackEffects():
		pass	# Restore 40% max health.
	

def main():
	attack=AskBruce()


if __name__=='__main__':
	main()