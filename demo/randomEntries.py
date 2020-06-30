import random
import datetime


categories = ["groceries", "car", "computer", "gaming", "business"]
descriptions = ["thank you!", "customer id: 12312", "purchase 0121", "your purchase no 92122", "insurance id 2911"]

def randDate():
    stime = datetime.datetime(year=2015, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    etime = datetime.datetime.now()

    return stime + random.random() * (etime - stime)

with open("names.txt", "r") as f:
    for l in f:
        thedate = randDate().strftime("%d.%m.%Y")
        cat = random.choice(categories)
        desc = random.choice(descriptions)
        amount = random.randrange(-200000, 200000, 1) * 0.01
        print(thedate + "; " + l.strip() + "; " + cat + "; " + desc + "; " + "{:.2f}".format(amount))
