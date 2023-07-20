import asyncio, asqlite
import json

path_to_db = "../db/"

async def cardDB():
	# Create the Card databases from scratch
	async with asqlite.connect(path_to_db+"card_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute('''DROP TABLE Dex''')

			await cursor.execute( '''CREATE TABLE IF NOT EXISTS Dex (dex integer, name text, element text, hp integer, atk integer, def integer, spd integer, talent text)''' )

			await cursor.execute( '''CREATE TABLE IF NOT EXISTS Upper (uid bigint, owner bigint, dex int, rarity text, evo int, exp int, cd int) ''' )

			await cursor.execute( '''CREATE TABLE IF NOT EXISTS Lower (uid bigint, owner bigint, dex int, rarity text DEFAULT r, cd int) ''' )

			await dumpCard()

			await connection.commit()


async def playerDB():
	# Create the User Database if it doesn't exist
	async with asqlite.connect(path_to_db+"player_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute( '''CREATE TABLE IF NOT EXISTS Users (id bigint, exp int, wuns int, stamina int, card int, location DECIMAL(6,3), maxloc DECIMAL(6,3) )''' )

			#\\await cursor.execute("ALTER TABLE Users ADD maxloc REAL DEFAULT 1.001 NOT NULL")

			#await cursor.execute("ALTER TABLE Users ADD location REAL DEFAULT 1.001 NOT NULL")

			#await cursor.execute("ALTER TABLE Users ADD location REAL DEFAULT 1.001 NOT NULL")

			await connection.commit()



async def verifyUser( user_id ):
	async with asqlite.connect(path_to_db+"player_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute( "SELECT * FROM Users WHERE id=?", (user_id,) )
			user_data = await cursor.fetchall()
			await connection.commit()
			
			return user_data



async def generateCard( index, owner, rarity, evo ):
	async with asqlite.connect(path_to_db+"card_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute("SELECT max(uid) FROM Upper")

			max_id = await cursor.fetchall()
			try:
				new_id = int(max_id[0][0]) + 1
			except TypeError:
				new_id = 1

			print("Database: ", index)
			await cursor.execute( "INSERT OR IGNORE INTO Upper VALUES ( ?, ?, ?, ?, ?, 0, 0 )", (new_id, owner, index, rarity, evo) )

			await connection.commit()


async def generateFodder( owner, index  ):
	async with asqlite.connect(path_to_db+"card_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute("SELECT max(uid) FROM Upper")

			max_id = await cursor.fetchall()

			await cursor.execute("SELECT max(uid) FROM Lower")
			max_id_2 = await cursor.fetchall()

			try:
				if max_id[0][0] < max_id_2[0][0]:
					new_id = int(max_id_2[0][0]) + 1
				else:
					new_id = int(max_id[0][0]) + 1
			except TypeError:
				new_id = int([max_id][0][0][0]) + 1

			await cursor.execute( "INSERT OR IGNORE INTO Lower VALUES ( ?, ?, ?, 'r', 0 )", (new_id, owner, index) )			



async def generateCardList():
	async with asqlite.connect(path_to_db+"card_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute("SELECT * FROM Dex")

			cards = await cursor.fetchall()
			names = []
			for i in cards:
				names.append(i["name"])


			cards = names
			#print(cards)
			return cards


d = {
	"Jujutsu Kaisen": (
		( 5, 'Kento Nanami', 'Ground', 69, 92, 84, 80, 'Pain for Power' ),
		( 6, 'Megumi Fushiguro', 'Light', 86, 71, 92, 78, 'Endurance' ),
		( 7, 'Nobara Kugisaki', 'Ground', 95, 73, 78, 85, 'Evasion' ),
		( 8, 'Ryomen Sukuna', 'Fire', 85, 78, 85, 78, 'Life Sap' ),
		( 9, 'Satoru Gojo', 'Electric', 86, 83, 78, 78, 'Berserker' ),
		( 10, 'Toge Inumaki', 'Neutral', 86, 89, 73, 81, 'Paralysis' ),
		( 11, 'Yuji Itadori', 'Ground', 80, 90, 75, 85, 'Unlucky Coin' ),
		( 12, 'Yuta Okkotsu', 'Dark', 85, 93, 73, 76, 'Paralysis' ) ,
	),
	"Demon Slayer": (
		( 13, 'Giyu Tomioka', 'Water', 76, 80, 81, 93, 'Double-edged Strike' ),
		( 14, 'Inosuke Hashibira', 'Dark', 90, 88, 81, 62, 'Amplifier' ),
		( 15, 'Kanao Tsuyuri', 'Neutral', 69, 81, 96, 77, 'Berserker' ),
		( 16, 'Kyojuro Rengoku', 'Fire', 81, 93, 74, 80, 'Berserker' ),
		( 17, 'Muzan Kibutsuji', 'Dark', 95, 75, 80, 75, 'Devour' ),
		( 18, 'Nezuko Kamado', 'Dark', 84, 82, 80, 78, 'Vengeance' ),
		( 19, 'Obanai Iguro', 'Light', 77, 90, 85, 75, 'Poison' ),
		( 20, 'Shinobu Kocho', 'Grass', 93, 83, 80, 72, 'Poison' ),
		( 21, 'Tanjiro Kamado', 'Water', 80, 82, 77, 89, 'Berserker' ),
		( 22, 'Zenitsu Agatsuma', 'Electric', 80, 73, 87, 88, 'Paralysis' ), 
	),
	"Chainsaw Man": (
		( 23, 'Aki Hayakawa', 'Dark', 79, 94, 76, 80, 'Temporal Rewind' ),
		( 24, 'Angel Devil', 'Neutral', 88, 91, 73, 76, 'Life Sap' ),
		( 25, 'Chainsaw man', 'Dark', 69, 102, 86, 69, 'Bloodthirster' ),
		( 26, 'Denji', 'Neutral', 84, 88, 91, 70, 'Paralysis' ),
		( 27, 'Himeno', 'Grass', 78, 93, 82, 72, 'Pain For Power' ),
		( 28, 'Makima', 'Dark', 84, 92, 80, 76, 'Miracle Injection' ),
		( 29, 'Power', 'Dark', 73, 92, 86, 82, 'Regeneration' ),
		( 30, 'Reze', 'Dark', 73, 101, 83, 70, 'Time Bomb' )
	)
}

with open(path_to_db+"cards.json", "w") as file:
		json.dump( d, file, indent=4 )

async def dumpCard():
	## id, name, hp ,atk, def, spd, talent

	with open(path_to_db+"cards.json", "w") as file:
		json.dump( d, file, indent=4 )

	async with asqlite.connect(path_to_db+"card_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute( "INSERT OR IGNORE INTO Dex VALUES ( 0, 'Zenith', 'Dark', 80, 80, 80, 80, 'Self Destruct' )" )
			await cursor.execute( "INSERT OR IGNORE INTO Dex VALUES ( 1, 'DPython', 'Light', 100, 100, 100, 100, 'White Justice' )" )

			for series in d:
				for card in d[series]:
					print(card)
					await cursor.execute( "INSERT OR IGNORE INTO Dex VALUES ( ?, ?, ?, ?, ?, ?, ?, ? )", (card[0], card[1], card[2], card[3], card[4], card[5], card[6], card[7]) )

			await connection.commit()



asyncio.run(dumpCard())

#asyncio.run(cardDB()) ##--> DO NOT RUN THIS COMMAND!!

#asyncio.run(playerDB())
#asyncio.run(cardDB())
#asyncio.run(generateFodder(1, 1))

#asyncio.run( generateCardList() )

#asyncio.run(generateCard(0, 0, 'sr', 1))