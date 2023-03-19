class Strategy:
    def __init__(self):
        pass

    def get_signal(self, symbol):
        """
        This method should return a signal indicating whether to buy or sell the given symbol.
        """
        raise NotImplementedError("Subclasses must implement get_signal method.")
