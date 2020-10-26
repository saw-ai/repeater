# check if I already working with newest version
import os
my_pid = os.getpid()

from subprocess import check_output
try:
    pids = check_output("ps aux | grep 'python3 repeater.py' | grep -v grep | awk '{print $2}'", shell=True).decode().split()
    pid = None
    for pid_ in pids:
        if pid_ != my_pid:
            pid = pid_
            break
except:
    pid = None

hash = check_output("md5sum repeater.py", shell=True).decode().split()[0]
try:
    matches = open('hash.md5').read().strip() == hash
except:
    matches = False

if pid and matches:
    exit()

if pid:
    check_output(f"kill -9 {pid}", shell=True)

with open("hash.md5", "w") as f:
    f.write(hash)


# STARTING ...

import telebot
from telebot import types
import json
import random
import numpy as np
import pandas as pd

bot = telebot.TeleBot('1307955102:AAFjWxksNaeQNpna8kGMcRucCxwLz2GfYDE')

@bot.message_handler(commands=['start'])
def start_message(message):
  def options():
    bot.send_message(message.chat.id, "/word - Добавить слово\n/test - Угадай слово\n/freq - Test frequent words\n/list - Список слов\n/delete - Удалить слово")
  options()


d = dict()
d['mode'] = 'waiting for a word'



def load():
    try:
        v[0] = json.load(open('vocab.json'))
    except:
        v[0] = dict()
        v[0]['_all'] = 0
        v[0]['_correct'] = 0

def dump():
    json.dump(v[0], open('vocab.json', 'w'))


v = dict()
load()



def vsize():
    return len(v[0]) - 2;



def how_many(x):
    s = ""
    if x % 10 == 0 or (x > 10 and x < 20):
        s = "слов"
    elif x % 10 == 1:
        s = "слово"
    elif x % 10 == 2 or x % 10 == 3 or x % 10 == 4:
        s = "слова"
    else:
        s = "слов"
    
    return "{} {}".format(x, s)




@bot.message_handler(content_types=['text'])
def send_text(message):

  def options():
    bot.send_message(message.chat.id, "/word - Добавить слово\n/freq - Test frequent words\n/test - Угадай слово\n/list - Список слов\n/delete - Удалить слово")
  def send(text):
    bot.send_message(message.chat.id, text)

  try:
    if message.text == 'delete_all_words':
        v[0] = {'_all' : 0, '_correct' : 0} 


    elif message.text == '/test':
        if vsize() < 4:
            bot.send_message(message.chat.id, "Для теста нужно хотя бы 4 слова. Сейчас у тебя только {}. Набери /word, чтобы добавить слово".format(vsize()))
            d['mode'] = 'waiting for a word'
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            cache = json.load(open('cache.json'))
            if 'words' in cache:
                words = cache['words']
            else:
                words = random.sample([x for x in v[0] if not x.startswith('_')], 4)
                with open('cache.json', 'w') as f:
                    json.dump({'words' : words}, f)

            word = words[0]
            d['question'] = word
            random.shuffle(words)

            buttons = [types.KeyboardButton(v[0][w]) for w in words]
            for button in buttons:
                markup.add(button)
            bot.send_message(message.chat.id, word + "?", reply_markup = markup)
            d['mode'] = 'waiting for the answer'
            d['correct'] = v[0][word]

    elif message.text == '/freq':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        df = pd.read_csv('freq.csv').set_index('word')
        words = list(np.random.choice(df[df.status == 0].head(500).index, 4, replace=False)) + ['ALLRIGHT']

        for word in words:
            markup.add(word)
        bot.send_message(message.chat.id, 'asking', reply_markup = markup)

        d['mode'] = 'waiting for the answer'
        d['candidates'] = words[:4]


    elif message.text == '/word':
        d['mode'] = 'waiting for a word'
        bot.send_message(message.chat.id, "Новое слово")

    elif message.text == '/list':

        df = pd.read_csv('freq.csv').set_index('word')

        amount = len(df)
        known = len(df[df.status == 1])
        unknown = len(df[df.status == 2])

        send(f'all: {amount}, known={known}, unknown={unknown}')

    elif message.text == '/delete':
        d['mode'] = 'waiting for deletion'
        bot.send_message(message.chat.id, "Какое слово удалить?")
        
    elif d['mode'] == 'waiting for deletion':
        if message.text not in v[0]:
            bot.send_message(message.chat.id, "Нет такого слова, еще разок")
        else:
            del v[0][message.text]
            send("Удалено! Теперь у заи {}".format(how_many(vsize())))
            d['mode'] = 'waiting for a word'
            options()

    elif d['mode'] == 'waiting for a word':
        if not ( 'a' <= message.text[0] and message.text[0] <= 'z'):
            send("English word, please!")
        else:
            d['word'] = message.text
            send("Теперь перевод")
            d['mode'] = 'waiting for translation'

    elif d['mode'] == 'waiting for translation':
        v[0][d['word']] = message.text
        dump()
        send("Теперь у заечки {}".format(how_many(vsize())))
        d['mode'] = 'waiting for a word'

    elif d['mode'] == 'waiting for the answer':


        if message.text == 'ALLRIGHT':
            df = pd.read_csv('freq.csv').set_index('word')
            for word in d['candidates']:
                df.at[word, 'status'] = 1
            df.to_csv('freq.csv') 
        else:
            df = pd.read_csv('freq.csv').set_index('word')
            df.at[message.text, 'status'] = 2
            df.to_csv('freq.csv')

            send(f'The word "{message.text}" is marked as unknown')

        d['mode'] = 'waiting for a word'

    dump()

    print("message.text = ", message.text)
    print(v[0])
    print(d)
  except KeyboardInterrupt:
      raise
  except:
      raise
      send("Ошибочка вышла...")


@bot.message_handler(commands=['switch'])
def switch(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons = [types.KeyboardButton(text=str(random.randint(0, 100))) for i in range(4)]
    for button in buttons:
        markup.add(button)
    bot.send_message(message.chat.id, "Выбрать чат", reply_markup = markup)




#bot.polling()


while True:
    try:
        bot.polling()
    except KeyboardInterrupt:
        raise
    except:
        pass
