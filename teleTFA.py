# needed from pip : python-telegram-bot and onetimepass

import os.path
from telegram.ext import Updater
import telegram
import sys
import pickle
import onetimepass as otp
deleteonclick=False;
if not os.path.isfile('data') :
	userdata={'data':{}, 'secretkeys':{}}
	print("You currently have no bot setup, Time to setup a bot!")
	print("Once your bot is setup via @botmaster, paste the API token here!")
	userdata['data']['token']=input()
	print("Next we will need a password, that you can use to connect your telegram account to teleTFA, please use at least 10 random characters, you will only need to type this once in telegram")
	userdata['data']['password']=input()
	updater = Updater(token=userdata['data']['token'])
	dispatcher = updater.dispatcher
	print("Start a conversation with your bot and follow the instructions. If you have already started a conversation, please type the password")
	def start(bot, update):
		bot.sendMessage(chat_id=update.message.chat_id, text="In order to connect, please send the password you set previously to this chat. If you have already done so, everything should work.")
	dispatcher.addTelegramCommandHandler('start', start)
	def password(bot, update):
		if userdata['data']['password']==update.message.text:
			userdata['data']['user']=update.message.from_user.id
			bot.sendMessage(chat_id=update.message.chat_id, text="User "+update.message.from_user.first_name+" "+update.message.from_user.last_name+" Has been added successfully")
			print("Do you wish to save these settings ? y/n")
			answer = input()
			if answer=='y':
				try:
					pickle.dump( userdata, open( "data", "wb+" ) )
				except:
					print("something went wrong, userdata could not be stored tofile")
					updater.stop()
				updater.stop()
				#forced to quit with sys exit because the script outright refuses to stop
				sys.exit("Done")
		else:
			bot.sendMessage(chat_id=update.message.chat_id, text="Incorrect Password")
	dispatcher.addTelegramMessageHandler(password)
	updater.start_polling()
else:
	file=open( "data", "rb" )
	userdata = pickle.load( file )
	file.close()
	print(userdata)
	updater = Updater(token=userdata['data']['token'])
	dispatcher = updater.dispatcher
	def list(bot, update):
		custom_keyboard = []
		for account in userdata['secretkeys']:
			custom_keyboard.append([account])
		try:
			print(custom_keyboard)
			reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
			bot.sendMessage(chat_id=update.message.chat_id, text="Here are your Accounts :", reply_markup=reply_markup)
		except:
			print("Oh Dear")
	
	def add(bot, update, args):
		userdata['secretkeys'][args[0]]=args[1]
		pickle.dump( userdata, open( "data", "wb+" ) )
		
	def remove(bot, update, args):
		global deleteonclick
		deleteonclick=True;
		bot.sendMessage(chat_id=update.message.chat_id, text="Select an Account to remove")
		list(bot, update)
		
	def handlechat(bot, update, args):
		global deleteonclick
		if deleteonclick:
			try:
				del userdata['secretkeys'][update.message.text]
				deleteonclick=False;
				list(bot, update)
			except:
				print("Key doesn't exist.")
		else:
			reply=otp.get_totp(userdata['secretkeys'][update.message.text])
			bot.sendMessage(chat_id=update.message.chat_id, text=reply)
		
	dispatcher.addTelegramMessageHandler(handlechat)
	dispatcher.addTelegramCommandHandler('list', list)
	dispatcher.addTelegramCommandHandler('add', add)
	dispatcher.addTelegramCommandHandler('remove', remove)
	updater.start_polling()


