import asyncio, asqlite
import json


async def cardDB():
	# Create the Card databases from scratch
	async with asqlite.connect("card_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute( '''CREATE TABLE IF NOT EXISTS Dex (dex integer, name text, hp integer, atk integer, def integer, spd integer, talent text)''' )

			await cursor.execute( '''CREATE TABLE IF NOT EXISTS Upper (uid bigint, owner bigint, dex int, rarity text, evo int, exp int, cd int) ''' )

			#await cursor.execute( "INSERT OR IGNORE INTO Dex VALUES ( 0, 'Zenith', 80, 80, 80, 80, 'Self Destruct' )" )
			#await cursor.execute( "INSERT OR IGNORE INTO Dex VALUES ( 1, 'DPython', 100, 100, 100, 100, 'White Justice' )" )

			#await cursor.execute( "INSERT OR IGNORE INTO Upper VALUES ( 1, 0, 'sr', 1, 0, 0 )" )

			await connection.commit()


async def playerDB():
	# Create the User Database if it doesn't exist
	async with asqlite.connect("player_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute( '''CREATE TABLE IF NOT EXISTS Users (id bigint, exp int, wuns int, stamina int, card int)''' )

			await connection.commit()


async def generateCard( index, owner, rarity, evo ):
	async with asqlite.connect("card_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute("SELECT max(uid) FROM Upper")

			max_id = await cursor.fetchall()
			try:
				new_id = int(max_id[0][0]) + 1
			except TypeError:
				new_id = 1

			await cursor.execute( "INSERT OR IGNORE INTO Upper VALUES ( ?, ?, ?, ?, ?, 0, 0 )", (new_id, owner, index, rarity, evo) )

			await connection.commit()


async def generateCardList():
	async with asqlite.connect("card_data.db") as connection:
		async with connection.cursor() as cursor:
			await cursor.execute("SELECT * FROM Dex")

			cards = await cursor.fetchall()
			names = []
			for i in cards:
				names.append(i["name"])


			cards = names
			#print(cards)
			return cards


#asyncio.run(playerDB())
#asyncio.run(cardDB())

#asyncio.run( generateCardList() )

#asyncio.run(generateCard(0, 0, 'sr', 1))