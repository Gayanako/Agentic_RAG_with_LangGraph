import streamlit as st
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Streamlit app configuration - Classic Theme
st.set_page_config(
    page_title="Adaptive RAG System", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for classic styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .model-box {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #fafafa;
    }
    .selected-model {
        border-color: #4CAF50;
        background-color: #f0f8f0;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
    }
    .validation-box {
        border: 2px solid #ff9800;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #fff3e0;
    }
    .source-box {
        border: 1px solid #b0bec5;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #eceff1;
    }
    .metric-box {
        text-align: center;
        padding: 1rem;
        border-radius: 5px;
        background-color: #f5f5f5;
    }
    .error-box {
        border: 2px solid #f44336;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background-color: #ffebee;
    }
</style>
""", unsafe_allow_html=True)

# --- Utility functions ---
def format_response(result):
    """Extract response from workflow result."""
    if isinstance(result, dict) and "generation" in result:
        return result["generation"]
    elif isinstance(result, dict) and "answer" in result:
        return result["answer"]
    else:
        return str(result)

def log_feedback(question, answer, rating):
    """Log user feedback to a file."""
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "rating": rating
    }
    feedback_dir = "logs"
    feedback_file = os.path.join(feedback_dir, "feedback_log.txt")
    try:
        os.makedirs(feedback_dir, exist_ok=True)
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_entry) + "\n")
        return f"✅ Feedback logged successfully: {rating}"
    except Exception as e:
        return f"⚠️ Failed to log feedback: {str(e)}"

# --- Initialize session state ---
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "feedback_status" not in st.session_state:
    st.session_state.feedback_status = ""
if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"user_session_{datetime.now().timestamp()}"

# Header
st.markdown('<div class="main-header">🤖 Adaptive RAG System</div>', unsafe_allow_html=True)

# Sidebar for history and metrics
with st.sidebar:
    st.header("Session Overview")
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", len(st.session_state.query_history))
    with col2:
        if st.session_state.last_result and st.session_state.last_result.get("chosen_model"):
            chosen_model = st.session_state.last_result["chosen_model"]
            # Handle fallback cases
            if "fallback" in chosen_model:
                display_model = chosen_model.split(" ")[0].upper()
            else:
                display_model = chosen_model.upper()
            st.metric("Best Model", display_model)
        else:
            st.metric("Best Model", "N/A")
    
    st.divider()
    
    st.subheader("Query History")
    if st.session_state.query_history:
        for i, entry in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            with st.expander(f"Q{i}: {entry['question'][:50]}...", expanded=False):
                st.markdown(f"**Answer:** {entry['answer'][:100]}...")
    else:
        st.info("No queries yet.")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Input section
    st.subheader("Ask a Question")
    question = st.text_area(
        "Enter your question:", 
        placeholder="e.g., What are AI agents? How do they work?",
        height=100
    )
    
    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("🚀 Get Answer", use_container_width=True, type="primary"):
            if not question.strip():
                st.error("Please enter a valid question.")
            else:
                try:
                    with st.spinner("🔄 Processing with multiple AI models..."):
                        st.session_state.last_result = None
                        st.session_state.feedback_status = ""
                        st.session_state.current_answer = ""
                        st.session_state.current_question = question

                        try:
                            from src.workflow.graph import app
                        except ImportError as e:
                            st.error(f"Failed to import workflow: {str(e)}")
                            st.stop()

                        # SIMPLIFIED CONFIG - No manual event loop management
                        config = {
                            "configurable": {"thread_id": st.session_state.thread_id},
                            "recursion_limit": 100
                        }
                        
                        try:
                            # Collect all outputs
                            full_output = []
                            for output in app.stream({"question": question}, config=config):
                                full_output.append(output)
                            
                            # Get the final result from the last output
                            if full_output:
                                last_output = full_output[-1]
                                for key, value in last_output.items():
                                    result = value
                                    break
                            
                            st.session_state.last_result = result
                            
                        except Exception as e:
                            st.error(f"❌ Processing error: {str(e)}")
                            st.session_state.last_result = {
                                "generation": f"Error: {str(e)}",
                                "gemini_answer": "Error during processing",
                                "perplexity_answer": "Error during processing", 
                                "validation_reasoning": "System encountered an error",
                                "chosen_model": "error"
                            }

                except Exception as e:
                    st.error(f"❌ System error: {str(e)}")

    with btn_col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.query_history = []
            st.session_state.last_result = None
            st.session_state.feedback_status = ""
            st.session_state.current_answer = ""
            st.session_state.current_question = ""
            st.session_state.thread_id = f"user_session_{datetime.now().timestamp()}"
            st.rerun()

    with btn_col3:
        if st.button("📊 System Info", use_container_width=True):
            st.info("""
            **System Architecture:**
            - 🤖 Gemini Pro: Text generation
            - 🔍 Perplexity Sonar: Alternative generation  
            - 🧠 GPT-4o-mini: Answer validation
            - 📚 Vector Store: Document retrieval
            - 🌐 Web Search: Fallback option
            
            **Workflow:**
            1. Question routing
            2. Document retrieval & grading
            3. Parallel model generation
            4. AI-powered validation
            5. Best answer selection
            """)

# Display results
if st.session_state.last_result:
    result = st.session_state.last_result
    answer = format_response(result)
    
    # Store in history (only if we have a valid answer)
    if question and answer and not answer.startswith("Error:"):
        # Check if this question is already in history to avoid duplicates
        existing_questions = [entry['question'] for entry in st.session_state.query_history]
        if question not in existing_questions:
            st.session_state.current_answer = answer
            st.session_state.query_history.append({"question": question, "answer": answer})

    with col1:
        # Selected Answer Section
        st.markdown("---")
        st.subheader("🎯 Selected Best Answer")
        
        chosen_model = result.get("chosen_model", "")
        if chosen_model:
            if "fallback" in chosen_model:
                st.warning(f"**Selected Model: {chosen_model.upper()}** (Fallback mode)")
            elif "error" in chosen_model:
                st.error("**System encountered an error**")
            else:
                st.success(f"**Selected Model: {chosen_model.upper()}** (Validated by GPT-4o-mini)")
        
        # Display answer with appropriate styling
        if answer.startswith("Error:"):
            st.markdown(f'<div class="error-box">{answer}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="model-box selected-model">{answer}</div>', unsafe_allow_html=True)
        
        # Validation Reasoning
        if result.get("validation_reasoning"):
            st.markdown("### 🧠 Validation Reasoning")
            st.markdown(f'<div class="validation-box">{result["validation_reasoning"]}</div>', unsafe_allow_html=True)

        # Retrieved Documents
        if result.get("documents"):
            st.markdown("### 📚 Retrieved Sources")
            unique_sources = set()
            for doc in result.get("documents", []):
                source = doc.metadata.get("source", "Unknown Source")
                unique_sources.add(source)
            
            for i, source in enumerate(sorted(unique_sources), 1):
                st.markdown(f'<div class="source-box">**Source {i}:** {source}</div>', unsafe_allow_html=True)

    with col2:
        # Parallel Model Responses
        st.markdown("---")
        st.subheader("🤖 Model Responses")
        
        # Gemini Response
        st.markdown("#### 🔷 Gemini Pro")
        gemini_answer = result.get("gemini_answer", "Not available")
        if "Error" in gemini_answer:
            st.markdown(f'<div class="error-box">{gemini_answer}</div>', unsafe_allow_html=True)
        else:
            gemini_class = "model-box selected-model" if result.get("chosen_model") == "gemini" else "model-box"
            st.markdown(f'<div class="{gemini_class}">{gemini_answer}</div>', unsafe_allow_html=True)
        
        # Perplexity Response  
        st.markdown("#### 🔶 Perplexity Sonar")
        perplexity_answer = result.get("perplexity_answer", "Not available")
        if "Error" in perplexity_answer:
            st.markdown(f'<div class="error-box">{perplexity_answer}</div>', unsafe_allow_html=True)
        else:
            perplexity_class = "model-box selected-model" if result.get("chosen_model") == "perplexity" else "model-box"
            st.markdown(f'<div class="{perplexity_class}">{perplexity_answer}</div>', unsafe_allow_html=True)

    # Feedback Section (only show for successful answers)
    if not answer.startswith("Error:") and st.session_state.current_answer and st.session_state.current_question:
        st.markdown("---")
        st.subheader("📊 Feedback")
        
        feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 2])
        
        with feedback_col1:
            if st.button("👍 Helpful", use_container_width=True, key="helpful_btn"):
                st.session_state.feedback_status = log_feedback(
                    st.session_state.current_question,
                    st.session_state.current_answer,
                    "positive"
                )
                st.rerun()
        
        with feedback_col2:
            if st.button("👎 Not Helpful", use_container_width=True, key="not_helpful_btn"):
                st.session_state.feedback_status = log_feedback(
                    st.session_state.current_question,
                    st.session_state.current_answer,
                    "negative"
                )
                st.rerun()
        
        with feedback_col3:
            if st.session_state.feedback_status:
                if "Failed" in st.session_state.feedback_status:
                    st.warning(st.session_state.feedback_status)
                else:
                    st.success(st.session_state.feedback_status)

# Initial state message
elif not st.session_state.last_result and not question:
    with col1:
        st.markdown("---")
        st.info("""
        ## 🚀 Welcome to Adaptive RAG System
        
        **How it works:**
        1. Enter your question in the text area
        2. Click **"Get Answer"** to process with multiple AI models
        3. View parallel responses from Gemini and Perplexity
        4. See which answer was selected as best by GPT-4o-mini
        5. Provide feedback to help improve the system
        
        **Features:**
        - 🤖 Dual-model generation for better accuracy
        - 🧠 AI-powered answer validation  
        - 📚 Smart document retrieval
        - 🌐 Web search fallback
        - 📊 Transparent decision process
        
        **Try asking:**
        - "What are AI agents?"
        - "Explain prompt engineering"
        - "How do language models work?"
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Adaptive RAG System | Multi-Model AI Validation | Classic Interface"
    "</div>", 
    unsafe_allow_html=True
)