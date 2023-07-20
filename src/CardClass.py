import asyncio, asqlite, json

path_to_db = "../db/"
ACTIVE_TALENTS = ["Amplifier", "Balancing Strike", "Blaze", "Breaker", "Celestial Blessing", "Devour", "Dexterity Drive", "Double-edged Strike", "Elemental Strike", "Endurance", "Evasion", "Freeze", "Lucky Coin", "Mana Reaver", "Offensive Stance", "Pain For Power", "Paralysis", "Poison", "Precision", "Regeneration", "Rejuvenation", "Restricted Instinct", "Smokescreen", "Time Attack", "Time Bomb", "Trick Room", "Ultimate Combo", "Unlucky Coin", "Vengeance" ]

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
					print("ERROR Card has no stats")
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
		self.rarity_s = ""
		self.rarity_mult = 1
		self.level_cap = 1
		self.evo = card["evo"]
		self.exp = card["exp"]
		self.level = 1
		self.name = data["name"]
		self.element = data["element"]
		self.hp = data["hp"]
		self.mana = 0
		self.atk = data["atk"]
		self.df = data["def"]
		self.spd = data["spd"]
		self.talent = data["talent"]
		self.talent_proc = False

		self.calcRarity()
		self.calcLevel()
		self.calcStats()

		if self.talent in ACTIVE_TALENTS:
			self.max_mana = 100
		else:
			self.max_mana = 0

		self.max_hp = self.hp*10
		self.current_atk = self.atk*10
		self.base_df = self.df*10
		self.ele_mult = 1
		self.evasion = 1
		self.critical_mult = 1
		self.critical_rate = 5
		self.healing_bonus = 0
		self.lifesteal = 0
		self.stunned = False
		self.regen_stacks = 0
		self.regen_lose = []


	def calcRarity(self):
		'''Rarity is defined by: 1.2 (C) | 1.4 (UC) | 1.6 (R) | 1.8 (SR) | 2 (UR)'''
		if self.rarity == 'c':
			self.rarity_mult = 1.2
			self.level_cap = 20
			self.rarity = "Common"
			self.rarity_s = "C"
		elif self.rarity == 'uc':
			self.rarity_mult = 1.4
			self.level_cap = 30
			self.rarity = "Uncommon"
			self.rarity_s = "UC"
		elif self.rarity == 'r':
			self.rarity_mult = 1.4
			self.level_cap = 40
			self.rarity = "Rare"
			self.rarity_s = "R"
		elif self.rarity == 'sr':
			self.rarity_mult = 1.8
			self.level_cap = 50
			self.rarity = "Super Rare"
			self.rarity_s = "SR"
		elif self.rarity == 'ur':
			self.rarity_mult = 2.0
			self.level_cap = 60
			self.rarity = "Ultra Rare"
			self.rarity_s = "UR"
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
		self.hp = int(self.hp*(self.rarity_mult*(1+0.005*self.level)*(1+0.15*(self.evo-1))))
		self.atk = int(self.atk*(self.rarity_mult*(1+0.005*self.level)*(1+0.15*(self.evo-1))))
		self.df = int(self.df*(self.rarity_mult*(1+0.005*self.level)*(1+0.15*(self.evo-1))))
		self.spd = int(self.spd*(self.rarity_mult*(1+0.005*self.level)*(1+0.15*(self.evo-1))))


	def battlePrep(self):
		self.hp *= 10
		self.atk *= 10
		self.df *= 10
		self.spd *= 10


	def __str__(self):
		return """
{}:
HP:  {}/{}
MP:  {}
ATK: {}[{}]
DEF: {}
SPD: {}
		""" .format(self.name, self.hp, self.max_hp, self.mana, self.atk, self.current_atk, self.df, self.spd)


class FloorCard(UserCard):
	def __init__(self, location, floor):
		with open(path_to_db+"cards.json", "r") as file:
			series = json.load(file)

		realms = []
		for i in series:
			realms.append(i)

		card = series[realms[location-1]][floor-1]

		self.realm_name = series[realms[location-1]]
		self.name = card[1]
		self.rarity = "r"
		self.evo = 1
		self.location = location
		self.floor = floor
		self.level = self.location+(self.floor*2)
		self.element = card[2]
		self.hp = card[3]
		self.mana = 0
		self.atk = card[4]
		self.df = card[5]
		self.spd = card[6]
		self.talent = card[7]
		self.talent_proc = False

		self.calcRarity()
		self.calcStats()

		if self.talent in ACTIVE_TALENTS:
			self.max_mana = 100
		else:
			self.max_mana = 0

		self.max_hp = self.hp*10
		self.current_atk = self.atk*10
		self.ele_mult = 1
		self.evasion = 1
		self.critical_rate = 5
		self.critical_mult = 1
		self.healing_bonus = 0
		self.lifesteal = 0
		self.stunned = False
		self.regen_stacks = 0
		self.regen_lose = []


	async def getDex(self):
		async with asqlite.connect(path_to_db+"card_data.db") as connection:
			async with connection.cursor() as cursor:
				# Get unique card id from Global Upper Card Table
				await cursor.execute("SELECT * FROM Dex WHERE name = ?", (self.name,))
				card = await cursor.fetchall()
				card = card[0]
				
				return card["dex"]

	def Query():
		pass