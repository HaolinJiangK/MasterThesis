# MasterThesis
This application is for generating company analysis based on web search and RAG.

Collector.py collect the relevant information from the Internet and save it in a JSON file.

Embedding.py embeds the text into vector databases.

Analyze.py retrieves the most related information to the user queries and output analysis responses based on retrieval.

Generation.py generates the final PowerPoint.

Run code `streamlit run main.py` in the terminal to start the application.
