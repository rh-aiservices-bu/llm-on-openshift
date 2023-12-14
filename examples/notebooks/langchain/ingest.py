from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores.pgvector import PGVector
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

PDF_PATH = "pdf/RH342-RHEL8.4-en-3-20230209.pdf"

COLLECTION_NAME = "documents_test"
CONNECTION_STRING = "postgresql+psycopg://vectordb:vectordb@postgresql:5432/vectordb"

# Load PDF
loader = PyPDFLoader(PDF_PATH)
data = loader.load()
print(f"Loaded {PDF_PATH} file")

# Split in chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024,
                                               chunk_overlap=40)
all_splits = text_splitter.split_documents(data)

# Clean text
for doc in all_splits:
    doc.page_content = doc.page_content.replace('\x00', '')

print(f"Generated {len(all_splits)} splits")

embeddings = HuggingFaceEmbeddings()


store = PGVector(
    connection_string=CONNECTION_STRING,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings)

store.add_documents(all_splits)

print("Splits added to PGvector store")