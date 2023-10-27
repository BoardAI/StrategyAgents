# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
# Licensed under the Apache License, Version 2.0 (the “License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an “AS IS” BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =========== Copyright 2023 @ CAMEL-AI.org. All Rights Reserved. ===========
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import os
import openai
import tiktoken

from camel.typing import ModelType
from board.utils import log_and_print_online
from board.tools import HFModelSearchTool, HFModelWebScrapeTool, search_tool

from langsmith.run_helpers import traceable
from funkagent import parser

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ModelBackend(ABC):
    r"""Base class for different model backends.
    May be OpenAI API, a local LLM, a stub for unit tests, etc."""

    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        r"""Runs the query to the backend model.

        Raises:
            RuntimeError: if the return value from OpenAI API
            is not a dict that is expected.

        Returns:
            Dict[str, Any]: All backends must return a dict in OpenAI format.
        """
        pass


class OpenAIModel(ModelBackend):
    r"""OpenAI API in a unified ModelBackend interface."""

    def __init__(self, model_type: ModelType, model_config_dict: Dict) -> None:
        super().__init__()
        self.model_type = model_type
        self.model_config_dict = model_config_dict

    @traceable(run_type="llm")
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        string = "\n".join([message["content"]
                           for message in kwargs["messages"]])
        encoding = tiktoken.encoding_for_model(self.model_type.value)
        num_prompt_tokens = len(encoding.encode(string))
        gap_between_send_receive = 15 * len(kwargs["messages"])
        num_prompt_tokens += gap_between_send_receive

        num_max_token_map = {
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-3.5-turbo-0613": 4096,
            "gpt-3.5-turbo-16k-0613": 16384,
            "gpt-4": 8192,
            "gpt-4-0613": 8192,
            "gpt-4-32k": 32768,
        }
        num_max_token = num_max_token_map[self.model_type.value]
        num_max_completion_tokens = num_max_token - num_prompt_tokens
        self.model_config_dict['max_tokens'] = num_max_completion_tokens
        response = openai.ChatCompletion.create(*args, **kwargs,
                                                model=self.model_type.value,
                                                **self.model_config_dict)

        log_and_print_online(
            "**[OpenAI_Usage_Info Receive]**\nprompt_tokens: {}\ncompletion_tokens: {}\ntotal_tokens: {}\n".format(
                response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"],
                response["usage"]["total_tokens"]))
        if not isinstance(response, Dict):
            raise RuntimeError("Unexpected return from OpenAI API")
        return response


class OpenAIToolModel(ModelBackend):
    r"""OpenAI Tool Agent in a unified ModelBackend interface."""

    def __init__(self,
                 model_type: ModelType,
                 model_config_dict: Dict) -> None:
        super().__init__()
        self.model_type = model_type
        self.model_config_dict = model_config_dict
        # self.tools = [HFModelSearchTool(), HFModelWebScrapeTool()]
        self.tools = [search_tool]
        self.functions = self._parse_functions(self.tools)

    def _parse_functions(self, functions: Optional[list]) -> Optional[list]:
        if functions is None:
            return None
        return [parser.func_to_json(func) for func in functions]

    # def _create_func_mapping(self, functions: Optional[list]) -> dict:
    #     if functions is None:
    #         return {}
    #     return {func.__name__: func for func in functions}

    @traceable(run_type="llm")
    def _create_chat_completion(
        self, *args, **kwargs
    ) -> openai.ChatCompletion:
        response = openai.ChatCompletion.create(
            *args, **kwargs,
            model=self.model_type.value,
            **self.model_config_dict,
            functions=self.functions
        )
        return response

    # def _generate_response(self, *args, **kwargs) -> openai.ChatCompletion:
    #     while True:
    #         print('.', end='')
    #         res = self._create_chat_completion(
    #             *args, **kwargs,
    #             # self.chat_history + self.internal_thoughts
    #         )
    #         finish_reason = res.choices[0].finish_reason

    #         if finish_reason == 'stop' or len(self.internal_thoughts) > 3:
    #             # create the final answer
    #             final_thought = self._final_thought_answer()
    #             final_res = self._create_chat_completion(
    #                 self.chat_history + [final_thought],
    #                 use_functions=False
    #             )
    #             return final_res
    #         elif finish_reason == 'function_call':
    #             self._handle_function_call(res)
    #         else:
    #             raise ValueError(f"Unexpected finish reason: {finish_reason}")

    # def _handle_function_call(self, res: openai.ChatCompletion):
    #     self.internal_thoughts.append(res.choices[0].message.to_dict())
    #     func_name = res.choices[0].message.function_call.name
    #     args_str = res.choices[0].message.function_call.arguments
    #     result = self._call_function(func_name, args_str)
    #     res_msg = {'role': 'assistant', 'content': (
    #         f"The answer is {result}.")}
    #     self.internal_thoughts.append(res_msg)

    # def _call_function(self, func_name: str, args_str: str):
    #     args = json.loads(args_str)
    #     func = self.func_mapping[func_name]
    #     res = func(**args)
    #     return res

    # def _final_thought_answer(self):
    #     thoughts = ("To answer the question I will use these step by step instructions."
    #                 "\n\n")
    #     for thought in self.internal_thoughts:
    #         if 'function_call' in thought.keys():
    #             thoughts += (f"I will use the {thought['function_call']['name']} "
    #                          "function to calculate the answer with arguments "
    #                          + thought['function_call']['arguments'] + ".\n\n")
    #         else:
    #             thoughts += thought["content"] + "\n\n"
    #     self.final_thought = {
    #         'role': 'assistant',
    #         'content': (f"{thoughts} Based on the above, I will now answer the "
    #                     "question, this message will only be seen by me so answer with "
    #                     "the assumption with that the user has not seen this message.")
    #     }
    #     return self.final_thought

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        self.name = "Negotiations Tool Agent"
        string = "\n".join([message["content"]
                           for message in kwargs["messages"]])
        encoding = tiktoken.encoding_for_model(self.model_type.value)
        num_prompt_tokens = len(encoding.encode(string))
        num_functions_tokens = len(encoding.encode(str(self.functions)))
        gap_between_send_receive = 15 * len(kwargs["messages"])
        num_prompt_tokens += gap_between_send_receive

        num_max_token_map = {
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-3.5-turbo-0613": 4096,
            "gpt-3.5-turbo-16k-0613": 16384,
            "gpt-4": 8192,
            "gpt-4-0613": 8192,
            "gpt-4-32k": 32768,
        }
        num_max_token = num_max_token_map[self.model_type.value]
        num_max_completion_tokens = num_max_token - \
            num_prompt_tokens - num_functions_tokens
        self.model_config_dict['max_tokens'] = num_max_completion_tokens
        # task = kwargs["messages"][-1]["content"]
        # response = self.agent.ask(task)
        # response = self.agent.chat(task=task, *args, **kwargs)

        response = self._create_chat_completion(*args, **kwargs)
        print(response)
        # response = openai.ChatCompletion.create(*args, **kwargs,
        #                                         model=self.model_type.value,
        #                                         **self.model_config_dict,
        #                                         functions=self.tools)

        log_and_print_online(
            "**[OpenAI_Usage_Info Receive]**\nprompt_tokens: {}\ncompletion_tokens: {}\ntotal_tokens: {}\n".format(
                response["usage"]["prompt_tokens"], response["usage"]["completion_tokens"],
                response["usage"]["total_tokens"]))
        if not isinstance(response, Dict):
            raise RuntimeError("Unexpected return from OpenAI API")
        return response


class StubModel(ModelBackend):
    r"""A dummy model used for unit tests."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        ARBITRARY_STRING = "Lorem Ipsum"

        return dict(
            id="stub_model_id",
            usage=dict(),
            choices=[
                dict(finish_reason="stop",
                     message=dict(content=ARBITRARY_STRING, role="assistant"))
            ],
        )


class ModelFactory:
    r"""Factory of backend models.

    Raises:
        ValueError: in case the provided model type is unknown.
    """

    @staticmethod
    def create(model_type: ModelType,
               model_config_dict: Dict,
               tools: bool = False) -> ModelBackend:
        default_model_type = ModelType.GPT_3_5_TURBO

        if model_type in {
            ModelType.GPT_3_5_TURBO, ModelType.GPT_4, ModelType.GPT_4_32k,
            None
        }:
            if tools:
                model_class = OpenAIToolModel
            else:
                model_class = OpenAIModel
        elif model_type == ModelType.STUB:
            model_class = StubModel
        else:
            raise ValueError("Unknown model")

        if model_type is None:
            model_type = default_model_type

        # log_and_print_online("Model Type: {}".format(model_type))
        inst = model_class(model_type, model_config_dict)
        return inst
