#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
This helps catch import errors before deployment.
"""

import sys
import os

def test_imports():
    """Test all imports to ensure they work correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test main imports
        print("✅ Testing main.py imports...")
        from main import app
        print("✅ main.py imports successful")
        
        # Test route imports
        print("✅ Testing route imports...")
        from routes_pdf import router as pdf_router
        from routes_lists import router as lists_router
        from routes_calendar import router as calendar_router
        print("✅ Route imports successful")
        
        # Test utility imports
        print("✅ Testing utility imports...")
        from pdf import extract_text_from_pdf, chunk_text
        from rag import embed_text_chunks, store_embeddings, query_rag
        from firestore_utils import create_list, get_lists, update_list, delete_list
        print("✅ Utility imports successful")
        
        # Test FastAPI imports
        print("✅ Testing FastAPI imports...")
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        print("✅ FastAPI imports successful")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without external dependencies."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test PDF functions
        print("✅ Testing PDF functions...")
        from pdf import chunk_text
        test_text = "This is a test document with some content."
        chunks = chunk_text(test_text)
        assert len(chunks) > 0, "Chunking failed"
        print("✅ PDF functions work")
        
        # Test RAG functions
        print("✅ Testing RAG functions...")
        from rag import embed_text_chunks, query_rag
        embeddings = embed_text_chunks(["test chunk"])
        assert len(embeddings) > 0, "Embedding failed"
        
        result = query_rag("test query", "test_user")
        assert "answer" in result, "Query failed"
        print("✅ RAG functions work")
        
        print("\n🎉 Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Penny Assistant Backend Import Test")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test basic functionality
    functionality_ok = test_basic_functionality()
    
    if imports_ok and functionality_ok:
        print("\n🎉 All tests passed! Backend is ready for deployment.")
        return True
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 