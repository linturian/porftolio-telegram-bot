from telegram.ext import Updater, InlineQueryHandler, CommandHandler, ConversationHandler, MessageHandler, Filters
import requests
import re
import logging
import telegram
import json
from tabulate import tabulate
import imgkit
from bs4 import BeautifulSoup
import urllib.request
from PortfolioUpdate import generate_email, getPrice, compute
from User import User
from telegram import ReplyKeyboardMarkup


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# ---------------Global Variable-------------------------
user_dict = {}

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Age', 'Favourite colour'],
                  ['Number of siblings', 'Something else...'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


# ------------------------------------Private Function-------------
# Result format:

# [['AMZN', 5, 1895.85, 1938.27, '+1.53%', 212.1],
#  ['BLK', 10, 538.505, 484.25, '+1.21%', -542.55],
#  ['TWTR', 280, 36.2, 35.11, '+0.52%', -305.2],
#  ['C', 50, 79.8, 64.56, '-0.75%', -762.0],
#  ['Total', '', 28990.3, '', '', -1397.65]]

# -------------------------------------------------------

def log(message):
    print("********************************")
    print(message)
    print("********************************")

def getUser(chat_id):
    user = user_dict.setdefault(chat_id, User(chat_id))
    log(user_dict)
    return user

def add(update, context):
    text_caps = ' '.join(context.args).upper()
    chat_id = update.effective_chat.id
    user = getUser(chat_id)
    stock = [context.args[0], context.args[1], context.args[2]]
    user.addStock(stock)

    context.bot.send_message(chat_id=chat_id, text="Added {} - Qty: {} - Price: {}".format(stock[0], stock[1], stock[2]))

def my_stock(update, context):
    chat_id = update.effective_chat.id
    user = getUser(chat_id)
    headers = ['Sym', 'Qty', 'Price']    

    context.bot.send_message(chat_id=chat_id, 
                 text=str(user.my_portfolio))

def clear_stock(update, context):
    chat_id = update.effective_chat.id
    user = getUser(chat_id)
    user.my_portfolio = {}
    context.bot.send_message(chat_id=chat_id, 
                text="Cleared all stocks")

    context.bot.send_message(chat_id=chat_id, 
                text=str(user.my_portfolio))


def start(update, context):
    chat_id = update.effective_chat.id
    user = getUser(chat_id)
    context.bot.send_message(chat_id,
                text="Hello to your personal Portfolio Assistant!")
    # update.message.reply_text(
    #     "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
    #     "Why don't you tell me something about yourself?",
    #     reply_markup=markup)

    # return CHOOSING


def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "{} You can tell me more, or change your opinion"
                              " on something.".format(facts_to_str(user_data)),
                              reply_markup=markup)

    return CHOOSING

def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text
    update.message.reply_text(
        'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

    return TYPING_REPLY

def custom_choice(update, context):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "{}"
                              "Until next time!".format(facts_to_str(user_data)))

    user_data.clear()
    return ConversationHandler.END


def shutdown():
    updater.stop()
    updater.is_idle = False

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()    
    url = contents['url']
    return url

def dog(update, context):
    url = get_url()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=url)


def me(update, context):


    bot = context.bot
    chat_id = update.effective_chat.id

    my_portfolio = user_dict[chat_id].my_portfolio
    data = compute(my_portfolio)

    headers = ['Sym', 'Qty', 'Paid', 'Price', 'PL']    

    bot.send_message(chat_id=chat_id, 
                 text=(str(tabulate(data, headers=headers, floatfmt=".2f"))))
    # text="""
    #     <html>
    #       <head>
    #         <meta name="imgkit-format" content="png"/>
    #         <meta name="imgkit-orientation" content="Landscape"/>
    #       </head>
    #       Hello World!
    #       </html>
    #     """
    # print("saving to image")
    # img = imgkit.from_string(text, False)
    # context.bot.send_photo(chat_id=update.effective_chat.id, photo=img)


    # bot.send_message(chat_id=chat_id, 
    #              text='''<html><body><table>
    #                     <tbody>
    #                         <tr>
    #                           <td>AMZN</td>
    #                           <td>100</td>
    #                           <td>3</td>
    #                           <td>4</td>
    #                           <td>5</td>
    #                           <td>6</td>
    #                         </tr>
    #                     </tbody>
    #              </table></body></html>''', 
    #              parse_mode=telegram.ParseMode.HTML)

def email(update, context):

    bot = context.bot
    chat_id = update.effective_chat.id
    # my_portfolio = {'AMZN': [5,1895.85], 'BLK': [10, 538.505],'TWTR': [280, 36.2], 'C':[50, 79.8]}
    user = getUser(chat_id)
    email_address = context.args[0]
    generate_email(user.my_portfolio, email_address)

    bot.send_message(chat_id=chat_id, 
                 text=("Email Sent"), 
                 parse_mode=telegram.ParseMode.HTML)

def main():
    updater = Updater('1082087845:AAGCIiSuyrNXXtH1rM0iNdqnEYL07jXVUyY', use_context=True)
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Age|Favourite colour|Number of siblings)$'),
                                      regular_choice),
                       MessageHandler(Filters.regex('^Something else...$'),
                                      custom_choice)
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice)
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )


    dp.add_handler(CommandHandler('me',me))
    dp.add_handler(CommandHandler('my_stock',my_stock))
    dp.add_handler(CommandHandler('clear_stock',clear_stock))
    dp.add_handler(CommandHandler('email',email))
    dp.add_handler(CommandHandler('add',add))
    dp.add_handler(CommandHandler('dog',dog))
    dp.add_handler(CommandHandler('stop',shutdown))
    updater.start_polling(poll_interval = 1.0,timeout=20)
    updater.idle()

if __name__ == '__main__':
    print("Starting Bot")
    main()  
    print("Exiting Bot")