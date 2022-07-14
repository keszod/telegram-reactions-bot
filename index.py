# -*- coding: utf-8 -*-
import os
import traceback
from threading import Thread
from pyrogram import Client, filters
import asyncio
from time import sleep
from sql import	SQLighter
from datetime import datetime, timezone, timedelta
import re
from telethon.sync import TelegramClient
from telethon import functions, types


api_id = 19626823
api_hash = "b7d11e9fd7349b31ede4a5e31e41d9da"
app = Client('my_account',api_id=api_id, api_hash=api_hash)
client = TelegramClient('name', api_id, api_hash)

debug = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.db")

db = SQLighter(db_path)

def check_messages():
	with client:
		result = [d.message for d in client.get_dialogs()]
	
	for message in result:
		try:
			channel_id = message.peer_id.channel_id
			channel_id = '-100'+str(channel_id)
		except:
			continue

		message_id = message.id
		
		if db.post_exists(channel_id,message_id):
			continue
		
		if not db.channel_exists(channel_id):
			db.add_channel(channel_id)

		now = datetime.now(timezone.utc)
		date = message.date

		if (now - date).seconds < 40*60:
			if len(message.text) > 20:
				print(message.text[0:10]+'...')
			else:
				print(message.text)
			
			db.add_post(channel_id,message_id,date)
			print(channel_id,message_id,'added')

@app.on_message()
def what_channel(client,message):
        print(message.chat.id)

def forward_message(channel_id,message_id,precent,average):
        print('forwarding')
        with app:
	        text = str(precent)+'%'
		
		app.send_message(chat_id=-727487371,text=text)
		app.forward_messages(chat_id=-727487371,from_chat_id=int(channel_id),message_ids=int(message_id))

def check_reactions(chat_id,message_id):	
	with app:
	        reactions = app.get_messages(int(chat_id), int(message_id)).reactions
	count = 0
	
	if not reactions:
		return count

	for reaction in reactions:
		count += reaction.count

	sleep(2)

	return count


def check_channels():
	with open('time_set.txt','r',encoding='utf-8-sig') as file:
		date = datetime.strptime(file.read(),'%d-%m-%Y %H:%M:%S')
	
	if not datetime.now() >= date:
		return

	channels = db.get_all_channels()

	for channel in channels:
		channel = channel[1]
		all_30 = 0
		all_60 = 0
		posts = db.get_channels_post(channel)
		count = 0
		
		for post in posts:
			date = datetime.strptime(post[3].split('+')[0],'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
			diff = datetime.now(timezone.utc) - date

			if diff.days > 2:
				continue
			
			if int(post[-1]) == 0:
				continue
			
			all_30 += int(post[-2])
			all_60 += int(post[-1])
			count += 1
		
		if count == 0:
			continue

		average_30 = all_30 // count  
		average_60 = all_60 // count

		db.update_channel(channel,average_30,average_60)

	set_time()


def set_time():
	with open('time_set.txt','w',encoding='utf-8-sig') as file:
		file.write((datetime.now() + timedelta(days=1)).strftime('%d-%m-%Y %H:%M:%S'))

def checking_posts():
	while True:
		posts = db.get_all_posts()
		check_channels()

		for post in posts:
			date = datetime.strptime(post[3].split('+')[0],'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
			diff = datetime.now(timezone.utc) - date
			print(*post[1:3])
			print('diff is ',diff.seconds//60,'min')
			
			average_dict = {'reactions_for_30_min':-2,'reations_for_1_h':-1}

			if diff.seconds in range(30*60,80*60):
				reactions = check_reactions(*post[1:3])
				print('reactions',reactions)
				if reactions == 0:
					continue
				
				if diff.seconds in range(30*60,35*60) and post[-2] == '0':
					param = 'reactions_for_30_min'
				elif diff.seconds in range(60*60,80*60) and post[-1] == '0':
					param = 'reations_for_1_h'
				else:
					continue

				print('updating ',param)
				db.update_post(reactions,*post[1:3],param)

				channel_average = db.get_specific_channel(post[1])[0]
				channel_average = int(channel_average[average_dict[param]])
				
				if channel_average == 0:
					continue
				
				precent = int((int(reactions)-channel_average)/channel_average*100)
				print(precent)
				
				if precent > 15 and int(post[4]) != 1:
					forward_message(*post[1:3],precent,average_dict[param])
					db.update_forward(*post[1:3])
		
		check_messages()
		
		sleep(1)

#app.run()
#checking_posts()
#set_time()
while True:
    try:
        checking_posts()
    except:
        traceback.print_exc()

#check_channels()
#app.run()#-719380975
