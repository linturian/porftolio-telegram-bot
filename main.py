from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests
import re
import logging
import telegram
import json
from tabulate import tabulate
import imgkit

headers = ['pln', 'amp', 'mass', 'prd', 'ecc']    

amp = [1.1, 1.2, 1.3, 1.4]
mass = [2.1, 2.2, 2.3, 2.4]
period = [3.1, 3.2, 3.3, 3.4]
ecc = [4.1, 4.2, 4.3, 4.4]
planet = range(1, len(amp)+1)

table = zip(planet, amp, mass, period, ecc)


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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


def bop(update, context):
    bot = context.bot
    chat_id = update.effective_chat.id
    bot.send_message(chat_id=chat_id, 
                 text=(str(tabulate(table, headers=headers, floatfmt=".2f")).replace('-','@')), 
                 parse_mode=telegram.ParseMode.HTML)
    text="""
        <html>
          <head>
            <meta name="imgkit-format" content="png"/>
            <meta name="imgkit-orientation" content="Landscape"/>
          </head>
          Hello World!
          </html>
        """
    print("saving to image")
    img = imgkit.from_string(text, False)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=img)


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
    

def main():
    updater = Updater('1082087845:AAGCIiSuyrNXXtH1rM0iNdqnEYL07jXVUyY', use_context=True)
    dp = updater.dispatcher
    print("Iam here")
    dp.add_handler(CommandHandler('bop',bop))
    dp.add_handler(CommandHandler('dog',dog))
    dp.add_handler(CommandHandler('stop',shutdown))
    print("Start polling")
    updater.start_polling(poll_interval = 1.0,timeout=20)
    updater.idle()
    print("afterilde")

if __name__ == '__main__':
    print("Starting Bot")
    main()
    print("Exiting Bot")