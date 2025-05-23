"""
Test script to verify that the querying functionality works correctly
after fixing the LlamaIndex API issues.
"""

import os
from dotenv import load_dotenv
from utils.constants import IndexModel
from utils.index import indexUtils

# Load environment variables
load_dotenv()

def test_query_functionality():
    """Test the RAG query functionality"""
    print("🧪 Testing query functionality...")
    
    # Sample content for testing
    test_content = """
    # Sample Article
    
    Artificial Intelligence (AI) is a rapidly growing field that focuses on creating 
    machines capable of performing tasks that typically require human intelligence. 
    These tasks include learning, reasoning, perception, and language understanding.
    
    Machine Learning is a subset of AI that enables computers to learn and improve 
    from experience without being explicitly programmed. It uses algorithms to 
    identify patterns in data and make predictions or decisions.
    
    Deep Learning is a specialized form of machine learning that uses neural networks 
    with multiple layers to model and understand complex patterns. It has been 
    particularly successful in areas like image recognition and natural language processing.
    """
    
    test_query = "What is the relationship between AI, Machine Learning, and Deep Learning?"
    model = "gpt-4o-mini"
    
    try:
        print(f"📝 Creating RAG index with content length: {len(test_content)} characters")
        
        # Test the index creation
        index = indexUtils.create_rag_index(test_content, model, IndexModel.VECTOR_STORE)
        
        if index is None:
            print("❌ Failed to create RAG index")
            return False
            
        print("✅ RAG index created successfully")
        
        # Test the query engine
        print(f"🔍 Testing query: {test_query}")
        
        system_prompt = """
        You need to write your answer in MarkDown format.
        You can link and highlight parts of the article using MarkDown links like: [Source](#highlight=Exact%20Text%20from%20the%20content)
        Do not use '-' for spaces, use '%20' instead, and refer to the content using exact words from the content.
        Link and highlight each part of the content that informs your answer.
        """
        
        query_engine = index.as_query_engine(
            system_prompt=system_prompt
        )
        
        response = query_engine.query(test_query)
        
        print("✅ Query executed successfully")
        print(f"📄 Response: {str(response)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during query test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test"""
    print("🚀 Testing Query Functionality Fixes")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key not found in environment variables")
        return
    
    success = test_query_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Query functionality is working correctly.")
    else:
        print("❌ Tests failed. There are still issues with the query functionality.")

if __name__ == "__main__":
    main()
