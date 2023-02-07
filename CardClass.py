import asyncio, asqlite

class CardClass():
	def __init__( self, rarity="sr", uid='0' ):
		self.rarity = rarity
		self.uid = uid
		self.card_data = None
		self.card_stats = None

		if rarity in "uc c r".split(" "):
			self.table = "Lower"
		else:
			self.table = "Upper"


	async def Query( self ):
		# Obtain the card information from the Index database and the global card database
		async with asqlite.connect("card_data.db") as connection:
			async with connection.cursor() as cursor:
				# Get unique card id from Global Upper Card Table
				await cursor.execute("SELECT * FROM {} WHERE uid={}".format(self.table, self.uid,))

				self.card_data = await cursor.fetchall()
				print(self.card_data)
				self.card_data = self.card_data[0]
				index = self.card_data["dex"]

				print("index:", index)

				# Get Card stats using corresponding index from table
				await cursor.execute("SELECT * FROM Dex WHERE dex=?", (index,))
				self.card_stats = await cursor.fetchall()

				print("Card Stats:", self.card_stats)

				if self.card_stats == []:
					return
				else:
					self.card_stats = self.card_stats[0]

				await connection.commit()

	def checkRarity( self ):
		return


	def CalcLevel( self ):
		pass


	def CalcStats( self ):
		pass

	def ReturnCard( self ):
		self.Query()
		self.CalcLevel()
		self.CalcStats()