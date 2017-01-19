
class DebuggingMethod:
	
	def __init__(self, name, time, damage):
		self.name=name
		
		#proposed min of 6, max of 9
		self.time_needed=time
		
		#what should the range be for the damage?
		self.damage=damage

class AskBruce(DebuggingMethod):
	
	def __init__(self):
		
		DebuggingMethod.__init__(self,"Ask Bruce", 5, 300)
		
	

def main():
	attack=AskBruce()
	


if __name__=='__main__':
	main()