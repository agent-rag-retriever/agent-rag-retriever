import os
import chromadb
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

class RAGRetriever:
    def __init__(self, target_repo_path: str):
        self.target_repo_path = target_repo_path
        
        # Initialize a local, persistent Vector DB in your directory
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create or fetch a collection for your codebase vectors
        self.collection = self.chroma_client.get_or_create_collection(name="codebase_index")
        
        # Index the repository immediately on startup
        self.index_codebase()

    def index_codebase(self):
        """Scans the repository, chunks code files, and stores them in the Vector DB."""
        print("[Agent 2] Scanning and indexing codebase into Vector DB...")
        
        # Use a code-aware splitter so functions don't get awkwardly split in half
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.JS, chunk_size=1000, chunk_overlap=200
        )

        for root, dirs, files in os.walk(self.target_repo_path):
            # Ignore hidden folders like .git or node_modules
            if any(ignored in root for ignored in [".git", "node_modules", "chroma_db"]):
                continue
                
            for file in files:
                if file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py')):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.target_repo_path)
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            code_content = f.read()
                        
                        # Chunk the code file
                        chunks = splitter.split_text(code_content)
                        
                        # Store chunks into ChromaDB
                        for idx, chunk in enumerate(chunks):
                            self.collection.upsert(
                                documents=[chunk],
                                metadatas=[{"file_path": relative_path}],
                                ids=[f"{relative_path}_chunk_{idx}"]
                            )
                    except Exception as e:
                        print(f"Skipping indexing for {file} due to error: {e}")
        print(f"[Agent 2] Indexing complete. Total chunks stored: {self.collection.count()}")

    def get_context(self, error_message: str, parsed_file: str = None, parsed_line: int = None) -> dict:
        """Main routing engine: Decides between Local Fallback or Vector Search."""
        if parsed_file and parsed_line:
            full_path = os.path.join(self.target_repo_path, parsed_file)
            if os.path.exists(full_path):
                print(f"[Agent 2] Precise error located. Executing Local Fallback for: {parsed_file}")
                return self._extract_local_context(full_path, parsed_line)
        
        print(f"[Agent 2] Vague error. Executing Vector Semantic Search...")
        return self._vector_semantic_search(error_message)

    def _extract_local_context(self, file_path: str, line_number: int, window_size: int = 30) -> dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            total_lines = len(lines)
            target_idx = line_number - 1 
            
            start_idx = max(0, target_idx - window_size)
            end_idx = min(total_lines, target_idx + window_size + 1)
            
            return {
                "status": "success",
                "retrieval_method": "local_fallback",
                "file_path": file_path,
                "target_line": line_number,
                "context_window": "".join(lines[start_idx:end_idx])
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _vector_semantic_search(self, query: str) -> dict:
        """Queries ChromaDB to find the code snippet most semantically related to the error."""
        # ChromaDB automatically handles basic text-embedding conversion locally out-of-the-box
        results = self.collection.query(
            query_texts=[query],
            n_results=1
        )
        
        if results['documents'] and results['documents'][0]:
            matched_code = results['documents'][0][0]
            matched_file = results['metadatas'][0][0]['file_path']
            
            return {
                "status": "success",
                "retrieval_method": "vector_db",
                "inferred_file": matched_file,
                "context_window": matched_code
            }
        
        return {
            "status": "error",
            "message": "No matching code context found in Vector DB."
        }

# ==========================================
# TEST INTEGRATION
# ==========================================
if __name__ == "__main__":
    # Setup our mock repository with a hidden bug
    os.makedirs("mock_repo/src/utils", exist_ok=True)
    
    # Write a file containing a clear authentication loop error
    with open("mock_repo/src/utils/auth.js", "w") as f:
        f.write("// User authentication controller\n")
        f.write("function loginUser(req, res) {\n")
        f.write("    // BUG: Entering an endless recursive loop if session fails\n")
        f.write("    if (!req.session) {\n")
        f.write("        return loginUser(req, res);\n") 
        f.write("    }\n")
        f.write("}\n")

    # Initialize retriever (which triggers indexing)
    retriever = RAGRetriever(target_repo_path="./mock_repo")

    # Scenario B Test: Vague error message containing no file names or line numbers!
    print("\n--- Running Upgraded Scenario B (Vague Log) ---")
    result_vague = retriever.get_context(
        error_message="Maximum call stack size exceeded in authentication routine loops"
    )
    print(f"Retrieved via: {result_vague['retrieval_method']}")
    print(f"Inferred File Location: {result_vague.get('inferred_file')}")
    print(f"Extracted Context:\n{result_vague['context_window']}")