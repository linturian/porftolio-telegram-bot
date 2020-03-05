from bs4 import BeautifulSoup
import urllib.request
import re
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tabulate import tabulate
import datetime


def sendEmail(row_body, email_address):
    sender_email = "theebrokestudent@gmail.com"
    receiver_email = email_address
    password = "Asdfghjkl1!@"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Portfolio_Daily_Update"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    # text = """\
    # PORFOLIO:
    # {table}

    # """


    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <style type="text/css">
          table {
            background: white;
            border-radius:3px;
            border-collapse: collapse;
            height: auto;
            max-width: 900px;
            padding:5px;
            width: 100%;
            animation: float 5s infinite;
          }
          th {
            color:black;
            background:white;
            border-bottom: 4px solid #9ea7af;
            font-size:14px;
            font-weight: 600;
            padding:10px;
            text-align:center;
            vertical-align:middle;
          }
          tr {
            border-top: 1px solid #C1C3D1;
            border-bottom: 1px solid #C1C3D1;
            border-left: 1px solid #C1C3D1;
            color:#666B85;
            font-size:16px;
            font-weight:normal;
          }
          tr:hover td {
            background:#4E5066;
            color:#FFFFFF;
            border-top: 1px solid #22262e;
          }
          td {
            background:#FFFFFF;
            padding:10px;
            text-align:left;
            vertical-align:middle;
            font-weight:300;
            font-size:13px;
            border-right: 1px solid #C1C3D1;
          }
        </style>
      </head>
      <body>
        Hi there,<br> <br>
        Daily Portfolio Report<br><br>
        <table>
          <thead>
            <tr style="border: 1px solid #1b1e24;">
              <th>Stock</th>
              <th>Q.ty</th>
              <th>Paid</th>
              <th>Curr. Price</th>
              <th>Daily Chg</th>
              <th>Profit/Loss</th>
            </tr>
          </thead>
          <tbody>
          """

#     row = """
#             <tr>
#               <td>AMZN</td>
#               <td>100</td>
#               <td>3</td>
#               <td>4</td>
#               <td>5</td>
#               <td>6</td>
#             </tr>
#         """

    end = """
          </tbody>
        </table>
        <br>
        <br>
        Thank you!
      </body>
    </html>
    """


    # text = text.format(table=tabulate(data))

    # Turn these into plain/html MIMEText objects
    # part1 = MIMEText(text, "plain")
    part2 = MIMEText(html+row_body+end, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    # message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

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
        my_portfolio[k] = my_portfolio[k] + (price)
    result = []
    for k in my_portfolio.keys():
        result.append([k] + my_portfolio[k])
    result.append(['Total', '',float("%.2f" % round(total_paid,2)),'','',float("%.2f" % round(total,2))])
    return(result)

def generateRow(data):
    row = """
        <tr>
          <td>{ticket}</td>
          <td>{Qty}</td>
          <td>{Paid}</td>
          <td>{CurrPrice}</td>
          <td>{DailyChg}</td>
          <td>{pl}</td>
        </tr>
    """
    list_of_row = ''
    for r in data:
        list_of_row += row.format(ticket = r[0], Qty=r[1], Paid= r[2], CurrPrice = r[3], DailyChg = r[4], pl = r[5])
    
    return(list_of_row)

def generate_email(my_portfolio, email_address):
    data = compute(my_portfolio)
    row_body = generateRow(data)
    sendEmail(row_body, email_address)

    
# def main():
#     my_portfolio = {'AMZN': [5,1895.85], 'BLK': [10, 538.505],'TWTR': [280, 36.2], 'C':[50, 79.8]}
#     data = compute(my_portfolio)
#     row_body = generateRow(data)
#     sendEmail(row_body)

# while True:
#     now = datetime.datetime.now()
#     if now.hour == 10 and now.minute == 0:
#         main()
