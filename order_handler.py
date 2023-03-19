class Order:
    def __init__(self, symbol, quantity, order_type, side):
        self.symbol = symbol
        self.quantity = quantity
        self.order_type = order_type
        self.side = side
        self.status = 'open'
        self.filled_quantity = 0
        self.filled_price = 0

    def is_open(self):
        return self.status == 'open'

    def is_filled(self):
        return self.status == 'filled'
