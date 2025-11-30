import os
import chromadb
import zipfile
import boto3
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

print("S3_BUCKET:", os.getenv("S3_BUCKET"))
print("AWS_ACCESS_KEY_ID:", os.getenv("AWS_ACCESS_KEY_ID"))
print("AWS_SECRET_ACCESS_KEY:", os.getenv("AWS_SECRET_ACCESS_KEY"))

S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = "chroma_joined_index.zip"
LOCAL_ZIP = "./chroma_joined_index_cloud.zip"
LOCAL_INDEX_PATH = "./chroma_joined_index_cloud"



# -----------------------
# Download Index from S3
# -----------------------
def download_index_if_needed():
    if os.path.exists(LOCAL_INDEX_PATH):
        print("📦 Local Chroma index already exists. Skipping download.")
        return
    
    print("⬇️ Downloading Chroma index from S3...")
    s3 = boto3.client("s3")
    s3.download_file(S3_BUCKET, S3_KEY, LOCAL_ZIP)

    print("📂 Extracting zip...")
    with zipfile.ZipFile(LOCAL_ZIP, 'r') as z:
        z.extractall(".")

    print("✅ Index ready.")

# -----------------------
# Initialization
# -----------------------
download_index_if_needed()

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_joined_index")

print("Collections in this index:")
for c in chroma_client.list_collections():
    print(c.name)

collection = chroma_client.get_collection("zameen_joined_index")
print("Collection loaded successfully:", collection.name)

# -----------------------
# Retrieval
# -----------------------
def retrieve(query: str, n_results: int = 5):
    print(f"\n🔍 Query: {query}")

    query_emb = model.encode([query])[0].tolist()

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=n_results
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    ids = results["ids"][0]

    for i in range(len(docs)):
        print("\n-----------------------------")
        print(f"Result {i+1}")
        print(f"ID: {ids[i]}")
        print(f"Location: {metas[i].get('location')}")
        print(f"Type: {metas[i].get('type')}")
        print(docs[i])

    return results


if __name__ == "__main__":
    while True:
        q = input("\nEnter query (exit to quit): ")
        if q.lower() == "exit":
            break
        retrieve(q)
