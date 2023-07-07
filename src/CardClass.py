import asyncio, asqlite, json

path_to_db = "../db/"

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
		async with asqlite.connect(path_to_db+"card_data.db") as connection:
			async with connection.cursor() as cursor:
				# Get unique card id from Global Upper Card Table
				await cursor.execute("SELECT * FROM {} WHERE uid={}".format(self.table, self.uid,))

				self.data = await cursor.fetchall()
				#print(self.uid)
				self.data = self.data[0]
				index = self.data["dex"]
				self.rarity = self.data["rarity"]

				#print("index:", index)

				# Get Card stats using corresponding index from table
				await cursor.execute("SELECT * FROM Dex WHERE dex=?", (index,))
				self.stats = await cursor.fetchall()

				#print("Card Stats:", self.stats)

				if self.stats == []:
					return
				else:
					self.stats = self.stats[0]

				await connection.commit()

	def ReturnCard( self ):
		self.Query()
		self.CalcLevel()
		self.CalcStats()


class UserCard:
	def __init__(self, card, data):
		self.id = card["uid"]
		self.dexid = card["dex"]
		self.rarity = card["rarity"]
		self.rarity_mult = 1
		self.level_cap = 1
		self.evo = card["evo"]
		self.exp = card["exp"]
		self.level = 1
		self.name = data["name"]
		self.hp = data["hp"]
		self.atk = data["atk"]
		self.df = data["def"]
		self.spd = data["spd"]
		self.talent = data["talent"]

		self.calcRarity()
		self.calcLevel()
		self.calcStats()

	def calcRarity(self):
		'''Rarity is defined by: 1.2 (C) | 1.4 (UC) | 1.6 (R) | 1.8 (SR) | 2 (UR)'''
		if self.rarity == 'c':
			self.rarity_mult = 1.2
			self.level_cap = 20
			self.rarity = "Common"
		elif self.rarity == 'uc':
			self.rarity_mult = 1.4
			self.level_cap = 30
			self.rarity = "Uncommon"
		elif self.rarity == 'r':
			self.rarity_mult = 1.4
			self.level_cap = 40
			self.rarity = "Rare"
		elif self.rarity == 'sr':
			self.rarity_mult = 1.8
			self.level_cap = 50
			self.rarity = "Super Rare"
		elif self.rarity == 'ur':
			self.rarity_mult = 2.0
			self.level_cap = 60
			self.rarity = "Ultra Rare"
		else:
			self.rarity = -1
			print("Error! Rarity should be c,uc,r,sr,ur")

	def calcLevel(self):
		## DO NOT CHANGE THESE VALUES
		level_exp = [0, 10, 38, 89, 169, 280, 426, 611, 837, 1107, 1423, 1787, 2202, 2670, 3193, 3773, 4413, 5113, 5876, 6704, 7598, 8560, 9591, 10694, 11869, 13119, 14444, 15846, 17327, 18888, 20531, 22257, 24067, 25962, 27944, 30014, 32174, 34424, 36766, 39201, 41730, 44355, 47076, 49895, 52813, 55831, 58950, 62172, 65497, 68927, 72462, 76104, 79853, 83711, 87679, 91757, 95947, 100250, 104667, 109180]
		
		count = 1

		for level in range(len(level_exp)):
			if count <= self.level_cap:
				if self.exp >= level_exp[level]:
					self.level = level+1

			count += 1

	def calcStats(self):
		'''Formula: BaseStat*(Rarity*(1+0.005*Level)*(1+0.15*(Evo-1)))'''
		self.hp = int(round(self.hp*(self.rarity_mult*(1+0.005*self.level)*(1+0.15*(self.evo-1)))))
		self.atk = int(round(self.atk*(self.rarity_mult*(1+0.005*self.level)*(1+0.15*(self.evo-1)))))
		self.df = int(round(self.df*(self.rarity_mult*(1+0.005*self.level)*(1+0.15*(self.evo-1)))))
		self.spd = int(round(self.spd*(self.rarity_mult*(1+0.005*self.level)*(1+0.15*(self.evo-1)))))


class FloorCard(UserCard):
	def __init__(self, location, floor):
		with open(path_to_db+"cards.json", "r") as file:
			series = json.load(file)

		realms = []
		for i in series:
			realms.append(i)

		card = series[realms[location]][floor]
		self.name = card[1]
		self.rarity = "c"
		self.evo = 1
		self.location = location
		self.floor = floor
		self.level = self.location*2+self.floor
		self.hp = card[2]
		self.atk = card[3]
		self.df = card[4]
		self.spd = card[5]
		self.talent = card[6]

		self.calcRarity()
		self.calcStats()


	def Query():
		pass