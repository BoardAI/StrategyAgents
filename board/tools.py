import os
import json
import requests
from transformers import Tool
from bs4 import BeautifulSoup

browserless_api_key = os.getenv("BROWSERLESS_API_KEY")
serper_api_key = os.getenv("SERP_API_KEY")


def search_tool(query: str) -> str:
    """This is a tool that is useful for when you need to get data from a website url, passing both url and objective to the function.
    DO NOT make up any url, the url should only be from the search results

    :param query: the user's search query to search the web for
    :return: The search result
    """
    print("####### SEARCHING ######")
    print(query)
    return search(query)


class HFModelSearchTool(Tool):
    name = "search_web"
    description = (
        "This is a tool that is useful for when you need to answer questions about current events, data."
        "You should ask targeted questions"
    )

    inputs = ["query"]
    outputs = ["result"]

    def __call__(self, query: str):
        print("######## SEARCHING #########")
        print("query:", query)
        return search(query)


class HFModelWebScrapeTool(Tool):
    name = "scrape_website"
    description = (
        "This is a tool that is useful for when you need to get data from a website url, passing both url and objective to the function."
        "DO NOT make up any url, the url should only be from the search results"
    )

    inputs = ["objective, url"]
    outputs = ["result"]

    def __call__(self, objective: str, url: str):
        print("######## SCRAPING #########")
        print("objective:", objective, "url:", url)
        return scrape_website(objective, url)


def search(query):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": query
    })

    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print("Serp response:", response.text)

    return response.text


# 2. Tool for scraping
def scrape_website(objective: str, url: str):
    # scrape website, and also will summarize the content based on objective if the content is too large
    # objective is the original objective & task that user give to the agent, url is the url of the website to be scraped

    print("Scraping website...")
    # Define the headers for the request
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # Define the data to be sent in the request
    data = {
        "url": url
    }

    # Convert Python object to JSON string
    data_json = json.dumps(data)

    # Send the POST request
    post_url = f"https://chrome.browserless.io/content?token={browserless_api_key}"
    response = requests.post(post_url, headers=headers, data=data_json)

    # Check the response status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        print("CONTENT:", text)

        if len(text) > 10000:
            output = summary(objective, text)
            return output
        else:
            return text
    else:
        print(f"HTTP request failed with status code {response.status_code}")


def summary(objective, content):
    pass
    # TODO implement summary
    # llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")

    # text_splitter = RecursiveCharacterTextSplitter(
    #     separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
    # docs = text_splitter.create_documents([content])
    # map_prompt = """
    # Write a summary of the following text for {objective}:
    # "{text}"
    # SUMMARY:
    # """
    # map_prompt_template = PromptTemplate(
    #     template=map_prompt, input_variables=["text", "objective"])

    # summary_chain = load_summarize_chain(
    #     llm=llm,
    #     chain_type='map_reduce',
    #     map_prompt=map_prompt_template,
    #     combine_prompt=map_prompt_template,
    #     verbose=True
    # )

    # output = summary_chain.run(input_documents=docs, objective=objective)

    # return output
