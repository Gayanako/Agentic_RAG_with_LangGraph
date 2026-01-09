# from typing import Any, Dict
# from src.workflow.chains.generation import gemini_generation_chain, perplexity_generation_chain
# from src.workflow.chains.answer_validator import answer_validator
# from src.workflow.state import GraphState
# from langchain_core.messages import HumanMessage, AIMessage

# def generate(state: GraphState) -> Dict[str, Any]:
#     """Generate answers using both Gemini and Perplexity, then validate the best one."""
#     print("---GENERATE WITH MULTI-LLM VALIDATION---")
#     question = state["question"]
#     documents = state.get("documents", [])
#     messages = state.get("messages", [])
#     retry_count = state.get("retry_count", 0)
    
#     # Check if we've exceeded reasonable limits
#     if retry_count > 3:
#         print("---TOO MANY RETRIES, RETURNING FALLBACK ANSWER---")
#         return {
#             "documents": documents,
#             "question": question,
#             "generation": "I apologize, but I'm having trouble generating a reliable answer after multiple attempts. Please try rephrasing your question.",
#             "messages": messages,
#             "gemini_answer": "Fallback due to retry limit",
#             "perplexity_answer": "Fallback due to retry limit",
#             "validation_reasoning": "Maximum retry attempts exceeded",
#             "chosen_model": "fallback"
#         }
    
#     history = "\n".join([f"{msg.type}: {msg.content}" for msg in messages[-10:]])
#     context = "\n\n".join([doc.page_content for doc in documents])
    
#     print(f"---CONTEXT LENGTH: {len(context)} chars---")
#     print(f"---DOCUMENTS COUNT: {len(documents)}---")
#     print(f"---RETRY COUNT: {retry_count}---")
    
#     # Generate answers from both models SEQUENTIALLY (more stable)
#     print("---GENERATING WITH GEMINI---")
#     try:
#         gemini_answer = gemini_generation_chain.invoke({
#             "context": context,
#             "question": question,
#             "history": history
#         })
#         print(f"---GEMINI SUCCESS: {len(gemini_answer)} chars---")
#     except Exception as e:
#         print(f"---GEMINI ERROR: {str(e)}---")
#         gemini_answer = f"Error: {str(e)}"
    
#     print("---GENERATING WITH PERPLEXITY---")
#     try:
#         perplexity_answer = perplexity_generation_chain.invoke({
#             "context": context,
#             "question": question,
#             "history": history
#         })
#         print(f"---PERPLEXITY SUCCESS: {len(perplexity_answer)} chars---")
#     except Exception as e:
#         print(f"---PERPLEXITY ERROR: {str(e)}---")
#         perplexity_answer = f"Error: {str(e)}"
    
#     print(f"---GEMINI ANSWER: {gemini_answer}---")
#     print(f"---PERPLEXITY ANSWER: {perplexity_answer}---")
    
#     # Validate and select best answer
#     print("---VALIDATING ANSWERS---")
#     try:
#         # Only validate if both answers are not errors
#         if "Error:" not in gemini_answer and "Error:" not in perplexity_answer:
#             validation_result = answer_validator.invoke({
#                 "question": question,
#                 "context": context,
#                 "gemini_answer": gemini_answer,
#                 "perplexity_answer": perplexity_answer
#             })
            
#             generation = validation_result.best_answer
#             validation_reasoning = validation_result.reasoning
#             chosen_model = validation_result.chosen_model
#             print(f"---VALIDATION SUCCESS: Chose {chosen_model}---")
            
#         else:
#             # If one model failed, use the successful one
#             if "Error:" not in gemini_answer:
#                 generation = gemini_answer
#                 chosen_model = "gemini"
#                 validation_reasoning = "Used Gemini answer (Perplexity failed)"
#             elif "Error:" not in perplexity_answer:
#                 generation = perplexity_answer
#                 chosen_model = "perplexity" 
#                 validation_reasoning = "Used Perplexity answer (Gemini failed)"
#             else:
#                 generation = "Both models failed to generate answers. Please try again."
#                 chosen_model = "error"
#                 validation_reasoning = "Both Gemini and Perplexity encountered errors"
            
#             print(f"---USING FALLBACK: {chosen_model}---")
        
#     except Exception as e:
#         print(f"---VALIDATION ERROR: {str(e)}---")
#         # Fallback: use the first successful answer
#         if "Error:" not in gemini_answer:
#             generation = gemini_answer
#             chosen_model = "gemini"
#         elif "Error:" not in perplexity_answer:
#             generation = perplexity_answer
#             chosen_model = "perplexity"
#         else:
#             generation = "I apologize, but I encountered an error while generating an answer. Please try again."
#             chosen_model = "error"
        
#         validation_reasoning = f"Validation failed: {str(e)}"
    
#     # Update conversation history
#     messages.append(HumanMessage(content=question))
#     messages.append(AIMessage(content=generation))
    
#     print(f"---FINAL GENERATION: {generation[:100]}...---")
#     print(f"---CHOSEN MODEL: {chosen_model}---")
    
#     return {
#         "documents": documents,
#         "question": question,
#         "generation": generation,
#         "messages": messages,
#         "gemini_answer": gemini_answer,
#         "perplexity_answer": perplexity_answer,
#         "validation_reasoning": validation_reasoning,
#         "chosen_model": chosen_model
#     }

# from typing import Any, Dict
# from langchain_core.messages import HumanMessage, AIMessage

# from src.workflow.chains.generation import gemini_generation_chain, perplexity_generation_chain
# from src.workflow.state import GraphState

# # NEW IMPORTS (metrics-based evaluator)
# from src.workflow.chains.metric_evaluator import evaluate_answers
# from src.workflow.ground_truths import GROUND_TRUTHS


# def generate(state: GraphState) -> Dict[str, Any]:
#     """Generate answers using both Gemini and Perplexity, then evaluate using metrics."""
    
#     print("---GENERATE WITH MULTI-LLM + METRIC EVALUATION---")

#     question = state["question"]
#     original_question = state.get("original_question", question)
#     documents = state.get("documents", [])
#     messages = state.get("messages", [])
#     retry_count = state.get("retry_count", 0)

#     # Retry safety
#     if retry_count > 3:
#         print("---TOO MANY RETRIES, RETURNING SAFE ANSWER---")
#         fallback = "I couldn't generate a reliable answer after multiple attempts. Please try rephrasing your question."
#         return {
#             "documents": documents,
#             "question": question,
#             "generation": fallback,
#             "messages": messages,
#             "chosen_model": "fallback",
#             "validation_reasoning": "Retry limit exceeded"
#         }

#     # Build context
#     history = "\n".join([f"{m.type}: {m.content}" for m in messages[-10:]])
#     context = "\n\n".join([doc.page_content for doc in documents])

#     print(f"---CONTEXT LENGTH: {len(context)}---")
#     print(f"---DOCUMENT COUNT: {len(documents)}---")
#     print(f"---RETRY COUNT: {retry_count}---")

#     # ----------------------------
#     # 1️⃣ GENERATE FROM GEMINI
#     # ----------------------------
#     print("---GENERATING WITH GEMINI---")
#     try:
#         gemini_answer = gemini_generation_chain.invoke({
#             "context": context,
#             "question": question,
#             "history": history
#         })
#         print(f"---GEMINI OK ({len(gemini_answer)} chars)---")
#     except Exception as e:
#         print(f"---GEMINI ERROR: {str(e)}---")
#         gemini_answer = f"Error: {str(e)}"

#     # ----------------------------
#     # 2️⃣ GENERATE FROM PERPLEXITY
#     # ----------------------------
#     print("---GENERATING WITH PERPLEXITY---")
#     try:
#         perplexity_answer = perplexity_generation_chain.invoke({
#             "context": context,
#             "question": question,
#             "history": history
#         })
#         print(f"---PERPLEXITY OK ({len(perplexity_answer)} chars)---")
#     except Exception as e:
#         print(f"---PERPLEXITY ERROR: {str(e)}---")
#         perplexity_answer = f"Error: {str(e)}"

#     print(f"---GEMINI ANSWER: {gemini_answer}---")
#     print(f"---PERPLEXITY ANSWER: {perplexity_answer}---")

#     # ----------------------------
#     # 3️⃣ METRIC VALIDATION
#     # ----------------------------

#     # Normalize lookup
#     q_norm = original_question.lower().strip()
#     ground_truth = None

#     for key, val in GROUND_TRUTHS.items():
#         if key in q_norm:
#             ground_truth = val
#             break

#     if ground_truth is None:
#         print("---NO GROUND TRUTH FOUND → DEFAULTING TO PERPLEXITY---")
#         chosen_model = "perplexity"
#         generation = perplexity_answer
#         validation_reasoning = "No ground truth available for metric evaluation."

#     else:
#         print("---GROUND TRUTH FOUND → RUNNING METRIC EVALUATION---")

#         # Ensure neither answer crashed
#         if "Error:" in gemini_answer and "Error:" in perplexity_answer:
#             print("---BOTH MODELS FAILED---")
#             chosen_model = "error"
#             generation = "Both models failed. Try again."
#             validation_reasoning = "Both Gemini and Perplexity errored."

#         elif "Error:" in gemini_answer:
#             print("---GEMINI FAILED → USING PERPLEXITY---")
#             chosen_model = "perplexity"
#             generation = perplexity_answer
#             validation_reasoning = "Gemini failed to generate."

#         elif "Error:" in perplexity_answer:
#             print("---PERPLEXITY FAILED → USING GEMINI---")
#             chosen_model = "gemini"
#             generation = gemini_answer
#             validation_reasoning = "Perplexity failed to generate."

#         else:
#             # BOTH answers OK → compute metrics
#             eval_result = evaluate_answers(
#                 gemini_answer,
#                 perplexity_answer,
#                 ground_truth
#             )
#             state["metric_evaluation"] = eval_result

#             print("---METRIC EVALUATION RESULTS---")
#             print(eval_result)

#             chosen_model = eval_result["winner"]

#             if chosen_model == "gemini":
#                 generation = gemini_answer
#             else:
#                 generation = perplexity_answer

#             validation_reasoning = f"Selected {chosen_model} based on highest evaluation score."

#     # ----------------------------
#     # 4️⃣ UPDATE CHAT HISTORY
#     # ----------------------------
#     messages.append(HumanMessage(content=question))
#     messages.append(AIMessage(content=generation))

#     print(f"---FINAL ANSWER: {generation[:120]}...---")
#     print(f"---CHOSEN MODEL: {chosen_model}---")

#     return {
#            "documents": documents,
#             "question": question,
#             "original_question": original_question,
#             "rewritten_question": state.get("question", question),
#             "route": state.get("route", "N/A"),
#             "generation": generation,
#             "messages": messages,
#             "gemini_answer": gemini_answer,
#             "perplexity_answer": perplexity_answer,
#             "chosen_model": chosen_model,
#             "validation_reasoning": validation_reasoning,
#             "metric_evaluation": eval_result if ground_truth else None
#     }



#metrics working
# from typing import Any, Dict
# from langchain_core.messages import HumanMessage, AIMessage

# from src.workflow.chains.generation import gemini_generation_chain, perplexity_generation_chain
# from src.workflow.state import GraphState

# # NEW IMPORTS (metrics-based evaluator)
# from src.workflow.chains.metric_evaluator import evaluate_answers
# from src.workflow.ground_truths import GROUND_TRUTHS


# def generate(state: GraphState) -> Dict[str, Any]:
#     """Generate answers using both Gemini and Perplexity, then evaluate using metrics."""
    
#     print("---GENERATE WITH MULTI-LLM + METRIC EVALUATION---")

#     question = state["question"]
#     original_question = state.get("original_question", question)
#     documents = state.get("documents", [])
#     messages = state.get("messages", [])
#     retry_count = state.get("retry_count", 0)

#     # Retry safety
#     if retry_count > 3:
#         print("---TOO MANY RETRIES, RETURNING SAFE ANSWER---")
#         fallback = "I couldn't generate a reliable answer after multiple attempts. Please try rephrasing your question."
#         return {
#             "documents": documents,
#             "question": question,
#             "generation": fallback,
#             "messages": messages,
#             "chosen_model": "fallback",
#             "validation_reasoning": "Retry limit exceeded"
#         }

#     # Build context
#     history = "\n".join([f"{m.type}: {m.content}" for m in messages[-10:]])
#     context = "\n\n".join([doc.page_content for doc in documents])

#     print(f"---CONTEXT LENGTH: {len(context)}---")
#     print(f"---DOCUMENT COUNT: {len(documents)}---")
#     print(f"---RETRY COUNT: {retry_count}---")

#     # ----------------------------
#     # 1️⃣ GENERATE FROM GEMINI
#     # ----------------------------
#     print("---GENERATING WITH GEMINI---")
#     try:
#         gemini_answer = gemini_generation_chain.invoke({
#             "context": context,
#             "question": question,
#             "history": history
#         })
#         print(f"---GEMINI OK ({len(gemini_answer)} chars)---")
#     except Exception as e:
#         print(f"---GEMINI ERROR: {str(e)}---")
#         gemini_answer = f"Error: {str(e)}"

#     # ----------------------------
#     # 2️⃣ GENERATE FROM PERPLEXITY
#     # ----------------------------
#     print("---GENERATING WITH PERPLEXITY---")
#     try:
#         perplexity_answer = perplexity_generation_chain.invoke({
#             "context": context,
#             "question": question,
#             "history": history
#         })
#         print(f"---PERPLEXITY OK ({len(perplexity_answer)} chars)---")
#     except Exception as e:
#         print(f"---PERPLEXITY ERROR: {str(e)}---")
#         perplexity_answer = f"Error: {str(e)}"

#     print(f"---GEMINI ANSWER: {gemini_answer}---")
#     print(f"---PERPLEXITY ANSWER: {perplexity_answer}---")

#     # ----------------------------
#     # 3️⃣ METRIC VALIDATION
#     # ----------------------------

#     # Normalize lookup
#     q_norm = original_question.lower().strip()
#     ground_truth = None

#     for key, val in GROUND_TRUTHS.items():
#         if key in q_norm:
#             ground_truth = val
#             break

#     if ground_truth is None:
#         print("---NO GROUND TRUTH FOUND → DEFAULTING TO PERPLEXITY---")
#         chosen_model = "perplexity"
#         generation = perplexity_answer
#         validation_reasoning = "No ground truth available for metric evaluation."

#     else:
#         print("---GROUND TRUTH FOUND → RUNNING METRIC EVALUATION---")

#         # Ensure neither answer crashed
#         if "Error:" in gemini_answer and "Error:" in perplexity_answer:
#             print("---BOTH MODELS FAILED---")
#             chosen_model = "error"
#             generation = "Both models failed. Try again."
#             validation_reasoning = "Both Gemini and Perplexity errored."

#         elif "Error:" in gemini_answer:
#             print("---GEMINI FAILED → USING PERPLEXITY---")
#             chosen_model = "perplexity"
#             generation = perplexity_answer
#             validation_reasoning = "Gemini failed to generate."

#         elif "Error:" in perplexity_answer:
#             print("---PERPLEXITY FAILED → USING GEMINI---")
#             chosen_model = "gemini"
#             generation = gemini_answer
#             validation_reasoning = "Perplexity failed to generate."

#         else:
#             # BOTH answers OK → compute metrics
#             eval_result = evaluate_answers(
#                 gemini_answer,
#                 perplexity_answer,
#                 ground_truth
#             )

#             print("---METRIC EVALUATION RESULTS---")
#             print(eval_result)

#             chosen_model = eval_result["winner"]

#             if chosen_model == "gemini":
#                 generation = gemini_answer
#             else:
#                 generation = perplexity_answer

#             validation_reasoning = f"Selected {chosen_model} based on highest evaluation score."

#     # ----------------------------
#     # 4️⃣ UPDATE CHAT HISTORY
#     # ----------------------------
#     messages.append(HumanMessage(content=question))
#     messages.append(AIMessage(content=generation))

#     print(f"---FINAL ANSWER: {generation[:120]}...---")
#     print(f"---CHOSEN MODEL: {chosen_model}---")

#     return {
#         "documents": documents,
#         "question": question,
#         "generation": generation,
#         "messages": messages,
#         "gemini_answer": gemini_answer,
#         "perplexity_answer": perplexity_answer,
#         "chosen_model": chosen_model,
#         "validation_reasoning": validation_reasoning
#     }

#UPDATED TO RETURN METRICS

# from typing import Any, Dict
# from langchain_core.messages import HumanMessage, AIMessage

# from src.workflow.chains.generation import gemini_generation_chain, perplexity_generation_chain
# from src.workflow.state import GraphState
# from src.workflow.chains.metric_evaluator import evaluate_answers
# from src.workflow.ground_truths import GROUND_TRUTHS


# def generate(state: GraphState) -> Dict[str, Any]:
#     """Generate answers using both Gemini and Perplexity, then evaluate using metrics."""
    
#     print("---GENERATE WITH MULTI-LLM + METRIC EVALUATION---")

#     question = state["question"]
#     original_question = state.get("original_question", question)
#     documents = state.get("documents", [])
#     messages = state.get("messages", [])
#     retry_count = state.get("retry_count", 0)

#     # Retry safety
#     if retry_count > 3:
#         fallback = "I couldn't generate a reliable answer after multiple attempts. Please try rephrasing your question."
#         return {
#             "documents": documents,
#             "question": question,
#             "generation": fallback,
#             "messages": messages,
#             "chosen_model": "fallback",
#             "validation_reasoning": "Retry limit exceeded",
#             "validation_result": None
#         }

#     # Build context
#     history = "\n".join([f"{m.type}: {m.content}" for m in messages[-10:]])
#     context = "\n\n".join([doc.page_content for doc in documents])

#     # ----------------------------
#     # 1️⃣ GENERATE FROM GEMINI
#     # ----------------------------
#     try:
#         gemini_answer = gemini_generation_chain.invoke({
#             "context": context,
#             "question": question,
#             "history": history
#         })
#     except Exception as e:
#         gemini_answer = f"Error: {str(e)}"

#     # ----------------------------
#     # 2️⃣ GENERATE FROM PERPLEXITY
#     # ----------------------------
#     try:
#         perplexity_answer = perplexity_generation_chain.invoke({
#             "context": context,
#             "question": question,
#             "history": history
#         })
#     except Exception as e:
#         perplexity_answer = f"Error: {str(e)}"

#     # ----------------------------
#     # 3️⃣ METRIC VALIDATION
#     # ----------------------------

#     # Normalize lookup
#     q_norm = original_question.lower().strip()
#     ground_truth = None

#     for key, val in GROUND_TRUTHS.items():
#         if key in q_norm:
#             ground_truth = val
#             break

#     eval_result = None  # <-- NEW

#     if ground_truth is None:
#         chosen_model = "perplexity"
#         generation = perplexity_answer
#         validation_reasoning = "No ground truth available for metric evaluation."

#     else:
#         # Both crashed
#         if "Error:" in gemini_answer and "Error:" in perplexity_answer:
#             chosen_model = "error"
#             generation = "Both models failed. Try again."
#             validation_reasoning = "Both Gemini and Perplexity errored."

#         elif "Error:" in gemini_answer:
#             chosen_model = "perplexity"
#             generation = perplexity_answer
#             validation_reasoning = "Gemini failed to generate."

#         elif "Error:" in perplexity_answer:
#             chosen_model = "gemini"
#             generation = gemini_answer
#             validation_reasoning = "Perplexity failed to generate."

#         else:
#             # RUN METRIC EVALUATOR
#             eval_result = evaluate_answers(
#                 gemini_answer,
#                 perplexity_answer,
#                 ground_truth
#             )

#             chosen_model = eval_result["winner"]
#             generation = gemini_answer if chosen_model == "gemini" else perplexity_answer
#             validation_reasoning = "Selected best model based on metric evaluation."

#     # ----------------------------
#     # 4️⃣ UPDATE CHAT HISTORY
#     # ----------------------------
#     messages.append(HumanMessage(content=question))
#     messages.append(AIMessage(content=generation))

#     # ----------------------------
#     # 5️⃣ RETURN STATE (NOW WITH SCORES)
#     # ----------------------------
#     return {
#         "documents": documents,
#         "question": question,
#         "original_question": original_question,
#         "generation": generation,
#         "messages": messages,
#         "gemini_answer": gemini_answer,
#         "perplexity_answer": perplexity_answer,
#         "chosen_model": chosen_model,
#         "validation_reasoning": validation_reasoning,
#         "validation_result": eval_result,   # <-- THE METRIC SCORES ARE RETURNED HERE
#     }

########################################Update to evaluate metric with context
# src/workflow/nodes/generate.py
# src/workflow/nodes/generate.py
from typing import Any, Dict
from langchain_core.messages import HumanMessage, AIMessage
from src.workflow.chains.generation import gemini_generation_chain, perplexity_generation_chain
from src.workflow.state import GraphState, convert_numpy_types
from src.workflow.chains.metric_evaluator import evaluate_answers_with_context

def generate(state: GraphState) -> Dict[str, Any]:
    """Generate answers using both Gemini and Perplexity, then evaluate against context."""
    
    print("---GENERATE WITH CONTEXT-BASED EVALUATION---")

    question = state["question"]
    documents = state.get("documents", [])
    messages = state.get("messages", [])
    retry_count = state.get("retry_count", 0)

    # Retry safety
    if retry_count > 3:
        fallback = "I couldn't generate a reliable answer after multiple attempts. Please try rephrasing your question."
        return {
            "documents": documents,
            "question": question,
            "generation": fallback,
            "messages": messages,
            "chosen_model": "fallback",
            "validation_reasoning": "Retry limit exceeded",
            "validation_result": None
        }

    # Build context and history
    history = "\n".join([f"{m.type}: {m.content}" for m in messages[-10:]])
    context = "\n\n".join([doc.page_content for doc in documents])

    print(f"---CONTEXT LENGTH: {len(context)} chars---")
    print(f"---DOCUMENT COUNT: {len(documents)}---")

    # ----------------------------
    # 1️⃣ GENERATE FROM BOTH MODELS
    # ----------------------------
    print("---GENERATING WITH GEMINI---")
    try:
        gemini_answer = gemini_generation_chain.invoke({
            "context": context,
            "question": question,
            "history": history
        })
        print(f"---GEMINI OK ({len(gemini_answer)} chars)---")
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
        print(f"---PERPLEXITY OK ({len(perplexity_answer)} chars)---")
    except Exception as e:
        print(f"---PERPLEXITY ERROR: {str(e)}---")
        perplexity_answer = f"Error: {str(e)}"

    # ----------------------------
    # 2️⃣ CONTEXT-BASED METRIC VALIDATION
    # ----------------------------
    eval_result = None

    # Both crashed
    if "Error:" in gemini_answer and "Error:" in perplexity_answer:
        chosen_model = "error"
        generation = "Both models failed. Try again."
        validation_reasoning = "Both Gemini and Perplexity errored."

    elif "Error:" in gemini_answer:
        chosen_model = "perplexity"
        generation = perplexity_answer
        validation_reasoning = "Gemini failed to generate."

    elif "Error:" in perplexity_answer:
        chosen_model = "gemini"
        generation = gemini_answer
        validation_reasoning = "Perplexity failed to generate."

    else:
        # BOTH answers OK → evaluate against context
        print("---RUNNING CONTEXT-BASED EVALUATION---")
        eval_result = evaluate_answers_with_context(
            gemini_answer,
            perplexity_answer,
            context  # Pass the retrieved context for evaluation
        )

        chosen_model = eval_result["winner"]
        generation = gemini_answer if chosen_model == "gemini" else perplexity_answer
        validation_reasoning = f"Selected {chosen_model} based on better factual consistency with retrieved context."

        print(f"---CONTEXT EVALUATION RESULTS---")
        print(f"Gemini Score: {eval_result['gemini_score']:.4f}")
        print(f"Perplexity Score: {eval_result['perplexity_score']:.4f}")
        print(f"Winner: {chosen_model}")

    # ----------------------------
    # 3️⃣ UPDATE CHAT HISTORY
    # ----------------------------
    messages.append(HumanMessage(content=question))
    messages.append(AIMessage(content=generation))

    print(f"---FINAL ANSWER: {generation[:120]}...---")
    print(f"---CHOSEN MODEL: {chosen_model}---")

    # Ensure all data is serializable
    if eval_result:
        eval_result = convert_numpy_types(eval_result)

    return {
        "documents": documents,
        "question": question,
        "generation": generation,
        "messages": messages,
        "gemini_answer": gemini_answer,
        "perplexity_answer": perplexity_answer,
        "chosen_model": chosen_model,
        "validation_reasoning": validation_reasoning,
        "validation_result": eval_result,  # Contains context-based metrics
        "retrieved_context": context[:2000] + "..." if len(context) > 2000 else context  # For debugging
    }