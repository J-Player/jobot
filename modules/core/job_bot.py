import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass

from modules.core import Bot, Job
from modules.utils import default_serializer, normalize_string


@dataclass
class JobBotOptions:
    username: str = None
    password: str = None
    keywords: list[str] = None
    full_match: bool = False
    exclude_keywords: list[str] = None


class JobBot(Bot):

    def __init__(self, options: JobBotOptions):
        super().__init__()
        self._username = options.username
        self._password = options.password
        self.__job_keywords = options.keywords
        self.__full_match = options.full_match
        self.__job_keywords_ignored = options.exclude_keywords
        self._logged: False
        self._jobs = defaultdict(Job)
        self.__jobs_ignored: list[str] = []

    async def _setup(self):
        self.__load_jobs_files()

    async def _login(self):
        raise NotImplementedError(f"The method {self._login.__name__} must be implemented.")

    @property
    def jobs(self):
        return self._jobs.copy()

    @property
    def jobs_ignored(self):
        return self.__jobs_ignored.copy()

    def _append_job(self, job: Job):
        if job.id in [*self._jobs.keys()] or job.id in self.__jobs_ignored:
            self._logger.warning(f'Job de id "{job.id}" já existe na lista.')
            return
        INCLUDE_REGEX = [rf"\b{re.escape(word)}\b" for word in self.__job_keywords] if self.__job_keywords else []
        EXCLUDE_REGEX = [rf"\b{re.escape(word)}\b" for word in self.__job_keywords_ignored] if self.__job_keywords_ignored else []
        description = normalize_string(job.description.lower().strip().replace(r"\s+", " "))
        include_condition = True
        if INCLUDE_REGEX:
            matches = (re.search(pattern, description, re.IGNORECASE) is not None for pattern in INCLUDE_REGEX)
            include_condition = all(matches) if self.__full_match else any(matches)
        exclude_condition = False
        if EXCLUDE_REGEX:
            exclude_matches = (re.search(ex_pattern, description, re.IGNORECASE) is not None for ex_pattern in EXCLUDE_REGEX)
            exclude_condition = any(exclude_matches)
        if include_condition and not exclude_condition:
            self._jobs[job.id] = job

    def _pop_job(self, job: Job | str):
        if type(job) == str:
            self._jobs.pop(job)
        else:
            del self._jobs[job.id]

    def _clear_job_list(self):
        self._jobs.clear()
        self._logger.debug(f"Lista de jobs foi limpa.")

    def __load_jobs_files(self):
        DIR_PATH = rf"jobs/{self.__class__.__name__.lower()}"
        os.makedirs(DIR_PATH, exist_ok=True)
        JSON_FILES = [pos_json.rsplit(".")[0] for pos_json in os.listdir(DIR_PATH) if pos_json.endswith(".json")]
        if len(JSON_FILES) == 0:
            self._logger.debug(f"Nenhum arquivo de job encontrado no diretório: {DIR_PATH}")
            return
        self.__jobs_ignored = JSON_FILES
        self._logger.debug(f"Total de jobs carregados: {len(self.__jobs_ignored)}")

    def _save_job_list(self):
        DIR_PATH = f"jobs/{self.__class__.__name__.lower()}"
        if len(self.jobs) > 0:
            self._logger.debug(f"Salvando jobs em arquivos no diretório: {DIR_PATH}")
            for key, job in self._jobs.items():
                filepath = f"{DIR_PATH}/{key}.json"
                exists = os.path.exists(filepath)
                os.makedirs(DIR_PATH, exist_ok=True)
                if not exists:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(job, f, default=default_serializer, indent=4, ensure_ascii=False)
