from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from BackTester import BackTester
from Models import *
import datetime as dt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/", tags=["Basic"])
def home():
    return "hello world"


@app.post("/start_test/", tags=["Main"])
def start_test(jobstarter: JobStarter):
    endDate = dt.datetime.now()
    startDate = endDate - dt.timedelta(365*jobstarter.years)
    stocks = [stock + ".SA" for stock in jobstarter.stocks]
    backtester = BackTester(stocks, startDate, endDate,
                            jobstarter.method, jobstarter.initial_investiment, 0)

    montante_final, portifolio_returns, return_per_stock = backtester.run()
    print("port : ", portifolio_returns, "type : ", type(portifolio_returns))

    print("per_stock_return : ", return_per_stock)
    to_return = {"montante_final": montante_final,
                 "portifolio_returns": list(portifolio_returns),
                 "return_per_stock": return_per_stock}

    return to_return
