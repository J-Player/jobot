from seleniumbase import SB
from dotenv import load_dotenv

from modules.bot.indeed.indeed_bot import IndeedBot

load_dotenv('../')

if __name__ == "__main__":
    bot = IndeedBot()
    bot.start()