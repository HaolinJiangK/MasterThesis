import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


class DatabaseCreator():
    def __init__(self):
        self.recursive_text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ",", "."],
            chunk_size=1000,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False,
        )

    def chunking(self, text=None, splitter='recursive'):
        seen = set()
        data = []
        for d in text:
            dict_tuple = tuple(sorted(d.items()))
            if dict_tuple not in seen:
                seen.add(dict_tuple)
                data.append(d)
        original_texts = []
        for item in data:
            original_texts.append(item['text_content'])
        if splitter == 'recursive':
            text_splitter = self.recursive_text_splitter
        split_texts = text_splitter.create_documents(original_texts)
        return split_texts

    def embedding(self, split_text=None, model='OpenAI'):
        if model == 'OpenAI':
            embedding_function = OpenAIEmbeddings()
        db = Chroma.from_documents(split_text, embedding_function)
        return db

    def loading(self, model='OpenAI', directory='./database'):
        if model == 'OpenAI':
            embedding_function = OpenAIEmbeddings()
        db = Chroma(persist_directory=directory, embedding_function=embedding_function)
        return db

def embedd():
    with open('database.json') as f:
        list = json.load(f)
    dbCreator = DatabaseCreator()
    chunked_text = dbCreator.chunking(list, splitter='recursive')
    db = dbCreator.embedding(split_text=chunked_text, model='OpenAI')
    return db