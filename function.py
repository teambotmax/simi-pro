from thrift.transport.THttpClient import THttpClient
#from thrift.transport.THttpClientPool import THttpClient as THttpClientPool
from thrift.protocol.TCompactProtocol import TCompactProtocol
from BE import *
from BE.ttypes import *
import time, json, requests, threading, os, random, ast, datetime

def readJson(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def writeJson(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)
        f.close()
    return


class BE_Team:
    def __init__(self, myToken, myApp, pool=False):
        self.lineServer = "https://ga2.line.naver.jp"
        self.thisHeaders = {}
        splited = myApp.split("\t")
        self.thisHeaders["x-line-access"] = myToken
        self.thisHeaders["x-line-application"] = myApp
        self.thisHeaders["x-lal"] = "en_id"
        if splited[0] == "ANDROIDLITE":
            self.thisHeaders["user-agent"] = 'LLA/{} Mi5 {}'.format(splited[1], splited[3])
        elif splited[0] == "CHROMEOS":
            self.thisHeaders["user-agent"] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
        else:
            self.thisHeaders["user-agent"] = 'Line/{}'.format(splited[1])
        self.talk = self.openTransport("/S4")
        if pool:
            self.poll = self.openTransport("/P4", True) ## REAL POLL /P5
        self.profile = self.getProfile()
        self.serverTime = self.getServerTime()
        self.lastOp = 0
        self.messageData = {}
        self.startBot = datetime.datetime.now()
        print("[ Login ] Display Name: " + self.profile.displayName)
        print("[ Login ] Auth Token: " + self.thisHeaders["x-line-access"])
        
    def openTransport(self, endPoint, pool=False):
        if pool:
            #transport = THttpClientPool(self.lineServer + endPoint)
            transport = THttpClient(self.lineServer + endPoint)
        else:
            transport = THttpClient(self.lineServer + endPoint)
        transport.setCustomHeaders(self.thisHeaders)
        protocol = TCompactProtocol(transport)
        return BEService.Client(protocol)

    def createChat(self, name, targetUserMids=[]):
        return self.talk.createChat(CreateChatRequest(0,0,name,targetUserMids,""))

    def inviteIntoChat(self, chatMid, targetUserMids=[]):
        return self.talk.inviteIntoChat(InviteIntoChatRequest(0,chatMid,targetUserMids))

    def cancelChatInvitation(self, chatMid, targetUserMids=[]):
        return self.talk.cancelChatInvitation(CancelChatInvitationRequest(0,chatMid,targetUserMids))

    def deleteOtherFromChat(self, chatMid, targetUserMids=[]):
        return self.talk.deleteOtherFromChat(DeleteOtherFromChatRequest(0,chatMid,targetUserMids))

    def acceptChatInvitation(self, chatMid):
        return self.talk.acceptChatInvitation(AcceptChatInvitationRequest(0,chatMid))

    def acceptChatInvitationByTicket(self, chatMid, ticketId):
        return self.talk.acceptChatInvitationByTicket(AcceptChatInvitationByTicketRequest(0,chatMid,ticketId))

    def reissueChatTicket(self, chatMid):
        return self.talk.reissueChatTicket(ReissueChatTicketRequest(0,chatMid))

    def findChatByTicket(self, ticketId):
        return self.talk.findChatByTicket(FindChatByTicketRequest(ticketId))

    def getInvitationTicketUrl(self, mid):
        return self.talk.getInvitationTicketUrl(GetInvitationTicketUrlRequest(mid))

    def getChats(self, chatMids=[], withMembers=True, withInvitees=True):
        return self.talk.getChats(GetChatsRequest(chatMids,withMembers,withInvitees))

    def updateChat(self, chat, updatedAttribute):
        return self.talk.updateChat(UpdateChatRequest(0,chat,updatedAttribute))

    def sendMessage(self, to, text, contentMetadata={}, contentType=0):
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = text
        msg.contentType, msg.contentMetadata = contentType, contentMetadata
        if to not in self.messageData:
            self.messageData[to] = -1
        self.messageData[to] += 1
        return self.talk.sendMessage(self.messageData[to], msg)
    
    def sendMessageReply(self, to, text, msgId):
        msg = Message()
        msg.to, msg._from = to, self.profile.mid
        msg.text = text
        msg.contentType, msg.contentMetadata = 0, {}
        msg.relatedMessageId = msgId
        msg.messageRelationType = 3
        msg.relatedMessageServiceCode = 1
        return self.talk.sendMessage(0, msg)

    def sendMention(self, to, mid, text):
        mentiones = '{"S":"0","E":"3","M":'+json.dumps(mid)+'}'
        text_ = '@x  {}'.format(text)
        return self.sendMessage(to, text_, contentMetadata={'MENTION':'{"MENTIONEES":['+mentiones+']}'}, contentType=0)

    def getMentiones(self, msg):
        if 'MENTION' in msg.contentMetadata.keys()!= None:
            mention = ast.literal_eval(msg.contentMetadata['MENTION'])
            mentionees = mention['MENTIONEES']
            return [mention["M"] for mention in mentionees]
        else:
            return None
    
    def getServerTime(self):
        return self.talk.getServerTime()

    def getProfile(self, syncReason=3):
        return self.talk.getProfile(syncReason)

    def fetchOps(self, individualRev, globalRev=int(time.time())+1*1000000, count=5): # MUST USE CORRECT VALUE
        return self.poll.fetchOps(self.lastOp, count, globalRev, individualRev)

    def fetchOperations(self, count=100):
        return self.poll.fetchOperations(self.lastOp, count)



    
