class User:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.name = ''
        self.my_portfolio = {}

    def __str__(self):
     return "{}: {}\n".format(self.chat_id, self.my_portfolio)


     # Stock {'Amzn': [5, 10]}
    def addStock(self, stock):
	    if stock[0] in self.my_portfolio:
	        past_stock = self.my_portfolio[stock[0]]
	        past_qty = past_stock[0]
	        past_price = past_stock[1]

	        new_stock = stock[1:]
	        new_qty = float(new_stock[0])
	        new_price = float(new_stock[1])

	        total_share = past_qty + new_qty
	        avg = (past_price * past_qty + new_qty * new_price) / total_share
	        self.my_portfolio[stock[0]] = [total_share, avg]

	    else:
	        new_qty = float(stock[1])
	        new_price = float(stock[2])
	        self.my_portfolio[stock[0]] = [new_qty, new_price]