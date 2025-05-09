# import asyncio
import asyncio
import re
from dataclasses import dataclass

from modules.bot.linkedin.linkedin_job import LinkedinJob
from modules.core import JobBot, JobBotOptions


@dataclass
class LinkedinSearch:
    job: str
    location: str = None


@dataclass
class LinkedinBotOptions(JobBotOptions):
    searches: list[LinkedinSearch] = None


class LinkedinBot(JobBot):

    def __init__(self, options: LinkedinBotOptions):
        super().__init__(options)
        self._searches = options.searches

    async def _setup(self):
        url = "https://www.linkedin.com/jobs/search"
        self._driver.uc_activate_cdp_mode(url)
        if self._username and self._password:
            self._logged = await self._login()
        else:
            await self._close_popup()

    async def _start(self):
        try:
            CAPTCHA_SELECTOR = ""  # TODO: Descobrir o selector do linkedin para captcha
            self._captcha_task = asyncio.create_task(self._captcha(CAPTCHA_SELECTOR))
            WRAPPER_SELECTOR = "//*[@class='two-pane-serp-page__detail-view']"
            if self._logged:
                WRAPPER_SELECTOR = "//*[contains(@class, 'jobs-details__main-content')]"
            async with self._captcha_condition:
                for index, search in enumerate(self._searches):
                    offset = 0
                    self._driver.cdp.sleep(5)
                    self._search_job(search.job, search.location)
                    await self._captcha_condition.wait_for(lambda: not self._captcha_active)
                    self._logger.info(
                        f"[{index+1} de {len(self._searches)}] Pesquisando vagas: {search.job} | Localização: {search.location}"
                    )
                    self._driver.cdp.sleep(5)
                    self._driver.cdp.assert_element_present(WRAPPER_SELECTOR, timeout=15)
                    while True:  # Loop entre as páginas
                        while True:  # Loop entre "page-down" para carregar mais itens
                            self._driver.cdp.sleep(10)  # Aguarda a lista carregar...
                            job_list_elements = self._get_job_list()[offset:]
                            if len(job_list_elements) == 0:
                                break
                            for job_element in job_list_elements:
                                job_element.click()
                                await self._captcha_condition.wait_for(lambda: not self._captcha_active)
                                CURRENT_URL = self._driver.cdp.get_current_url()
                                URL_PATTERN = r"currentJobId=(\d+)"
                                JOB_ID = re.search(URL_PATTERN, CURRENT_URL)[1]
                                job = LinkedinJob(id=JOB_ID)
                                job.url = f"https://www.linkedin.com/jobs/view/{JOB_ID}"
                                self._get_job_data(job)
                                self._append_job(job)
                            offset = len(job_list_elements)
                            self._driver.cdp.scroll_to_bottom()
                        btn_next = self._next_page()
                        if btn_next is None:
                            break
                        btn_next.click()
        except Exception as err:
            self._logger.error(err)
            raise err
        finally:
            # self._captcha_task.cancel()
            # await self._captcha_task
            pass

    def _next_page(self):
        NEXT_BUTTON_SELECTOR = "//*[@id='main-content']/section[2]/button"
        if self._logged:
            NEXT_BUTTON_SELECTOR = "//button[@id='ember223']"
        if self._driver.cdp.is_element_present(NEXT_BUTTON_SELECTOR):
            return self._driver.cdp.find_element(NEXT_BUTTON_SELECTOR)

    async def _login(self):
        try:
            MODAL_SELECTOR = "//*[@id='base-contextual-sign-in-modal']"
            LOGIN_BUTTON_POPUP_SELECTOR = f"{MODAL_SELECTOR}//div[@class='sign-in-modal']/button"
            self._driver.cdp.click(LOGIN_BUTTON_POPUP_SELECTOR)
            INPUT_USERNAME_SELECTOR = "//*[@id='base-sign-in-modal_session_key']"
            INPUT_PASSWORD_SELECTOR = "//*[@id='base-sign-in-modal_session_password']"
            BUTTON_SELECTOR = "//*[@id='base-sign-in-modal']/div/section/div/div/form/div[2]/button"
            self._driver.cdp.type(INPUT_USERNAME_SELECTOR, self._username)
            self._driver.cdp.type(INPUT_PASSWORD_SELECTOR, self._password)
            self._driver.cdp.click(BUTTON_SELECTOR)
            self._logged = True
        except Exception as err:
            self._logger.error(f"Erro durante o login: {err}")

    async def _close_popup(self):
        CLOSE_BUTTON_POPUP_SELECTOR = "//*[@id='base-contextual-sign-in-modal']/div/section/button"
        self._logger.debug(f"Aguardando popup inicial...")
        if self._driver.is_element_present(CLOSE_BUTTON_POPUP_SELECTOR):
            self._logger.debug(f"Popup fechado com sucesso!")
            self._driver.cdp.click(CLOSE_BUTTON_POPUP_SELECTOR)
            return
        self._logger.debug(f"Popup não encontrado.")

    def _search_job(self, job: str, location: str = None):
        INPUT_JOB_ID = "#job-search-bar-keywords"
        INPUT_LOCATION_ID = "#job-search-bar-location"
        BUTTON_SEARCH_XPATH = "//*[@id='jobs-search-panel']/form/button"
        if self._logged:
            INPUT_JOB_ID = "#jobs-search-box-keyword-id-ember99"
            INPUT_LOCATION_ID = "#jobs-search-box-location-id-ember99"
            BUTTON_SEARCH_XPATH = "//*[@id='global-nav-search']/div/div[2]/button[1]"
        for id, value in [(INPUT_JOB_ID, job), (INPUT_LOCATION_ID, location)]:
            if value:
                self._driver.cdp.type(id, value)
        self._driver.cdp.click(BUTTON_SEARCH_XPATH)

    def _get_job_list(self):
        SELECTOR_JOB_LIST = "//*[@id='main-content']/section/ul/li/div/a"
        if self._logged:
            SELECTOR_JOB_LIST = "//*[@id='main']/div/div[2]/div[1]/div/ul//a"
        return self._driver.cdp.find_elements(SELECTOR_JOB_LIST, timeout=15)

    def _get_job_data(self, job: LinkedinJob, timeout=15):
        WRAPPER = "//*[@class='two-pane-serp-page__detail-view']"
        SELECTORS = {
            "title": f"{WRAPPER}//a[@class='topcard__link']",
            "company": f"{WRAPPER}//*[@class='topcard__flavor-row'][1]/span[1]",
            "location": f"{WRAPPER}//*[@class='topcard__flavor-row'][1]/span[2]",
            "button": f"{WRAPPER}//div/button[contains(@class, 'sign-up')]",
            "description": f"{WRAPPER}//*[contains(@class, 'description__text')]/section/div",
            "details": f"{WRAPPER}//*[@class='description__job-criteria-list']/li",
        }
        if self._logged:
            WRAPPER = "//*[contains(@class, 'jobs-details__main-content')]"
            SELECTORS["title"] = f"{WRAPPER}//h1/a"
            SELECTORS["company"] = f"{WRAPPER}/div[1]/div/div[1]/div/div[1]/div[1]/div/a"
            SELECTORS["location"] = f"{WRAPPER}/div[1]/div/div[1]/div/div[3]/div/span/span[1]"
            SELECTORS["button"] = f"{WRAPPER}//*[@id='jobs-apply-button-id']"
            SELECTORS["description"] = f"{WRAPPER}//*[@id='job-details']/div"
            SELECTORS["details"] = f"{WRAPPER}//ul/li//span[contains(@class, 'ui-label')]/span"
        BUTTON_ELEMENT = self._driver.cdp.find_element(SELECTORS["button"])
        job.easy_application = "simplificada" in BUTTON_ELEMENT.text
        job.title = self._driver.cdp.find_element(SELECTORS["title"], timeout).text
        job.company = self._driver.cdp.find_element(SELECTORS["company"], timeout).text
        job.location = self._driver.cdp.find_element(SELECTORS["location"], timeout).text
        job.description = self._driver.cdp.find_element(SELECTORS["description"], timeout).text
        if self._driver.cdp.is_element_present(SELECTORS["details"]):
            details = dict()
            sections = self._driver.cdp.find_elements(SELECTORS["details"], timeout)
            for index in range(0, len(sections), 2 if self._logged else 1):
                if self._logged:
                    # TODO: Descobri o formato correto dos detalhes quando conectado
                    HIDDEN_VALUE = "Corresponde às suas preferências de vaga e o tipo de "
                    key = sections[index].text
                    values = sections[index + 1].text_fragment
                    values = values[len(HIDDEN_VALUE) :]
                else:
                    key = self._driver.cdp.find_element(f"{SELECTORS['details']}[{index + 1}]/h3").text
                    values = self._driver.cdp.find_element(f"{SELECTORS['details']}[{index + 1}]/span").text
                details[key] = values
            job.details = details
        return job
