from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {
        "Greeting": "Welcome to the personal finance application!\n This application is to help users understand where there money is going and act like a financial coach empowering individuals to have full control over where their money goes, how much they spend, what they spend it on as well as put some money aside.\n Ultimately it's to improve financial literacy so we can finally take that wonder holiday to Japan, have more to invest or just buy that fancy thing we've been saving up for but haven't quite got! "
    }
