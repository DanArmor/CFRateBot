import telebot

import json
import requests
import sys
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#YOU CAN CHANGE THAT VALUE
Border_of_low_rating = 1100 #All problems under that value are defined as low rating problems
##########################

def getInfoByResponse(response):
    try:
        response = requests.get(response) 
    except:
        sys.stderr.write("---------------------------------\n")
        sys.stderr.write("ERROR:\n")
        sys.stderr.write("Something went wrong when we tried to get data from codeforces! No responce!\n")
        sys.stderr.write("---------------------------------\n")
        return
    data = json.loads(response.text)
    return data

def checkData(data):
    if data["status"] != "OK":
        try:
            sys.stderr.write("---------------------------------\n")
            sys.stderr.write("ERROR:\n")
            sys.stderr.write("Something went wrong when we tried to get data from codeforces! The end data is wrong!\n")
            sys.stderr.write("Codeforces comment about error is:", data["comment"],"\n")
            sys.stderr.write("---------------------------------\n")
            return
        except:
            sys.stderr.write("Something went wrong with getting codeforces comment\n")
            sys.stderr.write("---------------------------------\n")
            return

def makeFancy(message, first, second):
    numberForPerc = first / second
    percentage = "{:.1%}".format(numberForPerc)
    output = "*" + message + "*" + str(first) + " = " + str(first) + "/" + str(second) + " (" + str(percentage) + ")\n"
    return output

def makeFancyAdv(message, first, second, third):
    numberForPerc = second / third
    percentage = "{:.1%}".format(numberForPerc)

    first = str(first)
    index = first.find("*")
    if(index != -1):
        first = first[:index] + "\\" + first[index:]

    output = "*" + message + "*" + str(first) + " = " + str(second) + "/" + str(third) + " (" + str(percentage) + ")\n"
    return output
    
admins = []
tagsAll = {}
ratingsAll = {}
totalLowFromAll = 0
totalHighFromAll = 0

emojiMap = {800: "⚪️", 900: "⚪️", 1000: "⚪️", 1100: "⚪️", 1200: "🟢", 1300:"🟢", 1400:"🔵", 1500: "🔵",
            1600: "🟣", 1700: "🟣", 1800: "🟣", 1900: "🟪", 2000: "🟪", 2100: "🟡", 2200: "🟡", 2300: "🟠",
            2400: "🔴", 2500: "🔴", 2600: "🔻", 2700: "🔻", 2800: "🔻", 2900: "🔻", 3000: "🔺", 3100: "🔺",
            3200: "🔺", 3300: "🔺", 3400: "🔺", 3500: "🔺"}


def Process_handle(handle):

    data = getInfoByResponse("https://codeforces.com/api/user.status?handle=" + handle)

    names = {}
    high_rates = {}
    low_rates = {}

    tags = {}

    total = 0;
    total_low = 0
    total_high = 0

    checkData(data)

    for t in data["result"]:

        if(t["verdict"] != "OK"):
            continue
        
        try:
            rate = t["problem"]["rating"]
        except KeyError:
            continue
        
        key = str(t["problem"]["contestId"]) + t["problem"]["index"]

        if key in names:
            continue
        else:
            names[key] = 1

        for tag in t["problem"]["tags"]:
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1

        high_rate = True
        if(rate < Border_of_low_rating):
            high_rate = False

        if(high_rate):
            total_high += 1
            if rate in high_rates:
                high_rates[rate] += 1
            else:
                high_rates[rate] = 1
        else:
            total_low += 1
            if rate in low_rates:
                low_rates[rate] += 1
            else:
                low_rates[rate] = 1

        total += 1

    output = "*Rating < " + str(Border_of_low_rating) + " is low rate*\n"
    output += "Problems without rating are not counted\n\nInformation about *" + str(handle) + "*\n"

    numberForTotal = numberForPerc = total / (totalLowFromAll + totalHighFromAll)
    percentageTotal = "{:.1%}".format(numberForTotal)
    
    output += makeFancy("*Total:* ", total, totalLowFromAll + totalHighFromAll)
    output += "--------------------\n"

    numberForTotal = numberForPerc = total_high / totalHighFromAll
    percentageTotal = "{:.1%}".format(numberForTotal)

    output += makeFancy("*Total high ratings:* ", total_high, totalHighFromAll)

    for k, v in sorted(ratingsAll.items(), reverse=True):
        try:
            solved = high_rates[k]
        except:
            solved = 0
        if(solved == 0):
            try:
                solved = low_rates[k]
            except:
                solved = 0
        output += makeFancyAdv(emojiMap[k] + " Rating: ", k, solved, ratingsAll[k])

    output += "--------------------\n"
    
    numberForTotal = numberForPerc = total_low / totalLowFromAll
    percentageTotal = "{:.1%}".format(numberForTotal)
    output += makeFancy("*Total low ratings:* ", total_low, totalLowFromAll)
    output += "--------------------\n\n"

    output += "*By tags:*\n"
    for k, v in sorted(tagsAll.items(), reverse=True):
        tagSolved = 0
        try:
            tagSolved = tags[k]
        except:
            tagSolved = 0
        output += makeFancyAdv("▶️  ", k, tagSolved, tagsAll[k])

    return output

# Token
ftoken = open("token.txt")
bot = telebot.TeleBot(ftoken.readline())
ftoken.close()

#Обработка основной команды rate - сбор и отправка данных пользователя
@bot.message_handler(commands=['rate'])
def rateMessage(message):
    breakedMessage = message.text.split()
    if(len(breakedMessage) == 1):
        print("No handle! From user : " + str(message.from_user.id))
        bot.send_message(message.from_user.id, "Ошибка при введении хэндла!")
    else:
        handle = breakedMessage[1]
        print("Handle, that was inputed by " + str(message.from_user.id) + " : " + handle)
        answer = Process_handle(handle)
        bot.send_message(message.from_user.id, answer, parse_mode="markdown")

#Возможность 
@bot.message_handler(content_types='text')
def adminMessage(message):
    if str(message.from_user.id) in admins:
        checkForCommand(message)

def checkForCommand(message):
    command = message.text
    if command == "update":
        updateDataCF()
    elif command == "refreshAdmin":
        loadWhitelist()
    elif command == "help":
        answer = "Список администраторских команд\n"
        answer += "update : обновление базы заданий CF\n"
        answer += "refreshAdmin : обновление списка админов" 
        bot.send_message(message.from_user.id, answer)
        

def updateDataCF():
    global totalLowFromAll, totalHighFromAll
    tagsAll.clear()
    ratingsAll.clear()
    totalLowFromAll = 0
    totalHighFromAll =0

    print("Парсим банк задач. . .")
    data = getInfoByResponse("https://codeforces.com/api/problemset.problems")

    checkData(data)

    print("Обрабатываем. . .")
    for t in data["result"]["problems"]:
        try:
            rate = t["rating"]
            for tag in t["tags"]:
                if tag in tagsAll:
                    tagsAll[tag] += 1
                else:
                    tagsAll[tag] = 1
            if t["rating"] in ratingsAll:
                ratingsAll[t["rating"]] += 1
            else:
                ratingsAll[t["rating"]] = 1
        except:
            pass
    for k, v in sorted(ratingsAll.items(), reverse=True):
        if(int(k) < Border_of_low_rating):
            totalLowFromAll += v
        else:
            totalHighFromAll += v
    print(bcolors.OKGREEN + "Начат прием запросов. . .", bcolors.ENDC)

def loadWhitelist():
    global admins
    print("Загружаем ID админов. . .")
    f = open("whitelist.txt", "r")
    admins = f.readlines()
    print(bcolors.OKGREEN + "ID админов загружены. . .", bcolors.ENDC)
    f.close()

if(__name__ == "__main__"):
    print(bcolors.OKGREEN + "Бот начал работу. . .", bcolors.ENDC)
    loadWhitelist()
    updateDataCF()
    bot.polling(none_stop=True, interval=0)