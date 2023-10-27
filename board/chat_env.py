import os
import re
import shutil
import subprocess
import time

from board.documents import Documents
from board.roster import Roster
from board.utils import log_and_print_online


class ChatEnvConfig:
    def __init__(self, clear_structure,
                 brainstorming):
        self.clear_structure = clear_structure
        self.brainstorming = brainstorming

    def __str__(self):
        string = ""
        string += "ChatEnvConfig.clear_structure: {}\n".format(
            self.clear_structure)
        string += "ChatEnvConfig.brainstorming: {}\n".format(
            self.brainstorming)
        return string


class ChatEnv:
    def __init__(self, chat_env_config: ChatEnvConfig):
        self.config = chat_env_config
        self.roster: Roster = Roster()
        self.requirements: Documents = Documents()
        self.env_dict = {
            "directory": "",
            "task_prompt": "",
            "vision": "",
            "product_plan": "",
            "supplier_plan": "",
            "financial_plan": "",
            "market_plan": "",
            "product_research_summary": "",
            "supplier_research_summary": "",
            "financial_research_summary": "",
            "market_research_summary": "",
            "legal_concerns": "",
            "strategy_considerations": "",
        }

    @staticmethod
    def fix_module_not_found_error(test_reports):
        if "ModuleNotFoundError" in test_reports:
            for match in re.finditer(r"No module named '(\S+)'", test_reports, re.DOTALL):
                module = match.group(1)
                subprocess.Popen("pip install {}".format(
                    module), shell=True).wait()
                log_and_print_online(
                    "**[CMD Execute]**\n\n[CMD] pip install {}".format(module))

    def set_directory(self, directory):
        assert len(self.env_dict['directory']) == 0
        self.env_dict['directory'] = directory
        self.requirements.directory = directory

        if os.path.exists(self.env_dict['directory']) and len(os.listdir(directory)) > 0:
            new_directory = "{}.{}".format(
                directory, time.strftime("%Y%m%d%H%M%S", time.localtime()))
            shutil.copytree(directory, new_directory)
            print("{} Copied to {}".format(directory, new_directory))
        if self.config.clear_structure:
            if os.path.exists(self.env_dict['directory']):
                shutil.rmtree(self.env_dict['directory'])
                os.mkdir(self.env_dict['directory'])
                print("{} Created".format(directory))
            else:
                os.mkdir(self.env_dict['directory'])

    def recruit(self, agent_name: str):
        self.roster._recruit(agent_name)

    def exist_employee(self, agent_name: str) -> bool:
        return self.roster._exist_employee(agent_name)

    def print_employees(self):
        self.roster._print_employees()

    def _load_from_hardware(self, directory) -> None:
        self.codes._load_from_hardware(directory)

    def _update_requirements(self, generated_content):
        self.requirements._update_docs(generated_content)

    def rewrite_requirements(self):
        self.requirements._rewrite_docs()

    def get_requirements(self) -> str:
        return self.requirements._get_docs()

    def write_meta(self) -> None:
        directory = self.env_dict['directory']

        if not os.path.exists(directory):
            os.mkdir(directory)
            print("{} Created.".format(directory))

        meta_filename = "meta.txt"
        with open(os.path.join(directory, meta_filename), "w", encoding="utf-8") as writer:
            writer.write("{}:\n{}\n\n".format(
                "Task", self.env_dict['task_prompt']))
            writer.write("{}:\n{}\n\n".format("Config", self.config.__str__()))
            writer.write("{}:\n{}\n\n".format(
                "Roster", ", ".join(self.roster.agents)))
            writer.write("{}:\n{}\n\n".format(
                "Vision", self.env_dict['vision']))
            writer.write("{}:\n{}\n\n".format(
                "Market Plan", self.env_dict['market_plan']))
            writer.write("{}:\n{}\n\n".format(
                "Product Plan", self.env_dict['product_plan']))
            writer.write("{}:\n{}\n\n".format(
                "Supplier Plan", self.env_dict['supplier_plan']))
            writer.write("{}:\n{}\n\n".format(
                "Financial Plan", self.env_dict['financial_plan']))
            writer.write("{}:\n{}\n\n".format(
                "Market Research Summary", self.env_dict['market_research_summary']))
            writer.write("{}:\n{}\n\n".format(
                "Product Research Summary", self.env_dict['product_research_summary']))
            writer.write("{}:\n{}\n\n".format(
                "Supplier Research Summary", self.env_dict['supplier_research_summary']))
            writer.write("{}:\n{}\n\n".format(
                "Financial Research Summary", self.env_dict['financial_research_summary']))
            writer.write("{}:\n{}\n\n".format(
                "Legal Concerns", self.env_dict['legal_concerns']))
            writer.write("{}:\n{}\n\n".format(
                "Strategy Considerations", self.env_dict['strategy_considerations']))
        print(os.path.join(directory, meta_filename), "Wrote")
