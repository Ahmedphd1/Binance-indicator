import datetime

today = datetime.date.today()

def newfiles():
    try:
        with open(f'logfile{today.strftime("%Y-%m-%d")}.txt', "w") as f:
            f.close()
        with open(f'report{today.strftime("%Y-%m-%d")}.txt', "w") as f:
            f.close()
    except:
        print("could not create files")

