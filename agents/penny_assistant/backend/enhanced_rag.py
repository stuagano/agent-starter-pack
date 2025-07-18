from typing import List, Dict, Any
import os
import json
from google.cloud import aiplatform
from google.cloud import aiplatform_v1
from config_reader import config_reader

class EnhancedRAG:
    def __init__(self):
        self.vertex_ai_configured = config_reader.is_service_configured("vertex_ai")
        self.vector_search_configured = config_reader.is_service_configured("vector_search")
        
        if self.vertex_ai_configured:
            self.initialize_vertex_ai()
        
        if self.vector_search_configured:
            self.initialize_vector_search()
    
    def initialize_vertex_ai(self):
        """Initialize Vertex AI client."""
        try:
            project_id = config_reader.get_project_id()
            location = config_reader.get_region()
            aiplatform.init(project=project_id, location=location)
            print("✅ Vertex AI initialized successfully")
        except Exception as e:
            print(f"⚠️  Vertex AI initialization failed: {e}")
            self.vertex_ai_configured = False
    
    def initialize_vector_search(self):
        """Initialize Vector Search client."""
        try:
            project_id = config_reader.get_project_id()
            location = config_reader.get_region()
            
            # Initialize Vector Search client
            self.vector_search_client = aiplatform_v1.MatchServiceClient(
                client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
            )
            
            # Get index endpoint
            index_name = config_reader.get_service_config("vector_search").get("index_name", "penny-assistant-index")
            self.index_endpoint = f"projects/{project_id}/locations/{location}/indexEndpoints/{index_name}"
            
            print("✅ Vector Search initialized successfully")
        except Exception as e:
            print(f"⚠️  Vector Search initialization failed: {e}")
            self.vector_search_configured = False
    
    def get_storage_method(self) -> str:
        """Get the current storage method being used."""
        if self.vector_search_configured:
            index_name = config_reader.get_service_config("vector_search").get("index_name", "penny-assistant-index")
            return f"Vertex AI Vector Search ({index_name})"
        elif self.vertex_ai_configured:
            return "Vertex AI Embeddings (Local Storage)"
        else:
            return "Local JSON Storage"
    
    def get_embedding_method(self) -> str:
        """Get the current embedding method being used."""
        if self.vertex_ai_configured:
            model_name = config_reader.get_service_config("vertex_ai").get("embedding_model", "textembedding-gecko@001")
            return f"Vertex AI ({model_name})"
        else:
            return "Mock Embeddings"
    
    def embed_text_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """Embed text chunks using Vertex AI or placeholder."""
        if self.vertex_ai_configured:
            return self._embed_with_vertex_ai(chunks)
        else:
            return self._embed_placeholder(chunks)
    
    def _embed_with_vertex_ai(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """Embed text chunks using Vertex AI."""
        try:
            from vertexai.language_models import TextEmbeddingModel
            
            model_name = config_reader.get_service_config("vertex_ai").get("embedding_model", "textembedding-gecko@001")
            model = TextEmbeddingModel.from_pretrained(model_name)
            embeddings = model.get_embeddings(chunks)
            
            result = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                result.append({
                    "id": f"embedding_{i}",
                    "embedding": embedding.values,
                    "text": chunk
                })
            return result
        except Exception as e:
            print(f"⚠️  Vertex AI embedding failed, using placeholder: {e}")
            return self._embed_placeholder(chunks)
    
    def _embed_placeholder(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """Generate placeholder embeddings."""
        embeddings = []
        for i, chunk in enumerate(chunks):
            embeddings.append({
                "id": f"embedding_{i}",
                "embedding": [0.1] * 768,  # Placeholder 768-dimensional embedding
                "text": chunk
            })
        return embeddings
    
    def store_embeddings(self, embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]]):
        """Store embeddings in Vector Search or placeholder storage."""
        if self.vector_search_configured:
            return self._store_in_vector_search(embeddings, metadata)
        else:
            return self._store_placeholder(embeddings, metadata)
    
    def _store_in_vector_search(self, embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]]):
        """Store embeddings in Vertex AI Vector Search."""
        try:
            from google.cloud.aiplatform_v1.types import IndexDatapoint, UpsertDatapointsRequest
            
            # Prepare datapoints for Vector Search
            datapoints = []
            for i, (embedding, meta) in enumerate(zip(embeddings, metadata)):
                datapoint = IndexDatapoint(
                    datapoint_id=f"{meta.get('source', 'unknown')}_{i}",
                    feature_vector=embedding["embedding"],
                    restricts=[
                        {"namespace": "user_id", "allow_list": [meta.get('user_id', 'demo-user')]},
                        {"namespace": "source", "allow_list": [meta.get('source', 'unknown')]}
                    ]
                )
                datapoints.append(datapoint)
            
            # Create upsert request
            request = UpsertDatapointsRequest(
                index_endpoint=self.index_endpoint,
                datapoints=datapoints
            )
            
            # Upsert datapoints
            operation = self.vector_search_client.upsert_datapoints(request=request)
            operation.result()  # Wait for completion
            
            index_name = config_reader.get_service_config("vector_search").get("index_name", "penny-assistant-index")
            print(f"✅ Stored {len(embeddings)} embeddings in Vector Search index: {index_name}")
            
            return {
                "stored_count": len(embeddings), 
                "storage": "vector_search", 
                "storage_method": f"Vertex AI Vector Search ({index_name})",
                "index": index_name
            }
        except Exception as e:
            print(f"⚠️  Vector Search storage failed, using placeholder: {e}")
            return self._store_placeholder(embeddings, metadata)
    
    def _store_placeholder(self, embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]]):
        """Store embeddings in placeholder storage."""
        storage_method = self.get_storage_method()
        print(f"Storing {len(embeddings)} embeddings in {storage_method}")
        
        # Store in local JSON file for persistence
        try:
            storage_file = "pdf_embeddings.json"
            existing_data = []
            
            if os.path.exists(storage_file):
                try:
                    with open(storage_file, 'r') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = []
            
            # Add new embeddings
            for i, (embedding, meta) in enumerate(zip(embeddings, metadata)):
                existing_data.append({
                    "id": embedding["id"],
                    "embedding": embedding["embedding"],
                    "text": embedding["text"],
                    "metadata": meta,
                    "timestamp": "2024-01-01T00:00:00Z"  # Placeholder timestamp
                })
            
            # Save to file
            with open(storage_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return {
                "stored_count": len(embeddings), 
                "storage": "local_json",
                "storage_method": storage_method,
                "file": storage_file
            }
        except Exception as e:
            print(f"⚠️  Local storage failed: {e}")
            return {
                "stored_count": len(embeddings), 
                "storage": "memory",
                "storage_method": "In-Memory Storage (Temporary)"
            }
    
    def query_rag(self, user_query: str, user_id: str) -> Dict[str, Any]:
        """Query RAG system using Vector Search or placeholder."""
        if self.vector_search_configured:
            return self._query_vector_search(user_query, user_id)
        else:
            return self._query_placeholder(user_query, user_id)
    
    def _query_vector_search(self, user_query: str, user_id: str) -> Dict[str, Any]:
        """Query Vector Search for relevant documents."""
        try:
            # First, embed the query
            query_embedding = self._embed_with_vertex_ai([user_query])[0]
            
            # Create find neighbors request
            from google.cloud.aiplatform_v1.types import FindNeighborsRequest, FindNeighborsResponse
            
            request = FindNeighborsRequest(
                index_endpoint=self.index_endpoint,
                deployed_index_id="deployed_index_0",  # Default deployed index
                queries=[
                    {
                        "datapoint": {
                            "datapoint_id": "query",
                            "feature_vector": query_embedding["embedding"]
                        },
                        "neighbor_count": 5
                    }
                ],
                return_full_datapoint=True
            )
            
            # Find neighbors
            response = self.vector_search_client.find_neighbors(request=request)
            
            # Extract results
            neighbors = response.nearest_neighbors[0].neighbors
            context = []
            sources = []
            
            for neighbor in neighbors:
                if hasattr(neighbor, 'datapoint') and neighbor.datapoint:
                    # Extract text from datapoint metadata or use a placeholder
                    text = getattr(neighbor.datapoint, 'text', f"Document chunk with score {neighbor.distance}")
                    context.append(text)
                    
                    # Extract source from restricts
                    source = "unknown"
                    if hasattr(neighbor.datapoint, 'restricts'):
                        for restrict in neighbor.datapoint.restricts:
                            if restrict.namespace == "source" and restrict.allow_list:
                                source = restrict.allow_list[0]
                                break
                    sources.append(source)
            
            # Generate answer using context
            answer = self._generate_answer_from_context(user_query, context)
            
            index_name = config_reader.get_service_config("vector_search").get("index_name", "penny-assistant-index")
            return {
                "answer": answer,
                "context": context,
                "sources": list(set(sources)),  # Remove duplicates
                "method": "vector_search",
                "storage_method": f"Vertex AI Vector Search ({index_name})",
                "index": index_name,
                "neighbors_found": len(neighbors)
            }
        except Exception as e:
            print(f"⚠️  Vector Search query failed, using placeholder: {e}")
            return self._query_placeholder(user_query, user_id)
    
    def _generate_answer_from_context(self, query: str, context: List[str]) -> str:
        """Generate an answer from the retrieved context."""
        if not context:
            return f"I couldn't find relevant information for: {query}"
        
        # Simple answer generation - in a real implementation, you'd use an LLM
        context_text = " ".join(context[:3])  # Use first 3 context pieces
        return f"Based on the documents, here's what I found about '{query}': {context_text[:200]}..."
    
    def _query_placeholder(self, user_query: str, user_id: str) -> Dict[str, Any]:
        """Generate placeholder RAG response."""
        storage_method = self.get_storage_method()
        return {
            "answer": f"[Placeholder RAG answer for: {user_query}]",
            "context": ["Sample context 1", "Sample context 2"],
            "sources": ["document1.pdf", "document2.pdf"],
            "method": "local_search",
            "storage_method": storage_method
        }
    
    def search_embeddings(self, query: str, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar embeddings."""
        if self.vector_search_configured:
            return self._search_vector_search(query, user_id, limit)
        else:
            return self._search_placeholder(query, user_id, limit)
    
    def _search_vector_search(self, query: str, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Vector Search index."""
        try:
            # Embed the query
            query_embedding = self._embed_with_vertex_ai([query])[0]
            
            # Create find neighbors request
            from google.cloud.aiplatform_v1.types import FindNeighborsRequest
            
            request = FindNeighborsRequest(
                index_endpoint=self.index_endpoint,
                deployed_index_id="deployed_index_0",
                queries=[
                    {
                        "datapoint": {
                            "datapoint_id": "query",
                            "feature_vector": query_embedding["embedding"]
                        },
                        "neighbor_count": limit
                    }
                ],
                return_full_datapoint=True
            )
            
            # Find neighbors
            response = self.vector_search_client.find_neighbors(request=request)
            
            # Format results
            results = []
            for neighbor in response.nearest_neighbors[0].neighbors:
                text = getattr(neighbor.datapoint, 'text', f"Document chunk with score {neighbor.distance}")
                source = "unknown"
                if hasattr(neighbor.datapoint, 'restricts'):
                    for restrict in neighbor.datapoint.restricts:
                        if restrict.namespace == "source" and restrict.allow_list:
                            source = restrict.allow_list[0]
                            break
                
                results.append({
                    "text": text,
                    "score": 1.0 - neighbor.distance,  # Convert distance to similarity score
                    "metadata": {"source": source}
                })
            
            return results
        except Exception as e:
            print(f"⚠️  Vector Search failed, using placeholder: {e}")
            return self._search_placeholder(query, user_id, limit)
    
    def _search_placeholder(self, query: str, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Generate placeholder search results."""
        return [
            {
                "text": f"Placeholder result {i} for query: {query}",
                "score": 0.9 - (i * 0.1),
                "metadata": {"source": f"document{i}.pdf"}
            }
            for i in range(min(limit, 3))
        ]

# Global instance
rag_system = EnhancedRAG()

# Convenience functions
def embed_text_chunks(chunks: List[str]) -> List[Dict[str, Any]]:
    return rag_system.embed_text_chunks(chunks)

def store_embeddings(embeddings: List[Dict[str, Any]], metadata: List[Dict[str, Any]]):
    return rag_system.store_embeddings(embeddings, metadata)

def query_rag(user_query: str, user_id: str) -> Dict[str, Any]:
    return rag_system.query_rag(user_query, user_id)

def search_embeddings(query: str, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    return rag_system.search_embeddings(query, user_id, limit) 