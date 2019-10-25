import threading
import json


try:
	from c.snipes import Sniper

	task = json.load(open("task.json"))
	profile=json.load(open("profile.json"))
	x=task['tasks']


	bot = Sniper(task['url'],task['productId'],task['variation'],task['size'],profile)

	while x>0:
		x-=1
		threading.Thread(target=bot.task, args=[x]).start()
except json.decoder.JSONDecodeError:
	print("you fcked up, save a valid json formatted task please")
except ModuleNotFoundError:
	print("you messed up again, please leave the snipes.py file in the c folder")
except FileNotFoundError:
	print("yeet, again. wheres the task.json/profile.json file? bruh")