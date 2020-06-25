from function import *

savedData = readJson("data.json")
myTokens = ['main_account', 'assist1', 'assist2', 'etc...']
#TOTAL OF ACCOUNT = UPTOYOU
#FIRST LIST = MAIN YOUR ACCOUNT

myBotsMid = []
myBotsClient = {}

for n in range(len(myTokens)):
    if n == 0:
        cl= BE_Team(myToken=myTokens[n],
                    myApp="ANDROIDLITE\t2.14.0\tAndroid OS\t5.1.1",
                    pool=True)
    else:
        cl= BE_Team(myToken=myTokens[n],
                    myApp="ANDROIDLITE\t2.14.0\tAndroid OS\t5.1.1")
    myBotsMid.append(cl.profile.mid)
    myBotsClient[cl.profile.mid] = cl
    
def saveData():
    writeJson("data.json",savedData)
    
def protectQR(op):
    for client in myBotsClient:
        if client != myBotsMid[0]:
            try:
                myBotsClient[client].deleteOtherFromChat(op.param1, [op.param2])
                break
            except Exception as e:
                print("[ ERROR ] {}, {}".format(client,e))
    for client in myBotsClient:
        if client != myBotsMid[0]:
            try:
                chat = myBotsClient[client].getChats([op.param1])
                chat.chats[0].extra.groupExtra.preventedJoinByTicket = True
                myBotsClient[client].updateChat(chat.chats[0],4)
                break
            except Exception as e:
                print("[ ERROR ] {}, {}".format(client,e))
    if op.param2 not in savedData["blackList"]:
        savedData["blackList"].append(op.param2)
        saveData()

def protectInvite(op):
    for invite in op.param3.split('\x1e'):
        for client in myBotsClient:
            if client != myBotsMid[0]:
                try:
                    myBotsClient[client].cancelChatInvitation(op.param1, [invite])
                    break
                except Exception as e:
                    print("[ ERROR ] {}, {}".format(client,e))
    for client in myBotsClient:
        if client != myBotsMid[0]:
            try:
                myBotsClient[client].deleteOtherFromChat(op.param1, [op.param2])
                break
            except Exception as e:
                print("[ ERROR ] {}, {}".format(client,e))
    if op.param2 not in savedData["blackList"]:
        savedData["blackList"].append(op.param2)
        savedData["blackList"].append(op.param3)
        saveData()

def protectJoin(op):
    for client in myBotsClient:
        if client != myBotsMid[0]:
            try:
                myBotsClient[client].deleteOtherFromChat(op.param1, [op.param2])
                break
            except Exception as e:
                print("[ ERROR ] {}, {}".format(client,e))

def protectCancel(op):
    for client in myBotsClient:
        if client != myBotsMid[0]:
            try:
                myBotsClient[client].deleteOtherFromChat(op.param1, [op.param2])
                break
            except Exception as e:
                print("[ ERROR ] {}, {}".format(client,e))
    if op.param2 not in savedData["blackList"]:
        savedData["blackList"].append(op.param2)
        saveData()

def protectKick(op):
    for client in myBotsClient:
        if client != myBotsMid[0]:
            try:
                myBotsClient[client].deleteOtherFromChat(op.param1, [op.param2])
                break
            except Exception as e:
                print("[ ERROR ] {}, {}".format(client,e))
    if op.param2 in myBotsMid:
        for client in myBotsClient:
            if client != myBotsMid[0]:
                try:
                    ticket = myBotsClient[client].reissueChatTicket(op.param1).ticketId
                    chat = myBotsClient[client].getChats([op.param1])
                    chat.chats[0].extra.groupExtra.preventedJoinByTicket = True
                    myBotsClient[client].updateChat(chat.chats[0],4)
                    try:
                        myBotsClient[op.param2].acceptChatInvitationByTicket(op.param1,ticket)
                    except Exception as e:
                        print("[ ERROR ] {}, {}".format(op.param2,e))
                    chat.chats[0].extra.groupExtra.preventedJoinByTicket = False
                    myBotsClient[client].updateChat(chat.chats[0],4)
                    break
                except Exception as e:
                    print("[ ERROR ] {}, {}".format(client,e))
    if op.param2 not in savedData["blackList"]:
        savedData["blackList"].append(op.param2)
        saveData()
    
def worker(op):
    if op.type == 11 or op.type == 122:
        if savedData["protect"] and op.param2 not in myBotsMid + savedData["adminList"]:
            t = threading.Thread(target=protectQR, args=(op,))
            t.daemon = True
            t.start()
            
    if op.type == 13 or op.type == 124:        
        if savedData["protect"] and op.param2 not in myBotsMid + savedData["adminList"]:
            t = threading.Thread(target=protectInvite, args=(op,))
            t.daemon = True
            t.start()

    if op.type == 17 or op.type == 130:
        if savedData["protect"] and op.param2 not in myBotsMid + savedData["adminList"] and op.param2 in savedData["blackList"]:
            t = threading.Thread(target=protectJoin, args=(op,))
            t.daemon = True
            t.start()

    if op.type == 32 or op.type == 126:       
        if savedData["protect"] and op.param2 not in myBotsMid + savedData["adminList"]:
            t = threading.Thread(target=protectCancel, args=(op,))
            t.daemon = True
            t.start()

    if op.type == 19 or op.type == 133:
        if savedData["protect"] and op.param2 not in myBotsMid + savedData["adminList"]:
            t = threading.Thread(target=protectCancel, args=(op,))
            t.daemon = True
            t.start()

    if op.type in [25, 26]:
        msg = op.message
        text = str(msg.text)
        msg_id = msg.id
        receiver = msg.to
        msg.from_ = msg._from
        sender = msg._from
        cmd = text.lower()
        if msg.toType == 0 and sender != myBotsClient[myBotsMid[0]].profile.mid: to = sender
        else: to = receiver
        if cmd == "join" and sender in myBotsMid + savedData["adminList"]:
            ticket = myBotsClient[myBotsMid[0]].reissueChatTicket(to).ticketId
            chat = myBotsClient[myBotsMid[0]].getChats([to])
            chat.chats[0].extra.groupExtra.preventedJoinByTicket = False
            myBotsClient[myBotsMid[0]].updateChat(chat.chats[0],4)
            for client in myBotsClient:
                if client != myBotsMid[0]:
                    try:
                        myBotsClient[client].acceptChatInvitationByTicket(to,ticket)
                    except Exception as e:
                        print("[ ERROR ] {}, {}".format(client,e))
            chat.chats[0].extra.groupExtra.preventedJoinByTicket = True
            myBotsClient[myBotsMid[0]].updateChat(chat.chats[0],4)
            myBotsClient[myBotsMid[0]].sendMessage(to,'ok')
            
        if cmd == "protect on" and sender in myBotsMid + savedData["adminList"]:
            savedData["protect"] = True
            saveData()
            myBotsClient[myBotsMid[0]].sendMessage(to,'ok')

        if cmd == "protect off" and sender in myBotsMid + savedData["adminList"]:
            savedData["protect"] = False
            saveData()
            myBotsClient[myBotsMid[0]].sendMessage(to,'ok')

        if cmd.startswith('addadmin') and sender in myBotsMid:
            admins = myBotsClient[myBotsMid[0]].getMentiones(msg)
            for admin in admins:
                if admin not in savedData["adminList"]:
                    savedData["adminList"].append(admin)
            saveData()
            myBotsClient[myBotsMid[0]].sendMessage(to,'ok')

        if cmd.startswith('deladmin') and sender in myBotsMid:
            admins = myBotsClient[myBotsMid[0]].getMentiones(msg)
            for admin in admins:
                if admin in savedData["adminList"]:
                    savedData["adminList"].remove(admin)
            saveData()
            myBotsClient[myBotsMid[0]].sendMessage(to,'ok')
            
while True:
    try:
    #ops = myBotsClient[myBotsMid[0]].fetchOps(123) #YOU MUST USE CORRECT VALUE :)
        ops = myBotsClient[myBotsMid[0]].fetchOperations()
        print(ops)
        for op in ops:
            if op.revision > myBotsClient[myBotsMid[0]].lastOp:
                try:
                    worker(op)
                except Exception as e:
                    print(e)
                myBotsClient[myBotsMid[0]].lastOp = max(op.revision, myBotsClient[myBotsMid[0]].lastOp)
    except:
        pass
