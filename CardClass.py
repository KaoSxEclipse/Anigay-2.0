import asyncio, asqlite, json

class CardClass():
	def __init__( self, uid, rarity="sr" ):
		self.rarity = rarity
		self.uid = uid
		self.data = None
		self.stats = None

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

				self.data = await cursor.fetchall()
				print(self.uid)
				self.data = self.data[0]
				index = self.data["dex"]
				self.rarity = self.data["rarity"]

				print("index:", index)

				# Get Card stats using corresponding index from table
				await cursor.execute("SELECT * FROM Dex WHERE dex=?", (index,))
				self.stats = await cursor.fetchall()

				print("Card Stats:", self.stats)

				if self.stats == []:
					return
				else:
					self.stats = self.stats[0]

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




class FloorCard(CardClass):
	def __init__(self, location, floor):
		with open("cards.json", "r") as file:
			series = json.load(file)

		realms = []
		for i in series:
			realms.append(i)

		card = series[realms[location]][floor]
		self.name = card[1]
		self.evo = 1
		self.level = location+floor
		self.hp = card[2]
		self.atk = card[3]
		self.df = card[4]
		self.spd = card[5]
		self.talent = card[6]