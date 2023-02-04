import asyncio, asqlite
"""'''
with asqlite.connect("card_data.db") as connection:
	with connection.cursor() as cursor():
		cursor.execute( '''CREATE TABLE Index
							()
			''' )"""



integer = 1092387000

integer = str(integer)
new_num = ""

for i in range(len(integer)-1, -1, -1):
	if i%3 == 0:
		print("comma")
		new_num += ","

	##print(i)
	new_num += integer[i]

new_num = new_num[1:]
new_num = new_num[::-1]


print(new_num)


def displayNumber( number ):
	integer = str(integer)
	new_num = ""

	for i in range(len(integer)-1, -1, -1):
		if i%3 == 0:
			print("comma")
			new_num += ","

		new_num += integer[i]

	new_num = new_num[1:]
	new_num = new_num[::-1]

	return new_num #String