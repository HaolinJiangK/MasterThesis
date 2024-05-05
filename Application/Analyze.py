from langchain_community.vectorstores import Chroma
from langchain.prompts import HumanMessagePromptTemplate
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from typing import List
from langchain_core.pydantic_v1 import BaseModel, Field
import json
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent
import os
import ast


class BusinessAnalyzer():
    def __init__(self):
        self.embedding_function_openai = OpenAIEmbeddings()
        self.analysis_type = ['Introduction', 'SWOT', 'Porter', 'Ansoff', 'Canvas', 'Competitor', 'Diligence']
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.0)

    def load_db(self):
        directory = './database'
        db = Chroma(persist_directory=directory, embedding_function=OpenAIEmbeddings())
        return db

    def analyze(self, database=None, k=5, retrieve_type=None, company=None):
        retriever = database.as_retriever()
        retriever_tool = create_retriever_tool(retriever,
                                               "company-information-retriever",
                                               "Query a retriever to get any information about the company",
                                               )
        tools = [retriever_tool]
        Introduction_retriever_prompt = """
        You are a professional business analyst.

        Your task is to create a brief introduction of {company}.

        First, propose several questions that might be useful for the introduction.

        Second, use the company-information-retriever to query the vector database with these questions.

        At last, create the introduction based on the retrieved results.
        Return the final analysis in a dictionary format as following:
        <Company Name>:
        <Sector>:
        <Industry>:
        <Country>:
        <City>:
        <Number of employees>:
        <Website>:
        <Overall Introduction>:

        Please only return the final introduction. Do not give any introduction, or description of data format.

        Do not make things up.
        """
        SWOT_retriever_prompt = """
        You are a professional business analyst.

        Your task is to create a SWOT analysis of {company}.

        First, propose several questions that might be useful for the SWOT analysis.

        Second, use the company-information-retriever to query the vector database with these questions.

        At last, create the SWOT analysis based on the retrieved results.
        You must return the final analysis in a dictionary format as following:
        <Strengths>:
        <Weaknesses>:
        <Opportunities>:
        <Threats>:
        If there are more than one key point in one category, do not use any list in the analysis, but use number.
        Please only return the final analysis. Do not give any introduction, or description of data format.

        Do not make things up.
        """
        Porter_retriever_prompt = """
        You are a professional business analyst.

        Your task is to create a Porter Five Forces analysis of {company}.

        First, propose several questions that might be useful for the Porter Five Forces analysis.

        Second, use the company-information-retriever to query the vector database with these questions.

        At last, create the Porter Five Forces analysis based on the retrieved results.

        Return the final analysis in a dictionary format as following:
        <Intensity of Competitive Rivalry>:
        <Bargaining Power of Suppliers>:
        <Bargaining Power of Buyers>:
        <Threats of New Entrants>:
        <Threats of Substitute Products>:

        Please only return the final analysis. Do not give any introduction, or description of data format.

        Do not make things up.
        """
        Ansoff_retriever_prompt = """
        You are a professional business analyst.

        Your task is to create a Ansoff Matrix analysis of {company}.

        First, propose several questions that might be useful for the Ansoff Matrix analysis.

        Second, use the company-information-retriever to query the vector database with these questions.

        At last, create the detailed Ansoff Matrix analysis based on the retrieved results.

        Return the final analysis in a dictionary format as following:
        <Market Penetration>:
        <Product Development>:
        <Market Development>:
        <Diversification>:

        Please only return the final analysis. Do not give any introduction, or description of data format.

        Do not make things up.
        """
        Canvas_retriever_prompt = """
        You are a professional business analyst.

        Your task is to create a Business Canvas analysis of {company}.

        First, propose several questions that might be useful for the Business Canvas analysis.

        Second, use the company-information-retriever to query the vector database with these questions.

        At last, create the detailed Business Canvas analysis based on the retrieved results.

        Return the final analysis in a dictionary format as following:
        <Key Partners>:
        <Key Activities>:
        <Key Resources>:
        <Value Proposition>:
        <Customer Relationships>:
        <Channels>:
        <Customer Segments>:
        <Cost Structure>:
        <Revenue Stream>:

        Please only return the final analysis. Do not give any introduction, or description of data format.

        Do not make things up.
        """
        Competitor_retriever_prompt = """
        You are a professional business analyst.

        Your task is to create a competitor analysis of {company}.

        First, propose several questions that might be useful for the competitor analysis.

        Second, use the company-information-retriever to query the vector database with these questions.

        At last, create the competitor analysis based on the retrieved results.

        Please only return the final analysis.

        Do not make things up.
        """
        Diligence_retriever_prompt = """
        You are a professional business analyst.

        Your task is to create a Due Diligence analysis of {company}.

        First, propose several questions that might be useful for the Due Diligence analysis.

        Second, use the company-information-retriever to query the vector database with these questions.

        At last, create the Due Diligence analysis based on the retrieved results.

        Please only return the final analysis.

        Do not make things up.
        """
        if retrieve_type == 'Introduction':
            retriever_template = HumanMessagePromptTemplate.from_template(Introduction_retriever_prompt)
        elif retrieve_type == 'SWOT':
            retriever_template = HumanMessagePromptTemplate.from_template(SWOT_retriever_prompt)
        elif retrieve_type == 'Porter':
            retriever_template = HumanMessagePromptTemplate.from_template(Porter_retriever_prompt)
        elif retrieve_type == 'Ansoff':
            retriever_template = HumanMessagePromptTemplate.from_template(Ansoff_retriever_prompt)
        elif retrieve_type == 'Canvas':
            retriever_template = HumanMessagePromptTemplate.from_template(Canvas_retriever_prompt)
        elif retrieve_type == 'Competitor':
            retriever_template = HumanMessagePromptTemplate.from_template(Competitor_retriever_prompt)
        elif retrieve_type == 'Diligence':
            retriever_template = HumanMessagePromptTemplate.from_template(Diligence_retriever_prompt)
        chat_prompt = ChatPromptTemplate.from_messages(
            [retriever_template, MessagesPlaceholder(variable_name="agent_scratchpad")])
        agent = create_openai_functions_agent(self.llm, tools, chat_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        result = agent_executor.invoke({"company": company})['output']
        return result


def analyzing(company=None, k=5, db=None):
    Analyzer = BusinessAnalyzer()
    Results = []
    for item in Analyzer.analysis_type:
        result = Analyzer.analyze(database=db, k=5, retrieve_type=item, company=company)
        Results.append({item: result})
    return Results