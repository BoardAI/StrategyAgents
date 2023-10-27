import os
import numpy as np


def get_info(dir, log_filepath):
    print("dir:", dir)

    num_doc_files = -1
    num_utterance = -1
    num_reflection = -1
    num_prompt_tokens = -1
    num_completion_tokens = -1
    num_total_tokens = -1

    if os.path.exists(dir):
        filenames = os.listdir(dir)

        num_doc_files = 0
        for filename in filenames:
            if filename.endswith(".py") or filename.endswith(".png"):
                continue
            if os.path.isfile(os.path.join(dir, filename)):
                # print(filename)
                num_doc_files += 1
        # print("num_doc_files:", num_doc_files)

        if "meta.txt" in filenames:
            lines = open(os.path.join(dir, "meta.txt"), "r",
                         encoding="utf8").read().split("\n")

        if "requirements.txt" in filenames:
            lines = open(os.path.join(dir, "requirements.txt"),
                         "r", encoding="utf8").read().split("\n")

        for filename in filenames:
            if filename.endswith(".py"):
                # print("......filename:", filename)
                lines = open(os.path.join(dir, filename), "r",
                             encoding="utf8").read().split("\n")
        # print("code_lines:", code_lines)

        lines = open(log_filepath, "r", encoding="utf8").read().split("\n")
        start_lines = [line for line in lines if "**[Start Chat]**" in line]
        chat_lines = [line for line in lines if "<->" in line]
        num_utterance = len(start_lines) + len(chat_lines)
        # print("num_utterance:", num_utterance)

        lines = open(log_filepath, "r", encoding="utf8").read().split("\n")
        sublines = [
            line for line in lines if line.startswith("prompt_tokens:")]
        if len(sublines) > 0:
            nums = [int(line.split(": ")[-1]) for line in sublines]
            num_prompt_tokens = np.sum(nums)
            # print("num_prompt_tokens:", num_prompt_tokens)

        lines = open(log_filepath, "r", encoding="utf8").read().split("\n")
        sublines = [line for line in lines if line.startswith(
            "completion_tokens:")]
        if len(sublines) > 0:
            nums = [int(line.split(": ")[-1]) for line in sublines]
            num_completion_tokens = np.sum(nums)
            # print("num_completion_tokens:", num_completion_tokens)

        lines = open(log_filepath, "r", encoding="utf8").read().split("\n")
        sublines = [line for line in lines if line.startswith("total_tokens:")]
        if len(sublines) > 0:
            nums = [int(line.split(": ")[-1]) for line in sublines]
            num_total_tokens = np.sum(nums)
            # print("num_total_tokens:", num_total_tokens)

        lines = open(log_filepath, "r", encoding="utf8").read().split("\n")

        lines = open(log_filepath, "r", encoding="utf8").read().split("\n")
        num_reflection = 0
        for line in lines:
            if "on : Reflection" in line:
                num_reflection += 1
        # print("num_reflection:", num_reflection)

    cost = 0.0
    if num_prompt_tokens != -1:
        cost += num_prompt_tokens * 0.003 / 1000.0
    if num_completion_tokens != -1:
        cost += num_completion_tokens * 0.004 / 1000.0

    info = "\n\n💰**cost**=${:.6f}\n\n🔨um_doc_files**={}\n\n📃**cotterances**={}\n\n🤔**num_self_reflections**={}\n\n❓**num_prompt_tokens**={}\n\n❗**num_completion_tokens**={}\n\n🌟**num_total_tokens**={}" \
        .format(cost,
                num_doc_files,
                num_utterance,
                num_reflection,
                num_prompt_tokens,
                num_completion_tokens,
                num_total_tokens)

    return info
