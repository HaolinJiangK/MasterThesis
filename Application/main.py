import os
import Collector
import Embedding
import Analyze
import Generation
import streamlit as st

if __name__ == "__main__":
    st.title('Automated Company Analysis Tool')
    company = st.text_input("Please enter the company name:")
    os.environ['OPENAI_API_KEY'] = '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'
    os.environ['SERPER_API_KEY'] = ''
    if company:
        Collection_state = st.text('Web scraping...')
        Collector.collect(company)
        Collection_state.text('Web scraping finished.')
        Embedding_state = st.text('Creating vector database...')
        db = Embedding.embedd()
        Embedding_state.text('Vector database created.')
        Analysis_state = st.text('Analyzing the company...')
        Results = Analyze.analyzing(company, db=db)
        Analysis_state.text('Analysis created.')
        Generation_state = st.text('Generating PowerPoint...')
        Generation.generate_powerpoint(Results=Results, company_name=company)
        Generation_state.text('PowerPoint Created.')
        company = None

