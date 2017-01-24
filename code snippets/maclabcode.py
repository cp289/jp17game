	# replace snippet of code below
	def loadHallwayStage( self ):
		# create two doors to robo lab and mac lab
		doorToRoboLab = agents.Door( ( 0, 1365 * scale ), ( 10, 40 / scale ), 'robotics lab' )
		self.hallwayStage.addDoor( doorToRoboLab )

		doorHallwayToMacLab = agents.Door( (  2750 * scale, 3100 * scale ), \
			( 200 * scale, 300 * scale ), 'mac lab' )
		self.hallwayStage.addDoor( doorHallwayToMacLab )
	
	# add entire method
	def enterHallwayStageBack( self ):
		self.stage = self.hallwayStage
		
		# set initial player and camera positions for this room
		self.camera.topleft = 2500 * self.stage.scale, 2000 * self.stage.scale
		initPos = ( 2750 * self.stage.scale, 2800 * self.stage.scale )
		
		self.player.setStagePos( initPos[0], initPos[1] )
		self.placePlayerOnScreen()
		
		self.player.goBackward( self.tileSize )
		
		self.hallwayStage.moveCamView( self.screen, self.refresh, self.camera )
		self.player.draw( self.screen )
		pygame.display.update()
		
		self.sound.play( 'explora', -1 )
		
		print 'enter hallway from mac lab'

	# add entire method
	def loadMacLabStage( self ):
		scale = 0.5
		
		bgOrig = pygame.image.load( 'images/backgrounds/Davis Mac Lab.png' ).convert_alpha()
		newDim = ( int( bgOrig.get_width() * scale ), int( bgOrig.get_height() * scale ) )
		bg = pygame.transform.scale( bgOrig, newDim ) # rescales the background image
		
		battleBGorig = pygame.image.load( 'images/backgrounds/Davis Mac Lab Battle.png' ).convert_alpha()
		battleBG = pygame.transform.scale( battleBGorig, self.screenSize )
		
		bugImgs = [ pygame.image.load( 'images/bugs/Bug 1010.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1011.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1100.png' ).convert_alpha(),
						 pygame.image.load( 'images/bugs/Bug 1101.png' ).convert_alpha()
						]

		self.macLabStage = Stage( 'mac lab', 2, scale, bg, battleBG, bugImgs )

		#def __init__( self, pos, dim, room ):
		doorMacLabtoHallway = agents.Door( (  300 * scale, 800 * scale ), \
			( 290 * scale, 15 * scale ), 'hallway' )
		self.macLabStage.addDoor( doorMacLabtoHallway )
		
		# create walls
		lWall = pygame.Surface( ( 5, self.macLabStage.height ) )
		lWall.set_alpha( 0 ) # set image transparency
		leftWall = agents.Thing( ( -5, 0 ), lWall )
		self.macLabStage.addThing( leftWall )
		
		rWall = pygame.Surface( ( 5, self.macLabStage.height ) )
		rWall.set_alpha( 0 ) # set image transparency
		rightWall = agents.Thing( ( self.macLabStage.width - 5, 0 ), rWall )
		self.macLabStage.addThing( rightWall )
		
		topWallHeight = 715 * scale
		self.macLabStage.setTopWallEdge( topWallHeight )
		tWall = pygame.Surface( ( self.macLabStage.width, topWallHeight ) )
		tWall.set_alpha( 0 ) # set image transparency
		topWall = agents.Thing( ( 0, 0 ), tWall )
		self.macLabStage.addThing( topWall )
	
		bWall = pygame.Surface( ( self.macLabStage.width, 5 ) )
		bWall.set_alpha( 0 ) # set image transparency
		bottomWall = agents.Thing( ( 0, self.macLabStage.height ), bWall )
		self.macLabStage.addThing( bottomWall )
		
		# tables in quadrants 1 and 2
		tTabDim = ( 2900 * scale, 150 * scale )
		tTabPos = ( 950 * scale, 800 * scale )
		tTable = pygame.Surface( tTabDim )
		topHalfTable = agents.Thing( tTabPos, tTable )
		self.macLabStage.addThing( topHalfTable )

		bTabDim = ( 290 * scale, 450 * scale )
		bTabPos = ( 960 * scale, 800 * scale )
		bTable = pygame.Surface( bTabDim )
		bottomHalfTable = agents.Thing( bTabPos, bTable )
		self.macLabStage.addThing( bottomHalfTable )
		
		bTabDim2 = ( 290 * scale, 450 * scale )
		bTabPos2 = ( 1875 * scale, 800 * scale )
		bTable2 = pygame.Surface( bTabDim2 )
		bottomHalfTable2 = agents.Thing( bTabPos2, bTable2 )
		self.macLabStage.addThing( bottomHalfTable2 )

		bTabDim3 = ( 290 * scale, 450 * scale )
		bTabPos3 = ( 2790 * scale, 800 * scale )
		bTable3 = pygame.Surface( bTabDim2 )
		bottomHalfTable3 = agents.Thing( bTabPos3, bTable3 )
		self.macLabStage.addThing( bottomHalfTable3 )

		bTabDim4 = ( 290 * scale, 1628 * scale )
		bTabPos4 = ( 3715 * scale, 800 * scale )
		bTable4 = pygame.Surface( bTabDim4 )
		bottomHalfTable4 = agents.Thing( bTabPos4, bTable4 )
		self.macLabStage.addThing( bottomHalfTable4 )

		# tables in center of background
		cTabDim = ( 820 * scale, 600 * scale )
		cTabPos = ( 669 * scale, 1725 * scale )
		cTable = pygame.Surface( cTabDim )
		centerTable = agents.Thing( cTabPos, cTable )
		self.macLabStage.addThing( centerTable )

		cTabDim2 = ( 820 * scale, 605 * scale )
		cTabPos2 = ( 2235 * scale, 1735 * scale )
		cTable2 = pygame.Surface( cTabDim2 )
		centerTable2 = agents.Thing( cTabPos2, cTable2 )
		self.macLabStage.addThing( centerTable2 )

		# tables in quadrants 3 and 4
		tTabDim2 = ( 290 * scale, 450 * scale )
		tTabPos2 = ( 960 * scale, 2820 * scale )
		tTable2 = pygame.Surface( tTabDim2 )
		topHalfTable2 = agents.Thing( tTabPos2, tTable2 )
		self.macLabStage.addThing( topHalfTable2 )

		tTabDim3 = ( 290 * scale, 450 * scale )
		tTabPos3 = ( 1875 * scale, 2820 * scale )
		tTable3 = pygame.Surface( tTabDim3 )
		topHalfTable3 = agents.Thing( tTabPos3, tTable3 )
		self.macLabStage.addThing( topHalfTable3 )

		tTabDim4 = ( 290 * scale, 450 * scale )
		tTabPos4 = ( 2790 * scale, 2820 * scale )
		tTable4 = pygame.Surface( tTabDim3 )
		topHalfTable4 = agents.Thing( tTabPos4, tTable4 )
		self.macLabStage.addThing( topHalfTable4 )

		tTabDim5 = ( 290 * scale, 450 * scale )
		tTabPos5 = ( 3715 * scale, 2820 * scale )
		tTable5 = pygame.Surface( tTabDim5 )
		topHalfTable5 = agents.Thing( tTabPos5, tTable5 )
		self.macLabStage.addThing( topHalfTable5 )

		bTabDim2 = ( 2900 * scale, 400 * scale )
		bTabPos2 = ( 960 * scale, 3096 * scale )
		bTable2 = pygame.Surface( bTabDim2 )
		bottomHalfTable2 = agents.Thing( bTabPos2, bTable2 )
		self.macLabStage.addThing( bottomHalfTable2 )

		# mac monitor that sticks out in bottom row of tables
		macMonDim = ( 180 * scale, 400 * scale )
		macMonPos = ( 2400 * scale, 3050 * scale )
		macMonSur = pygame.Surface( macMonDim )
		macMonitor = agents.Thing( macMonPos, macMonSur )
		self.macLabStage.addThing( macMonitor )

		# black box in left corner
		blackBoxDim = ( 340 * scale, 520 * scale )
		blackBoxPos = ( 0 * scale, 3130 * scale )
		blackBoxSur = pygame.Surface( blackBoxDim )
		blackBox = agents.Thing( blackBoxPos, blackBoxSur )
		self.macLabStage.addThing( blackBox )

		print 'loaded mac lab stage'
	
	# add entire method
	def enterMacLabStage( self ):
		self.stage = self.macLabStage
		
		# set initial player and camera positions for this room
		
		#self.camera.topleft = 2450 * self.stage.scale, 2850 * self.stage.scale # for scale 0.5
		#initPos = ( 3900 * self.stage.scale, 3672 * self.stage.scale )
		
		self.camera.topleft = 50 * self.stage.scale, 100 * self.stage.scale # for scale 0.4
		initPos = ( 275 * self.stage.scale, 500 * self.stage.scale )
			
		self.player.setStagePos( initPos[0], initPos[1] )
		self.placePlayerOnScreen()
		
		self.player.goForward( self.tileSize )
		
		self.macLabStage.moveCamView( self.screen, self.refresh, self.camera )
		self.player.draw( self.screen )
		pygame.display.update()
		
		print 'enter mac lab'

	# replace snippet of code below
	def updateExplore( self ):
	
		# check for entering a door
		door = self.stage.atDoor( self.player )
		if door != None:
			# if entering a door, determine which room the door leads to
			if door.room == 'robotics lab':
				if self.player.movement[0] == left: # make sure player is going in the correct direction
					self.enterRoboLabStage()
			elif door.room == 'hallway': # if entering the hallway, determine from which room
				if self.stage == self.roboLabStage and self.player.movement[0] == right:
					self.enterHallwayStageLeft()
				if self.stage == self.macLabStage and self.player.movement[0] == back:
					self.enterHallwayStageBack()
			elif door.room == 'mac lab': # make sure player enters mac lab stage
				if self.stage == self.hallwayStage and self.player.movement[0] == front:
					self.enterMacLabStage()
		
	

