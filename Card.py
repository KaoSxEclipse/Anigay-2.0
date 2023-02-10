import asyncio, asqlite

class Card():
	def __init__( self, rarity, uid ):
		self.rarity = rarity
		self.uid = uid
		self.card_data = None
		self.card_stats = None

		if rarity in "uc c r".split(" "):
			self.table = "Lower"
		else:
			self.table = "Upper"


	def Query( self ):
		# Obtain the card information from the Index database and the global card database
		async with asqlite.connect("card_data.db") as connection:
			async with connection.cursor() as cursor:
				# Get unique card id from Global Upper Card Table
				await cursor.execute("SELECT * FROM ? WHERE id=?", (self.table, self.uid,))

				self.card_data = await cursor.fectchall()[0]
				index = card_data["id"]

				# Get Card stats using corresponding index from table
				await cursor.execute("SELECT * FROM Index WHERE index=?", (index,))
				self.card_stats = await cursor.fetchall()[0]


	def CalcLevel( self ):
		pass


	def CalcStats( self ):
		pass

	def ReturnCard( self ):
		self.Query()
		self.CalcLevel()
		self.CalcStats()