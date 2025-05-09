import asyncio
import os
from itertools import product

import nest_asyncio
from dotenv import load_dotenv

from modules.bot.indeed import IndeedBot, IndeedBotOptions, IndeedSearch
from modules.bot.linkedin import LinkedinBot, LinkedinBotOptions, LinkedinSearch

nest_asyncio.apply()

load_dotenv("../")


async def indeed():
    jobs = [
        # "java",
        # "desenvolvedor",
        "desenvolvedor back end",
        # "desenvolvedor java",
        "desenvolvedor java junior",
        # "desenvolvedor java trainee",
        "desenvolvedor junior",
        "desenvolvedor sem experiência",
        "desenvolvedor web",
        # "programador",
        # "programador java",
        "programador java junior",
        # "programador java trainee",
        "programador junior",
        # "programador trainee",
        "programador sem experiência",
        "programador web",
    ]
    locations = [
        "Rio de Janeiro, RJ",
        "Remoto",
    ]
    options = IndeedBotOptions(
        # username=os.getenv("INDEED_USER"),
        searches=[IndeedSearch(j, l) for j, l in product(jobs, locations)],
        keywords=["java", "javascript", "spring", "react", "node", "nodejs", "typescript"],
        exclude_keywords=["english", "fluent"],
    )
    bot = IndeedBot(options)
    await bot.start()


async def linkedin():
    jobs = [
        "java",
        "desenvolvedor",
        "desenvolvedor back end",
        "desenvolvedor java",
        "desenvolvedor java junior",
        "desenvolvedor java trainee",
        "desenvolvedor junior",
        "desenvolvedor sem experiência",
        "desenvolvedor web",
        "programador",
        "programador java",
        "programador java junior",
        "programador java trainee",
        "programador junior",
        "programador trainee",
    ]
    locations = [
        "Rio de Janeiro, RJ",
        "Remoto",
    ]
    options = LinkedinBotOptions(
        username=os.getenv("LINKEDIN_USER"),
        password=os.getenv("LINKEDIN_PASS"),
        searches=[LinkedinSearch(j, l) for j, l in product(jobs, locations)],
        keywords=["java", "javascript", "spring", "react", "node", "nodejs", "typescript"],
        exclude_keywords=["english", "fluent"],
    )
    bot = LinkedinBot(options)
    await bot.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.run(indeed())
