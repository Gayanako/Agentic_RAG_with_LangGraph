from typing import Any, Dict
from src.workflow.chains.generation import gemini_generation_chain, perplexity_generation_chain
from src.workflow.chains.answer_validator import answer_validator
from src.workflow.state import GraphState
from langchain_core.messages import HumanMessage, AIMessage

def generate(state: GraphState) -> Dict[str, Any]:
    """Generate answers using both Gemini and Perplexity, then validate the best one."""
    print("---GENERATE WITH MULTI-LLM VALIDATION---")
    question = state["question"]
    documents = state.get("documents", [])
    messages = state.get("messages", [])
    retry_count = state.get("retry_count", 0)
    
    # Check if we've exceeded reasonable limits
    if retry_count > 3:
        print("---TOO MANY RETRIES, RETURNING FALLBACK ANSWER---")
        return {
            "documents": documents,
            "question": question,
            "generation": "I apologize, but I'm having trouble generating a reliable answer after multiple attempts. Please try rephrasing your question.",
            "messages": messages,
            "gemini_answer": "Fallback due to retry limit",
            "perplexity_answer": "Fallback due to retry limit",
            "validation_reasoning": "Maximum retry attempts exceeded",
            "chosen_model": "fallback"
        }
    
    history = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[-10:]])
    context = "\n\n".join([doc.page_content for doc in documents])
    
    print(f"---CONTEXT LENGTH: {len(context)} chars---")
    print(f"---DOCUMENTS COUNT: {len(documents)}---")
    print(f"---RETRY COUNT: {retry_count}---")
    
    # Generate answers from both models SEQUENTIALLY (more stable)
    print("---GENERATING WITH GEMINI---")
    try:
        gemini_answer = gemini_generation_chain.invoke({
            "context": context,
            "question": question,
            "history": history
        })
        print(f"---GEMINI SUCCESS: {len(gemini_answer)} chars---")
    except Exception as e:
        print(f"---GEMINI ERROR: {str(e)}---")
        gemini_answer = f"Error: {str(e)}"
    
    print("---GENERATING WITH PERPLEXITY---")
    try:
        perplexity_answer = perplexity_generation_chain.invoke({
            "context": context,
            "question": question,
            "history": history
        })
        print(f"---PERPLEXITY SUCCESS: {len(perplexity_answer)} chars---")
    except Exception as e:
        print(f"---PERPLEXITY ERROR: {str(e)}---")
        perplexity_answer = f"Error: {str(e)}"
    
    print(f"---GEMINI ANSWER: {gemini_answer}---")
    print(f"---PERPLEXITY ANSWER: {perplexity_answer}---")
    
    # Validate and select best answer
    print("---VALIDATING ANSWERS---")
    try:
        # Only validate if both answers are not errors
        if "Error:" not in gemini_answer and "Error:" not in perplexity_answer:
            validation_result = answer_validator.invoke({
                "question": question,
                "context": context,
                "gemini_answer": gemini_answer,
                "perplexity_answer": perplexity_answer
            })
            
            generation = validation_result.best_answer
            validation_reasoning = validation_result.reasoning
            chosen_model = validation_result.chosen_model
            print(f"---VALIDATION SUCCESS: Chose {chosen_model}---")
            
        else:
            # If one model failed, use the successful one
            if "Error:" not in gemini_answer:
                generation = gemini_answer
                chosen_model = "gemini"
                validation_reasoning = "Used Gemini answer (Perplexity failed)"
            elif "Error:" not in perplexity_answer:
                generation = perplexity_answer
                chosen_model = "perplexity" 
                validation_reasoning = "Used Perplexity answer (Gemini failed)"
            else:
                generation = "Both models failed to generate answers. Please try again."
                chosen_model = "error"
                validation_reasoning = "Both Gemini and Perplexity encountered errors"
            
            print(f"---USING FALLBACK: {chosen_model}---")
        
    except Exception as e:
        print(f"---VALIDATION ERROR: {str(e)}---")
        # Fallback: use the first successful answer
        if "Error:" not in gemini_answer:
            generation = gemini_answer
            chosen_model = "gemini"
        elif "Error:" not in perplexity_answer:
            generation = perplexity_answer
            chosen_model = "perplexity"
        else:
            generation = "I apologize, but I encountered an error while generating an answer. Please try again."
            chosen_model = "error"
        
        validation_reasoning = f"Validation failed: {str(e)}"
    
    # Update conversation history
    messages.append(HumanMessage(content=question))
    messages.append(AIMessage(content=generation))
    
    print(f"---FINAL GENERATION: {generation[:100]}...---")
    print(f"---CHOSEN MODEL: {chosen_model}---")
    
    return {
        "documents": documents,
        "question": question,
        "generation": generation,
        "messages": messages,
        "gemini_answer": gemini_answer,
        "perplexity_answer": perplexity_answer,
        "validation_reasoning": validation_reasoning,
        "chosen_model": chosen_model
    }