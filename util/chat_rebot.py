#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

class chatRebot:
    chatbot = ChatBot(
        "chatRebot",
        storage_adapter = "chatterbot.storage.MongoDatabaseAdapter",
    )

    def __init__(self):
        self.chatbot.set_trainer(ChatterBotCorpusTrainer)
        self.chatbot.train("chatterbot.corpus.chinese")

    def getResponse(self, message=""):
        return self.chatbot.get_response(message)

if __name__ == "__main__":
    bot = chatRebot()
    while True:
        print('ta: ', bot.getResponse(input("you: ")))
