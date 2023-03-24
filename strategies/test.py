from strategies.strategybase import Strategy


"""
Takes the data from the bot as input, runs our strategy logic. 
This should call back to bot to place/cancel/update orders.
"""
class test(Strategy):
    def __init__(self, config):
        super().__init__(config)


    def process_data(self, data):
        # Implement your strategy logic here
        print (data)
        pass