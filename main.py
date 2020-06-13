import os
from dotenv import load_dotenv
from gasbot import GASBot

def main():
    load_dotenv()
    bot = GASBot(os.getenv("DISCORD_TOKEN"), os.getenv("DB_NAME"))
    bot.run()
    
main()