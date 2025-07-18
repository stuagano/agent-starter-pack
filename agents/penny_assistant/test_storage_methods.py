#!/usr/bin/env python3
"""
Test script to verify storage method reporting in Penny Assistant
"""

import json
import os
from pathlib import Path

def test_storage_methods():
    """Test different storage method configurations."""
    
    print("🧪 Testing Storage Method Reporting")
    print("===================================")
    print()
    
    # Test scenarios
    scenarios = [
        {
            "name": "No Services Configured",
            "config": {
                "firestore": {"configured": False},
                "calendar": {"configured": False},
                "vertex_ai": {"configured": False},
                "vector_search": {"configured": False},
                "project_id": None,
                "region": "us-central1"
            },
            "expected_storage": "Local JSON Storage",
            "expected_embedding": "Mock Embeddings"
        },
        {
            "name": "Vertex AI Only",
            "config": {
                "firestore": {"configured": False},
                "calendar": {"configured": False},
                "vertex_ai": {"configured": True, "embedding_model": "textembedding-gecko@001"},
                "vector_search": {"configured": False},
                "project_id": "test-project",
                "region": "us-central1"
            },
            "expected_storage": "Vertex AI Embeddings (Local Storage)",
            "expected_embedding": "Vertex AI (textembedding-gecko@001)"
        },
        {
            "name": "Full Vector Search",
            "config": {
                "firestore": {"configured": False},
                "calendar": {"configured": False},
                "vertex_ai": {"configured": True, "embedding_model": "textembedding-gecko@001"},
                "vector_search": {"configured": True, "index_name": "penny-assistant-index"},
                "project_id": "test-project",
                "region": "us-central1"
            },
            "expected_storage": "Vertex AI Vector Search (penny-assistant-index)",
            "expected_embedding": "Vertex AI (textembedding-gecko@001)"
        }
    ]
    
    for scenario in scenarios:
        print(f"📋 Testing: {scenario['name']}")
        print(f"   Expected Storage: {scenario['expected_storage']}")
        print(f"   Expected Embedding: {scenario['expected_embedding']}")
        
        # Create temporary config file
        config_file = Path("test_setup_status.json")
        with open(config_file, 'w') as f:
            json.dump(scenario['config'], f, indent=2)
        
        try:
            # Import and test the RAG system
            import sys
            sys.path.append('.')
            
            # Mock the config reader to use our test config
            from enhanced_rag import EnhancedRAG
            
            # Create RAG instance with test config
            rag = EnhancedRAG()
            
            # Test storage method
            actual_storage = rag.get_storage_method()
            actual_embedding = rag.get_embedding_method()
            
            print(f"   Actual Storage: {actual_storage}")
            print(f"   Actual Embedding: {actual_embedding}")
            
            # Check if results match expectations
            storage_match = actual_storage == scenario['expected_storage']
            embedding_match = actual_embedding == scenario['expected_embedding']
            
            if storage_match and embedding_match:
                print("   ✅ PASS")
            else:
                print("   ❌ FAIL")
                if not storage_match:
                    print(f"      Storage mismatch: expected '{scenario['expected_storage']}', got '{actual_storage}'")
                if not embedding_match:
                    print(f"      Embedding mismatch: expected '{scenario['expected_embedding']}', got '{actual_embedding}'")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        finally:
            # Clean up test config
            if config_file.exists():
                config_file.unlink()
        
        print()
    
    print("🎯 Storage Method Test Summary")
    print("==============================")
    print("The storage method should now show:")
    print("• 'Local JSON Storage' when no services are configured")
    print("• 'Vertex AI Embeddings (Local Storage)' when only Vertex AI is configured")
    print("• 'Vertex AI Vector Search (index-name)' when Vector Search is configured")
    print()
    print("The embedding method should show:")
    print("• 'Mock Embeddings' when no services are configured")
    print("• 'Vertex AI (model-name)' when Vertex AI is configured")
    print()

if __name__ == "__main__":
    test_storage_methods() 