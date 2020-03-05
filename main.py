from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests
import re
import logging
import telegram
import json
from tabulate import tabulate
import imgkit
from bs4 import BeautifulSoup
import urllib.request
from PortfolioUpdate import generate_email

headers = ['Sym', 'Qty', 'Price', 'PL']    

amp = [1.1, 1.2, 1.3, 1.4]
mass = [2.1, 2.2, 2.3, 2.4]
period = [3.1, 3.2, 3.3, 3.4]
ecc = [4.1, 4.2, 4.3, 4.4]
planet = range(1, len(amp)+1)

table = zip(planet, amp, mass, period, ecc)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ------------------------------------Private Function-------------
def getSubStringBetweenMarket(s):
    pattern = "\((.*?)\)"
    substring = re.search(pattern, s).group(1)
    return substring
    
def getPrice(t):
    url = "https://sg.finance.yahoo.com/quote/{ticket}?p={ticket}".format(ticket=t)
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    price = float((soup.find('span', {'data-reactid':'14'}).string).replace(',',''))
    dailyChange = getSubStringBetweenMarket((soup.find('span', {'data-reactid':'16'}).string))
    return [price, dailyChange]

def compute(my_portfolio):
#   my_portfolio = {stock: [qty, paid,curr price, daily change, profit/loss]}
    total = 0
    total_paid = 0
    for k in my_portfolio.keys():
        price = getPrice(k)
        pl_value = (price[0] - my_portfolio[k][1]) * my_portfolio[k][0]
        total_paid += my_portfolio[k][1] * my_portfolio[k][0]
        pl = float("%.2f" % round(pl_value,2))
        total += pl
        price.append(pl)
        my_portfolio[k] = my_portfolio[k][:1] + (price)
    result = []
    for k in my_portfolio.keys():
        result.append([k] + my_portfolio[k])
    result.append(['Total',float("%.2f" % round(total_paid,2)),'','',float("%.2f" % round(total,2))])
    return(result)

# Result format:

# [['AMZN', 5, 1895.85, 1938.27, '+1.53%', 212.1],
#  ['BLK', 10, 538.505, 484.25, '+1.21%', -542.55],
#  ['TWTR', 280, 36.2, 35.11, '+0.52%', -305.2],
#  ['C', 50, 79.8, 64.56, '-0.75%', -762.0],
#  ['Total', '', 28990.3, '', '', -1397.65]]

# -------------------------------------------------------



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
    my_portfolio = {'AMZN': [5,1895.85], 'BLK': [10, 538.505],'TWTR': [280, 36.2], 'C':[50, 79.8]}
    data = compute(my_portfolio)



    bot = context.bot
    chat_id = update.effective_chat.id
    bot.send_message(chat_id=chat_id, 
                 text=(str(tabulate(data, headers=headers, floatfmt=".2f"))), 
                 parse_mode=telegram.ParseMode.HTML)
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
    my_portfolio = {'AMZN': [5,1895.85], 'BLK': [10, 538.505],'TWTR': [280, 36.2], 'C':[50, 79.8]}
    email_address = "nl.chuongthien@gmail.com"
    generate_email(my_portfolio, email_address)
    bot = context.bot
    chat_id = update.effective_chat.id
    bot.send_message(chat_id=chat_id, 
                 text=("Email Sent"), 
                 parse_mode=telegram.ParseMode.HTML)

def main():
    updater = Updater('1082087845:AAGCIiSuyrNXXtH1rM0iNdqnEYL07jXVUyY', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('me',me))
    dp.add_handler(CommandHandler('email',email))
    dp.add_handler(CommandHandler('dog',dog))
    dp.add_handler(CommandHandler('stop',shutdown))
    updater.start_polling(poll_interval = 1.0,timeout=20)
    updater.idle()

if __name__ == '__main__':
    print("Starting Bot")
    main()
    print("Exiting Bot")