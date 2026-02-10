import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_keys():
    """Test if all API keys are loaded correctly"""
    print("🔑 Testing API Keys...")
    print("=" * 50)
    
    keys = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"), 
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")
    }
    
    all_loaded = True
    for key_name, key_value in keys.items():
        status = "✅ Loaded" if key_value else "❌ Missing"
        print(f"   {key_name}: {status}")
        if not key_value:
            all_loaded = False
    
    print("=" * 50)
    return all_loaded

def test_gemini():
    """Test Gemini model"""
    print("\n🤖 Testing Gemini Pro...")
    print("-" * 30)
    try:
        from src.models.model import get_gemini_model
        gemini = get_gemini_model()
        print("   ✅ Model initialized successfully")
        
        # Test simple response
        response = gemini.invoke("Hello! Reply with just 'GEMINI_WORKING' if you're working correctly.")
        print(f"   ✅ Response received: {response.content}")
        return True
        
    except Exception as e:
        print(f"   ❌ Gemini Error: {str(e)}")
        return False

def test_perplexity():
    """Test Perplexity Sonar model"""
    print("\n🔍 Testing Perplexity Sonar...")
    print("-" * 30)
    try:
        from src.models.model import get_perplexity_model
        perplexity = get_perplexity_model()
        print("   ✅ Model initialized successfully")
        
        # Test simple response
        response = perplexity.invoke("Hello! Reply with just 'PERPLEXITY_WORKING' if you're working correctly.")
        print(f"   ✅ Response received: {response.content}")
        return True
        
    except Exception as e:
        print(f"   ❌ Perplexity Error: {str(e)}")
        return False

def test_openai():
    """Test OpenAI GPT-4o-mini model"""
    print("\n🧠 Testing OpenAI GPT-4o-mini...")
    print("-" * 30)
    try:
        from src.models.model import get_openai_model
        openai = get_openai_model()
        print("   ✅ Model initialized successfully")
        
        # Test simple response
        response = openai.invoke("Hello! Reply with just 'OPENAI_WORKING' if you're working correctly.")
        print(f"   ✅ Response received: {response.content}")
        return True
        
    except Exception as e:
        print(f"   ❌ OpenAI Error: {str(e)}")
        return False

async def test_parallel_generation():
    """Test parallel generation with both models"""
    print("\n⚡ Testing Parallel Generation...")
    print("-" * 30)
    
    try:
        from src.workflow.chains.generation import gemini_generation_chain, perplexity_generation_chain
        
        test_question = "What are AI agents? Reply briefly in one sentence."
        test_context = "AI agents are autonomous systems that use LLMs for decision making."
        test_history = ""
        
        # Run both models in parallel
        tasks = [
            gemini_generation_chain.ainvoke({
                "context": test_context,
                "question": test_question,
                "history": test_history
            }),
            perplexity_generation_chain.ainvoke({
                "context": test_context,
                "question": test_question,
                "history": test_history
            })
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        gemini_success = not isinstance(results[0], Exception)
        perplexity_success = not isinstance(results[1], Exception)
        
        if gemini_success:
            print(f"   ✅ Gemini parallel response: {results[0][:100]}...")
        else:
            print(f"   ❌ Gemini parallel error: {str(results[0])}")
            
        if perplexity_success:
            print(f"   ✅ Perplexity parallel response: {results[1][:100]}...")
        else:
            print(f"   ❌ Perplexity parallel error: {str(results[1])}")
            
        return gemini_success and perplexity_success
        
    except Exception as e:
        print(f"   ❌ Parallel generation error: {str(e)}")
        return False

def test_validation():
    """Test the answer validation system"""
    print("\n🎯 Testing Answer Validation...")
    print("-" * 30)
    
    try:
        from src.workflow.chains.answer_validator import answer_validator
        
        test_data = {
            "question": "What are AI agents?",
            "context": "AI agents are autonomous systems that use LLMs for planning and decision making.",
            "gemini_answer": "AI agents are autonomous systems powered by LLMs that can make decisions and perform tasks independently.",
            "perplexity_answer": "AI agents are intelligent systems that use language models to operate autonomously and solve complex problems."
        }
        
        validation_result = answer_validator.invoke(test_data)
        
        print(f"   ✅ Validation successful!")
        print(f"   📊 Chosen model: {validation_result.chosen_model}")
        print(f"   💭 Reasoning: {validation_result.reasoning}")
        print(f"   🏆 Best answer: {validation_result.best_answer[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Validation error: {str(e)}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("\n📦 Testing Module Imports...")
    print("-" * 30)
    
    modules_to_test = [
        "src.models.model",
        "src.workflow.chains.generation", 
        "src.workflow.chains.answer_validator",
        "src.workflow.nodes.generate",
        "src.workflow.graph"
    ]
    
    all_imported = True
    for module_path in modules_to_test:
        try:
            __import__(module_path)
            print(f"   ✅ {module_path}")
        except ImportError as e:
            print(f"   ❌ {module_path}: {str(e)}")
            all_imported = False
    
    return all_imported

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting Comprehensive Model Test")
    print("=" * 60)
    
    test_results = {}
    
    # Test 1: API Keys
    test_results["api_keys"] = test_api_keys()
    
    if not test_results["api_keys"]:
        print("\n❌ Some API keys are missing. Please check your .env file!")
        return test_results
    
    # Test 2: Module Imports
    test_results["imports"] = test_imports()
    
    if not test_results["imports"]:
        print("\n❌ Some modules failed to import. Check your project structure!")
        return test_results
    
    # Test 3: Individual Models
    test_results["gemini"] = test_gemini()
    test_results["perplexity"] = test_perplexity() 
    test_results["openai"] = test_openai()
    
    # Test 4: Parallel Generation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    test_results["parallel"] = loop.run_until_complete(test_parallel_generation())
    loop.close()
    
    # Test 5: Validation System
    test_results["validation"] = test_validation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title():<20} {status}")
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    
    print("=" * 60)
    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED! ({passed_tests}/{total_tests})")
        print("🚀 Your system is ready to run!")
    else:
        print(f"⚠️  {passed_tests}/{total_tests} tests passed")
        print("🔧 Please check the errors above before running the main application.")
    
    return test_results

if __name__ == "__main__":
    run_comprehensive_test()