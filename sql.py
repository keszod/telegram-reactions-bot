import sqlite3

class SQLighter:

	def __init__(self,database_file):
		"""Подключаемся к БД и сохраняем курсор соединения"""
		self.connection = sqlite3.connect(database_file, check_same_thread=False)
		self.execute = self.connection.cursor().execute

	def channel_exists(self,channel_id):
		with self.connection:
			result = self.execute("SELECT * FROM `channels` WHERE `channel_id` = ?",(channel_id,)).fetchall()
			return bool(len(result))

	def post_exists(self,channel_id,message_id):
		with self.connection:
			result = self.execute("SELECT * FROM `posts` WHERE `channel_id` = ? AND `message_id` = ?",(channel_id,message_id,)).fetchall()
			return bool(len(result))

	def get_all_posts(self):
		with self.connection:
			result = self.execute("SELECT * FROM `posts`").fetchall()
			return result

	def get_all_channels(self):
		with self.connection:
			result = self.execute("SELECT * FROM `channels`").fetchall()
			
			return result

	def get_specific_channel(self,channel_id):
		with self.connection:
			result = self.execute("SELECT * FROM `channels` WHERE`channel_id` = ?",(channel_id,)).fetchall()
			
			return result

	def get_channels_post(self,channel_id):
		with self.connection:
			result = self.execute("SELECT * FROM `posts` WHERE `channel_id` = ?",(channel_id,)).fetchall()
			return result

	def update_channel(self,channel_id,average_30,average_60):
		print(channel_id,average_30,average_60)
		with self.connection:
			return self.execute("UPDATE `channels` SET `average_30_min` = ? , `average_1_h` = ? WHERE `channel_id` = ?",(str(average_30),str(average_60),str(channel_id),))
	
	def add_channel(self,channel_id):
		with self.connection:
			return self.execute("INSERT INTO `channels` (`channel_id`) VALUES (?)",(channel_id,))

	def add_post(self,channel_id,message_id,date):
		with self.connection:
			return self.execute("INSERT INTO `posts` (`channel_id`,`message_id`,`date`) VALUES (?,?,?)",(channel_id,message_id,date,))

	def update_post(self,reactions,channel_id,message_id,param):
		with self.connection:
			return self.execute(f"UPDATE `posts` SET `{param}` = ? WHERE `channel_id` = ? AND `message_id` = ?",(str(reactions),str(channel_id),str(message_id),))

	def close(self):
		self.connection.close()