from flask import render_template, request, redirect, url_for, session, flash
from app import app
from classes import *


@app.route("/", methods=["GET", "POST"])
def home():
    load("save.txt")
    if not "marketID" in session:
        return render_template("home.html")
    elif request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        try:
            session["userID"] = int(request.form["userID"])
        except TypeError:
            print("Zadej cislo")
        return redirect(url_for("market"))


@app.route("/market", methods=["GET", "POST"])
def market():
    load("save.txt")
    if request.method == "GET" and "marketID" in session:
        market = Market.all_markets[session["marketID"]]
        user = Trader.all_traders[session["userID"]]
        table = make_table(market, user)
        return render_template("market.html", user=user, market=market, table=table)
    elif request.method == "POST":
        try:
            marketID = int(request.form["marketID"])
        except TypeError:
            print("Zadej cislo")
            return redirect(url_for("home"))
        session["marketID"] = marketID
    return redirect(url_for("home"))


def make_table(market, user):
    table = []
    for stock in Stock.all_stocks.values():
        amount = user.stocks[stock.short]
        price = market.stocks[stock.short][2]
        max_buy = min(user.money // price, market.stocks[stock.short][0])
        table.append([stock.name, stock.short, amount, price, max_buy])
    return table

@app.route("/buy", methods=["POST"])
def buy():
    market = Market.all_markets[session["marketID"]]
    user = Trader.all_traders[session["userID"]]
    traded = False
    for stockAction, amount in request.form.items():
        if not amount:
            continue
        amount = int(amount)
        traded = True
        short, action = stockAction.split("/")
        if action == "buy":
            market.trade(user.code, short, amount)
        else:
            market.trade(user.code, short, -amount)
    session.pop("userID", None)
    if traded:
        update_prices()
    save("save.txt")
    return redirect(url_for("home"))

@app.route("/highscores")
def highscores():
    leaderboard = sorted([[_.name, _.money] for _ in Trader.all_traders.values()], key=lambda x: -x[1])
    leaderboard = [[_+1, leaderboard[_][0], leaderboard[_][1]] for _ in range(len(leaderboard))]
    return render_template("highscores.html", leaderboard=leaderboard)

@app.errorhandler(Exception)
def error_site(e):
    flash(str(e))
    return redirect(url_for("home"))
