from transformers import Tool


class HFModelResearchTool(Tool):
    name = "web_research"
    description = (
        "This is a tool that does research by searching the web."
        "It takes a search topic and a search query that will be used to make the web search"
        "returns the result of the web search."
    )

    inputs = ["text"]
    outputs = ["text"]

    def __call__(self, task: str):
        print("Performing research with query:")
        # TODO implement search
        return "Here is the returned search result"
