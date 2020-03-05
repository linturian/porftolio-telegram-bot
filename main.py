import logging

import pandas as pd
import requests
import telegram
from tabulate import tabulate
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler

from PortfolioUpdate import generate_email, compute
from User import User

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# ---------------Global Variable-------------------------
user_dict = {}

s = pd.read_csv('./constituents_csv.csv')['Symbol']
s.unique()
symbol_set = set(s)


# ------------------------------------Private Function-------------
# Result format:

# [['AMZN', 5, 1895.85, 1938.27, '+1.53%', 212.1],
#  ['BLK', 10, 538.505, 484.25, '+1.21%', -542.55],
#  ['TWTR', 280, 36.2, 35.11, '+0.52%', -305.2],
#  ['C', 50, 79.8, 64.56, '-0.75%', -762.0],
#  ['Total', '', 28990.3, '', '', -1397.65]]
def log(message):
    print("********************************")
    print(message)
    print("********************************")


def validateStock(bot, chat_id, ticker):
    if ticker not in symbol_set:
        bot.send_message(chat_id=chat_id, text="Your stock is currently not supported!")
        return False
    return True


def getUser(chat_id):
    user = user_dict.setdefault(chat_id, User(chat_id))
    return user


# -------------------------------------------------------
# INPUT VALIDATION


def add(update, context):
    chat_id = update.effective_chat.id
    user = getUser(chat_id)
    bot = context.bot
    stock_symbol = context.args[0].upper()
    qty = float(context.args[1])
    price = float(context.args[2])
    if validateStock(bot, chat_id, stock_symbol):
        stock = [stock_symbol, qty, price]
        user.addStock(stock)
        bot.send_message(chat_id=chat_id, text="Added {} || Qty: {} || Price: {}".format(stock[0], stock[1], stock[2]))


def remove(update, context):
    chat_id = update.effective_chat.id
    user = getUser(chat_id)
    stock_symbol = context.args[0].upper()
    msg = "Remove {} from your portfolio".format(stock_symbol)
    try:
        del user.my_portfolio[stock_symbol]
    except KeyError:
        msg = "The stock is not in your portfolio, please check again!"

    context.bot.send_message(chat_id=chat_id,
                             text=msg)
    context.bot.send_message(chat_id=chat_id,
                             text="Here is your updated portfolio: /n {}".format(str(user.my_portfolio)))


def my_portfolio(update, context):
    chat_id = update.effective_chat.id
    user = getUser(chat_id)
    headers = ['Sym', 'Qty', 'Price']

    context.bot.send_message(chat_id=chat_id,
                             text=str(user.my_portfolio))


def clear_all_stock(update, context):
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
                             text="Hello, Welcome to your personal Portfolio Assistant!")


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def dog(update, context):
    url = get_url()
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=url)


def profit_loss(update, context):
    bot = context.bot
    chat_id = update.effective_chat.id

    my_portfolio = user_dict[chat_id].my_portfolio
    data = compute(my_portfolio)

    headers = ['Sym', 'Qty', 'Paid', 'Price', 'PL']

    bot.send_message(chat_id=chat_id,
                     text=(str(tabulate(data, headers=headers, floatfmt=".2f"))))


def email(update, context):
    bot = context.bot
    chat_id = update.effective_chat.id
    # my_portfolio = {'AMZN': [5,1895.85], 'BLK': [10, 538.505],'TWTR': [280, 36.2], 'C':[50, 79.8]}
    user = getUser(chat_id)
    email_address = context.args[0]
    generate_email(user.my_portfolio, email_address)

    bot.send_message(chat_id=chat_id,
                     text="Email Sent",
                     parse_mode=telegram.ParseMode.HTML)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater('1082087845:AAGCIiSuyrNXXtH1rM0iNdqnEYL07jXVUyY', use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('me', my_portfolio))
    dp.add_handler(CommandHandler('add', add))
    dp.add_handler(CommandHandler('remove', remove))
    dp.add_handler(CommandHandler('profit', profit_loss))
    dp.add_handler(CommandHandler('clear_all_stock', clear_all_stock))
    dp.add_handler(CommandHandler('email', email))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('dog', dog))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print("Starting Bot")
    main()
    print("Exiting Bot")
