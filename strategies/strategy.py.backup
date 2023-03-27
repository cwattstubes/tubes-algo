class Strategy:
    """
    Base class for trading strategies
    """

    def __init__(self):
        pass

    def process_data(self, data, broker, orders):
        """
        Process incoming data and place orders using the given broker and orders list
        """
        raise NotImplementedError


class MovingAverageStrategy(Strategy):
    """
    Simple moving average strategy
    """

    def __init__(self, window_size):
        super().__init__()
        self.window_size = window_size

    def process_data(self, data, broker, orders):
        # Calculate moving average
        if len(data) < self.window_size:
            return
        prices = [bar['close'] for bar in data[-self.window_size:]]
        ma = sum(prices) / len(prices)

        # Check if we should buy or sell
        if data[-1]['close'] > ma:
            # Buy
            if not any(order.symbol == data[-1]['symbol'] and order.side == 'buy' for order in orders):
                order = Order(symbol=data[-1]['symbol'], qty=100, side='buy', type='market')
                orders.append(order)
                broker.place_order(order)
        else:
            # Sell
            for order in orders:
                if order.symbol == data[-1]['symbol'] and order.side == 'buy':
                    order.side = 'sell'
                    order.type = 'market'
                    broker.update_order(order)
                    break
