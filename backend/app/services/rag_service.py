import chromadb
from chromadb.config import Settings
\n# Configuration for ChromaDB
chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chroma_db"))
\nclass RagService:
    def __init__(self):
        self.collection = chroma_client.create_collection("buet_exam_questions")
\n    def add_question(self, question_text, vector):
        # Add a question with its corresponding vector to the collection
        self.collection.add([question_text], [vector])
\n    def query(self, query_vector, n_results=5):
        # Perform a vector search for the most relevant questions
        results = self.collection.query(query_vector, n_results=n_results)
        return results
\n    def retrieve_all_questions(self):
        # Retrieve all questions stored in the collection
        return self.collection.get_all()  
