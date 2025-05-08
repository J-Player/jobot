import logging
from modules.bot.indeed.indeed_job import IndeedJob
from modules.core import Bot
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException


class IndeedBot(Bot):

    def __init__(self, username: str, password: str):
        Bot.__init__()

    def _setup(self):
        url = "https://br.indeed.com"
        self.driver.activate_cdp_mode(url)
        self._close_cookie_popup()

    def _start(self):
        try:
            self._search_job()
            self.driver.cdp.sleep(5)
            job_list_elements: list[WebElement] = self._get_job_list()
            job_list: list[IndeedJob] = []
            JOB_DETAILS_WRAPPER_ID = "#jobsearch-ViewjobPaneWrapper"
            self.driver.cdp.is_element_visible(JOB_DETAILS_WRAPPER_ID)
            for job_element in job_list_elements:
                job = IndeedJob()
                job.title = job_element.find_element(By.XPATH, ".//h2/span")
                self.driver.cdp.click(job_element)
                job_list.append(job)
        except Exception as err:
            logging.error(err)
        else:
            logging.info(f"Bot executado com sucesso!")

    def _captcha_resolve(self):
        PATH_ELEMENT = "#JnAv0 div div"
        self.driver.cdp.gui_click_element(PATH_ELEMENT)

    def _close_cookie_popup(self):
        try:
            BUTTON_COOKIE_REJECT_ID = "#onetrust-reject-all-handler"
            logging.debug(f"Aguardando popup de cookies.")
            self.driver.cdp.click(BUTTON_COOKIE_REJECT_ID, timeout=10)
        except TimeoutException:
            logging.debug(f"Popup não encontrado.")

    def _search_job(self, job: str, location: str):
        INPUT_JOB_ID = "#text-input-what"
        INPUT_LOCATION_ID = "#text-input-where"
        BUTTON_SEARCH_XPATH = '//button[@type="submit"]'
        for id, value in [(INPUT_JOB_ID, job), (INPUT_LOCATION_ID, location)]:
            self.driver.cdp.type(id, value)
        self.driver.cdp.click(BUTTON_SEARCH_XPATH)

    def _next_page(self):
        XPATH_NAV_PAGINATION = '//nav[@role="navigation"]'

    def _get_job_list(self):
        XPATH_JOB_LIST = '//*[@id="mosaic-provider-jobcards"]//ul//a'
        return self.driver.cdp.find_elements(XPATH_JOB_LIST, timeout=10)
