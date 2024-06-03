from random import uniform


class GameException(Exception):
    pass


class Stock:
    stability = 0.6
    all_stocks = {}

    def __init__(self, name: str, short: str, base_price: int, randomness: float, multiplier: float = 1, grow: bool = True):
        self.name = name
        self.short = short
        self.base_price = base_price
        self.randomness = randomness
        self.multiplier = multiplier
        self.grow = grow
        self.all_stocks.update({short: self})

    def __str__(self):
        r = f"{self.name} ({self.short}):\n"
        r += f"    base price:    {self.base_price}\n"
        r += f"    multiplier:    {self.multiplier:.5f}\n"
        r += f"    current price: {self.price()}\n"
        r += f"    randomness:    {self.randomness:.3%}\n"
        r += f"    stability:     {self.stability:.3%}\n"
        r += f"    grow:          {self.grow}"
        return r

    def save(self):
        return f"Stock('{self.name}', '{self.short}', {self.base_price}, {self.randomness}, {self.multiplier}, {self.grow})"

    def random_tick(self):
        self.grow = self.grow == (self.stability >= uniform(0, 1))
        mult = 1 + uniform(0, self.randomness)
        self.multiplier *= mult if self.grow else 1/mult

    def price(self):
        return _ if (_ := int(self.base_price*self.multiplier)) else 1


class Trader:
    all_traders = {}

    def __init__(self, name: str, code: int, money: int, stocks: dict = {}):
        self.name = name
        self.money = money
        self.code = code
        if stocks:
            self.stocks = stocks
        else:
            self.stocks = {stock.short: 0 for stock in Stock.all_stocks.values()}
        self.all_traders.update({code: self})

    def __str__(self):
        r = f"{self.name} (#{self.code}; ${self.money}):\n"
        for stock_short, amount in self.stocks.items():
            r += f"    {stock_short}: {amount}\n"
        return r[:-1]

    def save(self):
        return f"Trader('{self.name}', {self.code}, {self.money}, {self.stocks})"



class Market:
    all_markets = {}

    def __init__(self, name: str, code: int, stocks: dict = {}):
        self.name = name
        self.code = code
        if stocks:
            self.stocks = stocks
        else:
            self.stocks = {stock.short: [10000, 1, stock.price()] for stock in Stock.all_stocks.values()}
        self.all_markets.update({code: self})

    def __str__(self):
        r = f"{self.name} (#{self.code}):\n"
        r += "        | amount     | multiplier | price \n"
        r += "   -----+------------+------------+------------\n"
        for stock_short in self.stocks:
            stock = Stock.all_stocks[stock_short]
            stock_data = self.stocks[stock_short]
            r += f"    {stock.short} | {stock_data[0]:>10} | {stock_data[1]:>10.3f} | {stock_data[2]:>10}\n"
        return r[:-1]

    def save(self):
        return f"Market('{self.name}', {self.code}, {self.stocks})"

    def update_prices(self):
        new = {}
        for stock_short in self.stocks:
            amount = self.stocks[stock_short][0]
            mult = 4/(3*amount/10000 + 1)
            new.update({stock_short: [amount, mult, _ if (_ := int(mult*Stock.all_stocks[stock_short].price())) else 1]})
        self.stocks = new

    def trade(self, trader_num: int, stock_short: str, stock_amount: int):
        try:
            trader = Trader.all_traders[trader_num]
        except KeyError:
            raise GameException("player not found")

        try:
            if trader.stocks[stock_short] < -stock_amount:
                raise GameException()
        except KeyError:
            raise GameException("stock not found")
        except GameException:
            raise GameException("not enough stock to sell")

        if trader.money < (stock_amount * self.stocks[stock_short][2]):
            raise GameException("not enough money to buy")

        if self.stocks[stock_short][0] < stock_amount:
            raise GameException("not enough stock to sell")

        trader.stocks[stock_short] += stock_amount
        trader.money -= stock_amount * self.stocks[stock_short][2]
        self.stocks[stock_short][0] -= stock_amount


def save(save_file: str):
    save_str = f"Stocks[{len(Stock.all_stocks)}]:\n"
    for stock in Stock.all_stocks.values():
        save_str += stock.save() + "\n"
    save_str += f"\nTraders[{len(Trader.all_traders)}]:\n"
    for trader in Trader.all_traders.values():
        save_str += trader.save() + "\n"
    save_str += f"\nMarkets[{len(Market.all_markets)}]:\n"
    for market in Market.all_markets.values():
        save_str += market.save() + "\n"
    with open(save_file, "w") as f:
        f.write(save_str)


def load(save_file: str):
    with open(save_file, "r") as f:
        for line in f.readlines():
            if line.split("(")[0] in ("Stock", "Trader", "Market"):
                eval(line)


if __name__ == "__main__":
    load("config.txt")
