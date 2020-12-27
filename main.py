import requests, json
from datetime import datetime, date, timedelta

def print_json(o):
	print(json.dumps(o, indent=4))

def print_title(s):
	print("--------" + s + "--------")

def load_messages(gc_id, token, from_file=False, file_name="messages"):
	if(from_file):
		msg_file = open(file_name + ".txt", "r")
		ret = json.loads(msg_file.read())
		msg_file.close()
		return ret
	else:
		req_messages = requests.get("https://api.groupme.com/v3/groups/" + gc_id + "/messages?token=" + token)
		res_messages = json.loads(req_messages.text)["response"]
		msgs = []
		for x in range(20, res_messages["count"], 20):
			print(str(int(x / res_messages["count"] * 100)) + "% done")
			msgs.extend(res_messages["messages"])
			req_messages = requests.get("https://api.groupme.com/v3/groups/" + gc_id + "/messages?token=" + token + 
				"&before_id=" + res_messages["messages"][-1]["id"])
			res_messages = json.loads(req_messages.text)["response"]


		msgs.extend(res_messages["messages"])

		msg_file = open(file_name + ".txt", "w")
		msg_file.write(json.dumps(msgs))
		msg_file.close()
		return msgs

def sort_dict(dic):
	ar = []
	for x in dic:
		ar.append((x, dic[x]))
	ar = sorted(ar, key=lambda x: x[1])[::-1]
	return ar


def sortByMostLiked(msgs, gc_json):
	return sorted(msgs, key=lambda x: len(x["favorited_by"]))

def printTopLiked(msgs, gc_json, n):
	msgs1 = sortByMostLiked(msgs, gc_json)[::-1]
	print_title("The " + str(n) + " most liked messages")
	for x in range(n):
		#print_json(msgs1[x])
		print(msgs1[x]["name"] + " said \"" + (msgs1[x]["text"] if msgs1[x]["text"] != None else "") + "\" with " 
			+ str(len(msgs1[x]["favorited_by"])) + " likes\n")

def personNumberOfMessagesDict(msgs, gc_json):
	personDict = {}
	for x in gc_json["members"]:
		personDict[x["user_id"]] = 0
	for x in msgs:
		if(x["user_id"] in personDict):
			personDict[x["user_id"]] += 1
	return personDict

def personLikesDensityDict(msgs, gc_json):
	personDict = {}
	personDict1 = {}
	for x in gc_json["members"]:
		personDict[x["user_id"]] = 0
		personDict1[x["user_id"]] = 0
	for x in msgs:
		if(x["user_id"] in personDict):
			personDict[x["user_id"]] += len(x["favorited_by"])
			personDict1[x["user_id"]] += 1
	res = {}
	for x in gc_json["members"]:
		if(personDict1[x["user_id"]]  != 0): res[x["user_id"]] = personDict[x["user_id"]] / personDict1[x["user_id"]] 
	return res

def idToNicknameDict(msgs, gc_json):
	idDict = {}
	for x in gc_json["members"]:
		idDict[x["user_id"]] = x["nickname"]
	return idDict	

def printTopMessagingPeople(msgs, gc_json, n):
	print_title("The " + str(n) + " most active members")
	personDict = personNumberOfMessagesDict(msgs, gc_json)
	idDict = idToNicknameDict(msgs, gc_json)
	ar = sort_dict(personDict)
	for x in range(n):
		print(idDict[ar[x][0]] + " with " + str(ar[x][1]) + " messages")

def printTopLikeDensity(msgs, gc_json, n):
	print_title("The " + str(n) + " most active members")
	personDict = personLikesDensityDict(msgs, gc_json)
	idDict = idToNicknameDict(msgs, gc_json)
	ar = sort_dict(personDict)
	for x in range(len(ar)):
		if("Sanjiv" in idDict[ar[x][0]]):
			print(idDict[ar[x][0]] + " with " + str(ar[x][1]) + " likes / message")
	for x in range(n):
		print(idDict[ar[x][0]] + " with " + str(ar[x][1]) + " likes / message")

def printNumberOfStalkers(msgs, gc_json):
	print_title("Number of stalkers (people who have never commented)")
	personDict = personNumberOfMessagesDict(msgs, gc_json)
	c = 0
	for x in personDict:
		if(personDict[x] == 0):
			c +=1
	print(str(c) + " (around " + str(int(c / len(personDict) * 100)) + "% of the gc)")

def wordFreqDict(msgs, gc_json):
	wordDict = {}
	c = 0
	for x in msgs:
		if(x["text"] != None):
			if(timestampToDate(x["created_at"]).weekday() == 6):
				for y in x["text"].split(" "):
					if(y.lower() in wordDict):
						wordDict[y.lower()] += 1
					else:
						wordDict[y.lower()] = 1
		c += 1
	return wordDict

def addToSet(s, fileName):
	file = open(fileName, "r")
	for x in file.read().split("\n"):
		s.add(x.split(" ")[0].lower())
	file.close()

def wordCount(wordDict, word):
	return wordDict[word] if word in wordDict else 0

def personLikesDict(msgs, gc_json):
	personDict = {}
	for x in gc_json["members"]:
		personDict[x["user_id"]] = 0
	for x in msgs:
		for y in x["favorited_by"]:
			if(y in personDict):
				personDict[y] += 1
	return personDict

def printMostGenerousPeople(msgs, gc_json, n):
	print_title("The " + str(n) + " most generous people (give out the most likes)")
	personDict = personLikesDict(msgs, gc_json)
	idDict = idToNicknameDict(msgs, gc_json)
	ar = sort_dict(personDict)
	for x in range(n):
		print(idDict[ar[x][0]] + " with " + str(ar[x][1]) + " likes")

def printTotalNumberOfMessages(msgs, gc_json):
	print_title("Total number of messages on gc")
	print(len(msgs))

def timestampToDate(ts):
	return datetime.fromtimestamp(ts).date()

def startDate(msgs, gc_json):
	return timestampToDate(gc_json["created_at"])

def dateTimeDict(msgs, gc_json):
	dateDict = {}
	for x in range((date.today() - startDate(msgs, gc_json)).days + 1):
		dateDict[startDate(msgs, gc_json) + timedelta(x)] = 0
	for x in msgs:
		dateDict[timestampToDate(x["created_at"])] += 1
	return dateDict

def printTopDays(msgs, gc_json, n):
	print_title("The " + str(n) + " days with the most messages")
	dateDict = dateTimeDict(msgs, gc_json)
	ar = sort_dict(dateDict)
	for x in range(n):
		print(str(ar[x][0]) + " with " + str(ar[x][1]) + " messages")

def printLowDays(msgs, gc_json, n):
	print_title("The " + str(n) + " days with the least messages")
	dateDict = dateTimeDict(msgs, gc_json)
	ar = sort_dict(dateDict)[::-1]
	for x in range(n):
		print(str(ar[x][0]) + " with " + str(ar[x][1]) + " messages")


from_file = True
gc_id = None
token = None
if(not from_file):

	#put auth token from groupme api in token.txt
	token_file = open("token.txt", "r")
	token = token_file.read()
	token_file.close()

	#Put your group chat name here
	gc_name = "RU Honors College ‘23"
	req_groups = requests.get("https://api.groupme.com/v3/groups?token=" + token)

	res_groups = json.loads(req_groups.text)["response"]

	gc_json = {}

	for x in res_groups:
		print(x["name"])
		if(x["name"] == gc_name):
			gc_json = x
			break

	#print_json(gc_json)

	gc_id = gc_json["id"]

#print(gc_id)

msgs = load_messages(gc_id, token, True)

n = 20

print(len(list(filter(lambda x: timestampToDate(x["created_at"]).weekday() == 6, msgs))))
printTopLikeDensity(msgs, gc_json, 100)
printNumberOfWashing(msgs, gc_json)
printTopLiked(msgs, gc_json, n)
printTopMessagingPeople(msgs, gc_json, n)
printNumberOfStalkers(msgs, gc_json)
printMostGenerousPeople(msgs, gc_json, n)
printTotalNumberOfMessages(msgs, gc_json)
printTopDays(msgs, gc_json, n)
printLowDays(msgs, gc_json, n)
