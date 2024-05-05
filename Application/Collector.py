from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
import os
import json
import requests
from langchain_community.tools.google_serper.tool import GoogleSerperResults
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

class information_collector():
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.0)
        self.tools = [GoogleSerperResults(api_wrapper=GoogleSerperAPIWrapper())]
        self.question_types = ['Introduction', 'SWOT', 'Porter', 'Ansoff', 'Canvas', 'Competitor', 'Diligence']

    def proposing_questions(self, question_type, company):
        Introduction_question_prompt = """
        You are a professional business analyst.
        Now you are trying to write an introduction about ```{company}```.
        Propose 5 questions that might be useful for creating the company introduction.
        Return them in the following JSON format:

        questions: <list of questions>
        """
        SWOT_question_prompt = """
        You are a professional business analyst.
        Now you are trying to do a SWOT analysis about ```{company}```.
        Propose 5 questions that might be useful for creating the SWOT analysis.
        Return them in the following JSON format:

        questions: <list of questions>
        """
        Five_Forces_question_prompt = """
        You are a professional business analyst.
        Now you are trying to do a Porter Five Forces analysis about ```{company}```.
        Propose 5 questions that might be useful for creating the Porter Five Forces analysis.
        Return them in the following JSON format:

        questions: <list of questions>
        """

        Ansoff_Matrix_question_prompt = """
        You are a professional business analyst.
        Now you are trying to create a Ansoff Matrix about ```{company}```.
        Propose 5 questions that might be useful for creating the Ansoff Matrix.
        Return them in the following JSON format:

        questions: <list of questions>        
        """

        Business_Canvas_question_prompt = """
        You are a professional business analyst.
        Now you are trying to create a Business Canvas about ```{company}```.
        Propose 10 questions that might be useful for creating the Business Canvas.
        Return them in the following JSON format:

        questions: <list of questions>     
        """

        Competitor_question_prompt = """
        You are a professional business analyst.
        Now you are trying to do a competitor analysis about ```{company}```.
        Propose 5 questions that might be useful for creating the competitor analysis.
        Return them in the following JSON format:

        questions: <list of questions>
        """

        Diligence_question_prompt = """
        You are a professional business analyst.
        Now you are trying to analyze the due diligence of ```{company}```.
        Propose 10 questions that might be useful for creating the due diligence analysis.
        Please focus the questions on the following topics: corporate finance, Legislation, Human rights, Civil litigation, and Criminal law.
        Return them in the following JSON format:

        questions: <list of questions>
        """

        if question_type == 'Introduction':
            question_proposing_template = HumanMessagePromptTemplate.from_template(Introduction_question_prompt)
        elif question_type == 'SWOT':
            question_proposing_template = HumanMessagePromptTemplate.from_template(SWOT_question_prompt)
        elif question_type == 'Porter':
            question_proposing_template = HumanMessagePromptTemplate.from_template(Five_Forces_question_prompt)
        elif question_type == 'Ansoff':
            question_proposing_template = HumanMessagePromptTemplate.from_template(Ansoff_Matrix_question_prompt)
        elif question_type == 'Canvas':
            question_proposing_template = HumanMessagePromptTemplate.from_template(Business_Canvas_question_prompt)
        elif question_type == 'Competitor':
            question_proposing_template = HumanMessagePromptTemplate.from_template(Competitor_question_prompt)
        elif question_type == 'Diligence':
            question_proposing_template = HumanMessagePromptTemplate.from_template(Diligence_question_prompt)

        chat_prompt = ChatPromptTemplate.from_messages(
            [question_proposing_template, MessagesPlaceholder(variable_name="agent_scratchpad")])
        agent = create_openai_functions_agent(self.llm, self.tools, chat_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        result = agent_executor.invoke({"company": company})['output']
        result_json = json.loads(result)
        return result_json['questions']

    def web_search(self, question):
        web_search_prompt = """
        You are a professional business analyst.
        Search for the answers in the Internet for the following question:
        ```{question}```
        You must return 3 most relevant website links and a short introduction of the website\
        in the exact format of a Python list of dictionaries:
        Introduction: <Short introduction of website>,
        URL: <Website url>
        Please do not return any text other than this Python list.
        """
        web_search_template = HumanMessagePromptTemplate.from_template(web_search_prompt)
        chat_prompt = ChatPromptTemplate.from_messages(
            [web_search_template, MessagesPlaceholder(variable_name="agent_scratchpad")])
        agent = create_openai_functions_agent(self.llm, self.tools, chat_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        result = agent_executor.invoke({"question": question})['output']
        result_list = json.loads(result)
        return result_list

    def web_scraping(self, url):
        headers = {
            'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
            }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
        else:
            text_content = "Unable to get information from the url."
            print(response.status_code)
        return text_content


def collect(company):
    questions = []
    content = []
    weblinks = []
    collector = information_collector()
    for question_type in collector.question_types:
        proposed_questions = collector.proposing_questions(question_type=question_type, company=company)
        questions += proposed_questions
    print(questions)
    for item in questions:
        weblinks += collector.web_search(question=item)
    print(weblinks)
    for weblink in weblinks:
        print(weblink['URL'])
        text_content = collector.web_scraping(url=weblink['URL'])
        content.append({'URL': weblink['URL'], 'text_content': text_content})
    with open("database.json", "w") as f:
        json.dump(content, f)
