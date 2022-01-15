import requests
import traceback
import time
from configparser import ConfigParser
from binancelibrary import *
import termcolor
import threading

# apikey = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRoZXdheTAwN0BnbWFpbC5jb20iLCJpYXQiOjE2MTc4OTAzNTcsImV4cCI6NzkyNTA5MDM1N30.bmV4uLiLnjqpu6xqw7UnGuab5LLs5q2EioOZ43FD-p0

# python exe: pyinstaller --onefile GUI.py

file = "config.ini"
config = ConfigParser()
config.read(file)

print("your balance")
seebalance()


def getkdj():

    try:
        response = requests.get(f"https://api.taapi.io/kdj?secret=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRoZXdheTAwN0BnbWFpbC5jb20iLCJpYXQiOjE2MTc4OTAzNTcsImV4cCI6NzkyNTA5MDM1N30.bmV4uLiLnjqpu6xqw7UnGuab5LLs5q2EioOZ43FD-p0&exchange=binance&symbol={str(config['appstate']['symbol'])}&interval={str(config['appstate']['timeframe'])}&period=9")

        return response.json()
    except:
        traceback.print_exc()

def buykdj(exit_event):
    counter = 0

    seebalance()

    while exit_event.is_set() == False:
        try:
            kdj = getkdj()

            print("Monitoring Intrument: Buy criteria")

            print("Value k                          Value D:                        Value J:             J-K")
            print(
                f'{kdj["valueK"]}             {kdj["valueD"]}             {kdj["valueJ"]}     {float(kdj["valueJ"]) - float(kdj["valueK"])}')

            for x in range(3):
                print(" ")

            if float(kdj['valueJ']) - float(kdj['valueK']) > 0:
                counter += 1

                print(
                    f'J-K value is greater than 0: {float(kdj["valueJ"]) - float(kdj["valueK"])}: counter is incremented: {counter}')

                for x in range(3):
                    print(" ")

            elif float(kdj['valueJ']) - float(kdj['valueK']) < 0:
                counter = 0
                print(
                    f'J-K value is less than 0: {float(kdj["valueJ"]) - float(kdj["valueK"])}: counter is reset: {counter}')

                for x in range(3):
                    print(" ")

            if counter >= int(config['appstate']['countern']):

                print("Cheking for open orders")

                if checkportfolio() == True:
                    print("Portfolio is not Empty: Attempting to sell already open order")

                    for x in range(3):
                        print(" ")

                    if createorder("sell", "market", modquantity=getbalances()) == False:
                        return False
                    time.sleep(3)


                print(f'Counter(n) reached: Attempting to buy market order for: {str(config["appstate"]["symbol"])} Control counter is: {counter}: Counter(n) is: {int(config["appstate"]["countern"])}')

                for x in range(3):
                    print(" ")

                if createorder("buy", "market",modquantity=getquantity()) == False:
                    print(f'You cannot buy that instrument.. you dont have balance: {str(config["appstate"]["symbol"]).split("/")[1]}')
                    return False
                time.sleep(3)

                if sellkdj(exit_event) == False:
                    return False

                time.sleep(2)
                break
        except:
            traceback.print_exc()

    time.sleep(2)

def sellkdj(exit_event):
    counter = 0

    while exit_event.is_set() == False:
        try:
            kdj = getkdj()

            print("Monitoring Intrument: SELL criteria")

            print("Value k                          Value D:                        Value J:             J-K")
            print(
                f'{kdj["valueK"]}             {kdj["valueD"]}             {kdj["valueJ"]}     {float(kdj["valueJ"]) - float(kdj["valueK"])}')

            for x in range(3):
                print(" ")

            if float(kdj['valueJ']) - float(kdj['valueK']) < 0:
                counter += 1

                print(
                    f'J-K value is less than 0: {float(kdj["valueJ"])} - float(kdj["valueK"]): counter is incremented: {counter}')

                for x in range(3):
                    print(" ")

            elif float(kdj['valueJ']) - float(kdj['valueK']) > 0:
                counter = 0

                print(
                    f'J-K value is greater than 0: {float(kdj["valueJ"])} - float(kdj["valueK"]): counter is reset: {counter}')

                for x in range(3):
                    print(" ")

            if counter >= int(config['appstate']['countern']):

                print(
                    f'Counter(n) reached. Attempting to sell intrument: {str(config["appstate"]["symbol"])} Control counter is: {counter}: Counter(n) is: {int(config["appstate"]["countern"])}')

                for x in range(3):
                    print(" ")

                if createorder("sell", "market", modquantity=getbalances()) == False:
                    return False
                time.sleep(3)

                print("order sold. Creating report")

                for x in range(3):
                    print(" ")

                createreport()

                break
        except:
            traceback.print_exc()

    time.sleep(2)

