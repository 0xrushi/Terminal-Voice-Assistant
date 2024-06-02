import chromadb
import subprocess
import os
import logging
from dotenv import load_dotenv
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv() 

# not using this right now for further cleaning
def get_zsh_history():
    """
    Return zsh shell history
    """
    history_file = os.path.expanduser('~/.zsh_history')
    result = subprocess.run(['cat', history_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode == 0:
        return result.stdout
    else:
        print(f"Error: {result.stderr}")
        return None

chroma_client = chromadb.PersistentClient(path="./chromadbpath")
collection_name = "my_collection"

existing_collections = [i.name for i in chroma_client.list_collections()]
if collection_name in existing_collections:
    collection = chroma_client.get_collection(name=collection_name)
else:
    collection = chroma_client.create_collection(name=collection_name)

    f = open("src/utils/chrmadb/abc.txt", "r")
    text = f.read()

    lines = text.strip().split('\n')
    # documents = list(set([line.split(maxsplit=1)[1] for line in lines if len(line)> 5]))
    df=pd.DataFrame({'line': lines})
    documents = list(df['line'].str.split(n=1, expand=True).dropna()[1].unique())

    collection.upsert(
        documents=documents,
        ids=[str(i) for i in range(len(documents))]
    )

def get_relevant_history(query="ssh to doraemon"):
    results = collection.query(
        query_texts=[query],
        n_results=2
    )
    relevant_history = '\n'.join(results['documents'][0])
    logger.info(f"Retrieved relevant history: {relevant_history}\n")
    return relevant_history

# print(get_relevant_history(query="Ssh Doraemon"))