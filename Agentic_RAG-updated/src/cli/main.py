# # from dotenv import load_dotenv
# # from src.workflow.graph import app

# # load_dotenv()

# # def format_response(result):
# #     """Extract response from workflow result."""
# #     if isinstance(result, dict) and "generation" in result:
# #         return result["generation"]
# #     elif isinstance(result, dict) and "answer" in result:
# #         return result["answer"]
# #     else:
# #         return str(result)

# # def main():
# #     """CLI for adaptive RAG system."""
# #     print("Adaptive RAG System")
# #     print("Type 'quit' to exit.\n")
    
# #     # Fixed thread_id for session state; can prompt for multi-user
# #     thread_id = "user_session_1"  # Or input("Enter session ID: ") for multi-user
    
# #     while True:
# #         try:
# #             question = input("Question: ").strip()
            
# #             if question.lower() in ['quit', 'exit', 'q', '']:
# #                 break
                
# #             print("Processing...")
# #             config = {"configurable": {"thread_id": thread_id}}  # Pass config for state
# #             result = None
# #             for output in app.stream({"question": question}, config=config):  # Fix: named config
# #                 for key, value in output.items():
# #                     result = value
                    
# #             if result:
# #                 print(f"\nAnswer: {format_response(result)}")
# #                 print("\nRetrieved Documents")
# #                 # Collect unique sources
# #                 unique_sources = set()
# #                 for doc in result.get("documents", []):
# #                     source = doc.metadata.get("source", "Unknown Source")
# #                     unique_sources.add(source)
                
# #                 # Display unique sources
# #                 for i, source in enumerate(sorted(unique_sources), 1):
# #                     print(f"Doc {i}: {source}")
# #                 print("\nAnswer generated!")
# #             else:
# #                 print("No response generated.")
                
# #         except KeyboardInterrupt:
# #             break
# #         except Exception as e:
# #             print(f"Error: {str(e)}")

# # if __name__ == "__main__":
# #     main()

# from dotenv import load_dotenv
# from src.workflow.graph import app

# load_dotenv()


# # =============================================
# # PRETTY OUTPUT FORMATTER
# # =============================================
# def pretty_print(result: dict):
#     print("\n" + "=" * 60)
#     print("                 ADAPTIVE RAG SYSTEM")
#     print("=" * 60)

#     # ---------------------------
#     # QUERY & REWRITE
#     # ---------------------------
#     print("\n🔍 Query:")
#     print(result.get("original_question", result.get("question", "N/A")))

#     if "rewritten_question" in result:
#         print("\n✏️ Rewritten Query:")
#         print(result["rewritten_question"])

#     # ---------------------------
#     # ROUTING INFO
#     # ---------------------------
#     if "route" in result:
#         print("\n🌐 Routed To:")
#         print(result["route"])

#     # ---------------------------
#     # RETRIEVED DOCUMENTS
#     # ---------------------------
#     documents = result.get("documents", [])
#     if documents:
#         print("\n📄 Retrieved Documents (Unique Sources)")
#         print("-" * 60)
#         unique_sources = set()

#         for doc in documents:
#             src = doc.metadata.get("source", "Unknown")
#             unique_sources.add(src)

#         for i, src in enumerate(sorted(unique_sources), start=1):
#             print(f"{i}. {src}")

#     # ---------------------------
#     # MODEL ANSWERS
#     # ---------------------------
#     gem = result.get("gemini_answer", None)
#     per = result.get("perplexity_answer", None)

#     if gem or per:
#         print("\n🤖 Model Outputs")
#         print("-" * 60)

#         if gem:
#             print("Gemini:")
#             print(gem[:300] + "..." if len(gem) > 300 else gem)
#             print()

#         if per:
#             print("Perplexity:")
#             print(per[:300] + "..." if len(per) > 300 else per)
#             print()

#     # ---------------------------
#     # METRIC EVALUATION RESULT
#     # ---------------------------
#     val_res = result.get("validation_result", None)
#     if val_res:
#         print("\n📊 Evaluation Metrics (Model Comparison)")
#         print("-" * 60)
#         print(f"Winner: ⭐ {val_res['winner'].upper()} ⭐")
#         print(f"Gemini Score:     {val_res['gemini_score']:.4f}")
#         print(f"Perplexity Score: {val_res['perplexity_score']:.4f}")

#     # ---------------------------
#     # FINAL ANSWER
#     # ---------------------------
#     print("\n🏆 Final Answer")
#     print("-" * 60)
#     final_ans = result.get("generation", "No final answer.")
#     print(final_ans)

#     # ---------------------------
#     # QUALITY CHECK FLAGS
#     # ---------------------------
#     hallucination_pass = result.get("hallucination_pass", True)
#     answer_pass = result.get("answer_grade_pass", True)

#     print("\n🔎 Quality Check")
#     print(f"Hallucination Check: {'PASS' if hallucination_pass else 'FAIL'}")
#     print(f"Answer Grade Check:  {'PASS' if answer_pass else 'FAIL'}")

#     print("\n" + "=" * 60)
#     print("                   OUTPUT COMPLETE")
#     print("=" * 60 + "\n")


# # =============================================
# # CLI LOOP
# # =============================================
# def main():
#     print("Adaptive RAG System")
#     print("Type 'quit' to exit.\n")

#     thread_id = "user_session_1"  # session persistence

#     while True:
#         try:
#             question = input("Question: ").strip()

#             if question.lower() in ["quit", "exit", "q"]:
#                 break

#             if not question:
#                 continue

#             print("Processing...\n")

#             config = {"configurable": {"thread_id": thread_id}}
#             result = None

#             # stream results from the workflow
#             for output in app.stream({"question": question}, config=config):
#                 for key, value in output.items():  # capture final state
#                     result = value

#             if result:
#                 pretty_print(result)
#             else:
#                 print("⚠ No response generated.\n")

#         except KeyboardInterrupt:
#             break
#         except Exception as e:
#             print(f"Error: {str(e)}\n")


# if __name__ == "__main__":
#     main()


#UPDATED TO RETURN METRICS
# from dotenv import load_dotenv
# from src.workflow.graph import app

# load_dotenv()


# # =============================================
# # PRETTY OUTPUT FORMATTER
# # =============================================
# def pretty_print(result: dict):
#     print("\n" + "=" * 60)
#     print("                 ADAPTIVE RAG SYSTEM")
#     print("=" * 60)

#     # ---------------------------
#     # QUERY & REWRITE
#     # ---------------------------
#     print("\n🔍 Query:")
#     print(result.get("original_question", result.get("question", "N/A")))

#     if "rewritten_question" in result:
#         print("\n✏️ Rewritten Query:")
#         print(result["rewritten_question"])

#     # ---------------------------
#     # RETRIEVED DOCUMENTS
#     # ---------------------------
#     documents = result.get("documents", [])
#     if documents:
#         print("\n📄 Retrieved Documents (Unique Sources)")
#         print("-" * 60)
#         unique_sources = set()

#         for doc in documents:
#             src = doc.metadata.get("source", "Unknown")
#             unique_sources.add(src)

#         for i, src in enumerate(sorted(unique_sources), start=1):
#             print(f"{i}. {src}")

#     # ---------------------------
#     # MODEL ANSWERS
#     # ---------------------------
#     gem = result.get("gemini_answer", None)
#     per = result.get("perplexity_answer", None)

#     if gem or per:
#         print("\n🤖 Model Outputs")
#         print("-" * 60)

#         if gem:
#             print("Gemini:")
#             print(gem[:300] + "..." if len(gem) > 300 else gem)
#             print()

#         if per:
#             print("Perplexity:")
#             print(per[:300] + "..." if len(per) > 300 else per)
#             print()

#     # ---------------------------
#     # METRIC EVALUATION RESULT
#     # ---------------------------
#     val_res = result.get("validation_result", None)

#     if val_res:
#         print("\n📊 Evaluation Metrics (Model Comparison)")
#         print("-" * 60)
#         print(f"Winner: ⭐ {val_res['winner'].upper()} ⭐")
#         print(f"Gemini Score:     {val_res['gemini_score']:.4f}")
#         print(f"Perplexity Score: {val_res['perplexity_score']:.4f}")

#         # Optional: show detailed metrics
#         print("\n🔬 Detailed Gemini Metrics")
#         for k, v in val_res["gemini_metrics"].items():
#             print(f"{k}: {v:.4f}")

#         print("\n🔬 Detailed Perplexity Metrics")
#         for k, v in val_res["perplexity_metrics"].items():
#             print(f"{k}: {v:.4f}")

#     # ---------------------------
#     # FINAL ANSWER
#     # ---------------------------
#     print("\n🏆 Final Answer")
#     print("-" * 60)
#     print(result.get("generation", "No final answer."))

#     print("\n" + "=" * 60)
#     print("                   OUTPUT COMPLETE")
#     print("=" * 60 + "\n")


# # =============================================
# # CLI LOOP
# # =============================================
# def main():
#     print("Adaptive RAG System")
#     print("Type 'quit' to exit.\n")

#     thread_id = "user_session_1"

#     while True:
#         try:
#             question = input("Question: ").strip()

#             if question.lower() in ["quit", "exit", "q"]:
#                 break

#             if not question:
#                 continue

#             print("Processing...\n")

#             config = {"configurable": {"thread_id": thread_id}}
#             result = None

#             for output in app.stream({"question": question}, config=config):
#                 for key, value in output.items():
#                     result = value

#             if result:
#                 pretty_print(result)
#             else:
#                 print("⚠ No response generated.\n")

#         except KeyboardInterrupt:
#             break
#         except Exception as e:
#             print(f"Error: {str(e)}\n")


# if __name__ == "__main__":
#     main()




##################################Updated to evaluate the context for metrics
#UPDATED TO RETURN CONTEXT-BASED METRICS
from dotenv import load_dotenv
from src.workflow.graph import app

load_dotenv()


# =============================================
# PRETTY OUTPUT FORMATTER
# =============================================
def pretty_print(result: dict):
    print("\n" + "=" * 60)
    print("                 ADAPTIVE RAG SYSTEM")
    print("=" * 60)

    # ---------------------------
    # QUERY & REWRITE
    # ---------------------------
    print("\n🔍 Query:")
    print(result.get("original_question", result.get("question", "N/A")))

    if "rewritten_question" in result:
        print("\n✏️ Rewritten Query:")
        print(result["rewritten_question"])

    # ---------------------------
    # RETRIEVED DOCUMENTS
    # ---------------------------
    documents = result.get("documents", [])
    if documents:
        print("\n📄 Retrieved Documents (Unique Sources)")
        print("-" * 60)
        unique_sources = set()

        for doc in documents:
            src = doc.metadata.get("source", "Unknown")
            unique_sources.add(src)

        for i, src in enumerate(sorted(unique_sources), start=1):
            print(f"{i}. {src}")

    # ---------------------------
    # MODEL ANSWERS
    # ---------------------------
    gem = result.get("gemini_answer", None)
    per = result.get("perplexity_answer", None)

    if gem or per:
        print("\n🤖 Model Outputs")
        print("-" * 60)

        if gem:
            print("Gemini:")
            print(gem[:300] + "..." if len(gem) > 300 else gem)
            print()

        if per:
            print("Perplexity:")
            print(per[:300] + "..." if len(per) > 300 else per)
            print()

    # ---------------------------
    # CONTEXT-BASED METRIC EVALUATION RESULT
    # ---------------------------
    val_res = result.get("validation_result", None)

    if val_res:
        print("\n📊 CONTEXT-BASED Evaluation Metrics")
        print("-" * 60)
        print(f"Winner: ⭐ {val_res['winner'].upper()} ⭐")
        print(f"Evaluation: {val_res.get('evaluation_note', 'Based on context consistency')}")
        print(f"Gemini Score:     {val_res['gemini_score']:.4f}")
        print(f"Perplexity Score: {val_res['perplexity_score']:.4f}")

        # Show key context-based metrics
        print("\n🔬 Key Context Metrics (Higher is better)")
        gem_metrics = val_res["gemini_metrics"]
        perp_metrics = val_res["perplexity_metrics"]
        
        print(f"Faithfulness:     Gemini {gem_metrics['faithfulness']:.3f} | Perplexity {perp_metrics['faithfulness']:.3f}")
        print(f"Context Usage:    Gemini {gem_metrics['context_utilization']:.3f} | Perplexity {perp_metrics['context_utilization']:.3f}")
        print(f"BERT F1:          Gemini {gem_metrics['bert_f1']:.3f} | Perplexity {perp_metrics['bert_f1']:.3f}")
        print(f"Cosine Similarity: Gemini {gem_metrics['cosine_sim']:.3f} | Perplexity {perp_metrics['cosine_sim']:.3f}")
        print(f"Novel Terms:      Gemini {gem_metrics['novel_terms_ratio']:.3f} | Perplexity {perp_metrics['novel_terms_ratio']:.3f}")

        # Optional: show detailed metrics
        print("\n📈 Detailed Gemini Metrics")
        for k, v in val_res["gemini_metrics"].items():
            print(f"{k}: {v:.4f}")

        print("\n📈 Detailed Perplexity Metrics")
        for k, v in val_res["perplexity_metrics"].items():
            print(f"{k}: {v:.4f}")

    # ---------------------------
    # FINAL ANSWER
    # ---------------------------
    print("\n🏆 Final Answer")
    print("-" * 60)
    print(result.get("generation", "No final answer."))

    # ---------------------------
    # CONTEXT INFO (for debugging)
    # ---------------------------
    if result.get("retrieved_context"):
        print("\n📋 Retrieved Context (Preview)")
        print("-" * 60)
        context_preview = result["retrieved_context"]
        if len(context_preview) > 500:
            print(context_preview[:500] + "...")
        else:
            print(context_preview)

    print("\n" + "=" * 60)
    print("                   OUTPUT COMPLETE")
    print("=" * 60 + "\n")


# =============================================
# CLI LOOP
# =============================================
def main():
    print("Adaptive RAG System")
    print("Type 'quit' to exit.\n")

    thread_id = "user_session_1"

    while True:
        try:
            question = input("Question: ").strip()

            if question.lower() in ["quit", "exit", "q"]:
                break

            if not question:
                continue

            print("Processing...\n")

            config = {"configurable": {"thread_id": thread_id}}
            result = None

            for output in app.stream({"question": question}, config=config):
                for key, value in output.items():
                    result = value

            if result:
                pretty_print(result)
            else:
                print("⚠ No response generated.\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")


if __name__ == "__main__":
    main()