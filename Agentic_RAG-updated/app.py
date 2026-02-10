#updated Ui
# app.py — Adaptive RAG System (Streamlit UI, metrics-enabled)
# import streamlit as st
# from dotenv import load_dotenv
# import os
# import json
# from datetime import datetime
# from typing import Any, Dict, Optional
# import pandas as pd

# # Load environment
# load_dotenv()

# st.set_page_config(
#     page_title="Adaptive RAG System",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # =========================================================
# #                     CSS STYLES
# # =========================================================
# st.markdown(
#     """
#     <style>
#       .main-header { font-size: 2.4rem; color: #11A8FF; text-align:center; font-weight:700; margin-bottom:20px;}
#       .model-box { border:1px solid #e0e0e0; border-radius:8px; padding:12px; background:#fafafa; }
#       .selected-model { border-color:#4CAF50; background:#f0f8f0; box-shadow: 0 4px 8px rgba(76,175,80,0.08); }
#       .validation-box { border:1px solid #ff9800; border-radius:8px; padding:10px; background:#fff8ef; margin-bottom:12px;}
#       .source-box { border:1px solid #d0d7de; border-radius:6px; padding:8px; background:#f5f7fa; margin-bottom:6px;}
      
#       .metric-table { border-collapse: collapse; width:100%; margin-top:10px;}
#       .metric-table th, .metric-table td { border: 1px solid #e6e6e6; padding:8px; text-align:center; }
#       .metric-table th { background: #fafafa; }
#       .winner-cell { background: #e6f4ea; font-weight:700; color:#1b5e20;}
#       .loser-cell { background: #fff6f6; color:#b71c1c;}
#       .neutral-cell { background:#ffffff; }
#       .small { font-size:0.85rem; color:#555; }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # =========================================================
# #                     UTILITIES
# # =========================================================
# def format_response(result: Dict[str, Any]) -> str:
#     if not isinstance(result, dict):
#         return str(result)
#     if "generation" in result:
#         return result["generation"]
#     if "answer" in result:
#         return result["answer"]
#     return json.dumps(result, indent=2)

# # Extract metrics safely
# def extract_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
#     default = {
#         "rouge1": None, "rouge2": None, "rougeL": None,
#         "bleu": None, "meteor": None, "bert_f1": None,
#         "cosine_sim": None, "faithfulness": None,
#         "terminology_precision": None, "coverage": None
#     }

#     output = {
#         "gemini_metrics": dict(default),
#         "perplexity_metrics": dict(default),
#         "gemini_score": None,
#         "perplexity_score": None
#     }

#     vr = result.get("validation_result")
#     if vr and isinstance(vr, dict):
#         output["gemini_metrics"] = vr.get("gemini_metrics", default)
#         output["perplexity_metrics"] = vr.get("perplexity_metrics", default)
#         output["gemini_score"] = vr.get("gemini_score")
#         output["perplexity_score"] = vr.get("perplexity_score")
#         return output

#     return output


# def build_metrics_table(gem, perp, gem_score, perp_score):
#     rows = [
#         ("ROUGE-1", "rouge1"),
#         ("ROUGE-2", "rouge2"),
#         ("ROUGE-L", "rougeL"),
#         ("BLEU", "bleu"),
#         ("METEOR", "meteor"),
#         ("BERT-F1", "bert_f1"),
#         ("CosineSim", "cosine_sim"),
#         ("Faithfulness", "faithfulness"),
#         ("Terminology Precision", "terminology_precision"),
#         ("Coverage", "coverage"),
#     ]

#     ranges = {
#         "rouge1": "0.4–0.6 OK, >0.6 strong",
#         "rouge2": "0.2–0.4 OK, >0.4 strong",
#         "rougeL": "0.4–0.6 OK, >0.6 strong",
#         "bleu": "0.2–0.4 OK, >0.4 strong",
#         "meteor": "0.2–0.4 OK, >0.4 strong",
#         "bert_f1": ">0.4 good, >0.6 strong",
#         "cosine_sim": ">0.7 good",
#         "faithfulness": ">0.6 good",
#         "terminology_precision": ">0.6 good",
#         "coverage": ">0.6 good",
#     }

#     table = []
#     for label, key in rows:

#         def fmt(x):
#             try:
#                 return f"{float(x):.3f}"
#             except:
#                 return "n/a"

#         table.append({
#             "Metric": label,
#             "Gemini": fmt(gem.get(key)),
#             "Perplexity": fmt(perp.get(key)),
#             "Good Range": ranges[key]
#         })

#     # Composite score row
#     table.append({
#         "Metric": "Composite Score",
#         "Gemini": f"{gem_score:.4f}" if gem_score else "n/a",
#         "Perplexity": f"{perp_score:.4f}" if perp_score else "n/a",
#         "Good Range": "Higher is better"
#     })

#     return pd.DataFrame(table)


# def render_html_metrics_table(df, gem_score, perp_score, overall_winner):
#     html = []
#     html.append("<div class='model-box'><h4>📊 Metric Comparison</h4>")
#     html.append("<table class='metric-table'>")
#     html.append("<thead><tr><th>Metric</th><th>Gemini</th><th>Perplexity</th><th>Good Range</th></tr></thead>")
#     html.append("<tbody>")

#     for _, row in df.iterrows():

#         def to_float(x):
#             try:
#                 return float(x)
#             except:
#                 return None

#         g = to_float(row["Gemini"])
#         p = to_float(row["Perplexity"])

#         if g is None or p is None:
#             gcls = pcls = "neutral-cell"
#         else:
#             if abs(g - p) < 1e-9:
#                 gcls = pcls = "neutral-cell"
#             elif g > p:
#                 gcls = "winner-cell"
#                 pcls = "loser-cell"
#             else:
#                 pcls = "winner-cell"
#                 gcls = "loser-cell"

#         html.append(
#             f"<tr>"
#             f"<td>{row['Metric']}</td>"
#             f"<td class='{gcls}'>{row['Gemini']}</td>"
#             f"<td class='{pcls}'>{row['Perplexity']}</td>"
#             f"<td class='small'>{row['Good Range']}</td>"
#             f"</tr>"
#         )

#     html.append("</tbody></table>")

#     if overall_winner:
#         html.append(
#             f"<div style='margin-top:10px; background:#eef7ff; padding:8px; border-radius:6px;'>"
#             f"🏆 <b>Overall Winner:</b> {overall_winner.upper()} </div>"
#         )

#     html.append("</div>")
#     return "\n".join(html)

# # =========================================================
# #               SESSION STATE INIT
# # =========================================================
# if "query_history" not in st.session_state:
#     st.session_state.query_history = []
# if "last_result" not in st.session_state:
#     st.session_state.last_result = None
# if "current_answer" not in st.session_state:
#     st.session_state.current_answer = ""
# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = f"user_session_{datetime.now().timestamp()}"

# # =========================================================
# #                     PAGE HEADER
# # =========================================================
# st.markdown('<div class="main-header">🤖 Adaptive RAG System — Metrics Dashboard</div>', unsafe_allow_html=True)

# left, right = st.columns([2, 1])

# # =========================================================
# #                       LEFT COLUMN
# # =========================================================
# with left:
#     st.subheader("Ask a Question")
#     question = st.text_area("Your question:", height=110)

#     if st.button("🚀 Run Query", use_container_width=True):
#         if not question.strip():
#             st.error("Please enter a valid question.")
#             st.stop()

#         from src.workflow.graph import app
#         config = {"configurable": {"thread_id": st.session_state.thread_id}}

#         final_state = None
#         for output in app.stream({"question": question}, config=config):
#             for _, v in output.items():
#                 final_state = v

#         st.session_state.last_result = final_state
#         if final_state:
#             ans = format_response(final_state)
#             st.session_state.query_history.append({"question": question, "answer": ans})
#             st.session_state.current_answer = ans

#     st.markdown("---")

#     # Display results
#     if st.session_state.last_result:
#         result = st.session_state.last_result

#         st.markdown("### 🎯 Final Answer")
#         st.success(f"Selected Model: {result.get('chosen_model', 'N/A')}")
#         st.markdown(f"<div class='model-box selected-model'>{format_response(result)}</div>", unsafe_allow_html=True)

#         if result.get("validation_reasoning"):
#             st.markdown("### 🧠 Validation Reasoning")
#             st.markdown(f"<div class='validation-box'>{result['validation_reasoning']}</div>", unsafe_allow_html=True)

#         if result.get("documents"):
#             st.markdown("### 📚 Retrieved Sources")
#             unique = set()
#             for d in result["documents"]:
#                 try:
#                     src = d.metadata.get("source", "Unknown")
#                 except:
#                     src = "Unknown"
#                 unique.add(src)

#             for i, s in enumerate(sorted(unique), 1):
#                 st.markdown(f"<div class='source-box'>{i}. {s}</div>", unsafe_allow_html=True)

#         # Metrics
#         metrics = extract_metrics(result)
#         df = build_metrics_table(
#             metrics["gemini_metrics"],
#             metrics["perplexity_metrics"],
#             metrics["gemini_score"],
#             metrics["perplexity_score"]
#         )

#         winner = None
#         if metrics["gemini_score"] is not None and metrics["perplexity_score"] is not None:
#             winner = "gemini" if metrics["gemini_score"] >= metrics["perplexity_score"] else "perplexity"

#         st.markdown("### 📈 Metric Evaluation")
#         html = render_html_metrics_table(df, metrics["gemini_score"], metrics["perplexity_score"], winner)
#         st.markdown(html, unsafe_allow_html=True)

#         with st.expander("Raw Metric Data"):
#             st.json(metrics)

# # =========================================================
# #                      RIGHT COLUMN (WINNER MOVED HERE)
# # =========================================================
# with right:
#     st.subheader("Parallel Model Outputs")

#     if st.session_state.last_result:
#         r = st.session_state.last_result

#         # Gemini output
#         st.markdown("#### 🔷 Gemini Output")
#         st.markdown(f"<div class='model-box'>{r.get('gemini_answer', 'N/A')}</div>", unsafe_allow_html=True)

#         # Perplexity output
#         st.markdown("#### 🔶 Perplexity Output")
#         st.markdown(f"<div class='model-box'>{r.get('perplexity_answer', 'N/A')}</div>", unsafe_allow_html=True)

#         # -------------------------------
#         # NEW: WINNER SECTION ON RIGHT SIDE
#         # -------------------------------
#         st.markdown("### 🏆 Winner (Comparison)")

#         metrics = extract_metrics(r)
#         gem_score = metrics["gemini_score"]
#         perp_score = metrics["perplexity_score"]

#         if gem_score is not None and perp_score is not None:
#             winner = "Gemini" if gem_score >= perp_score else "Perplexity"

#             st.success(f"**Winner: {winner} 🎉**")

#             st.markdown(
#                 f"""
#                 <div class='model-box selected-model'>
#                     <b>Gemini Score:</b> {gem_score:.4f}<br>
#                     <b>Perplexity Score:</b> {perp_score:.4f}
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )
#         else:
#             st.info("Winner unavailable (metric scores missing).")

#     else:
#         st.info("Run a query to see model outputs.")


#Updated metrics returns code
# app.py — Adaptive RAG System (Streamlit UI, metrics-enabled)
# import streamlit as st
# from dotenv import load_dotenv
# import os
# import json
# from datetime import datetime
# from typing import Any, Dict, Optional
# import pandas as pd

# # Load environment
# load_dotenv()

# st.set_page_config(
#     page_title="Adaptive RAG System",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # =========================================================
# #                     CSS STYLES
# # =========================================================
# st.markdown(
#     """
#     <style>
#       .main-header { font-size: 2.4rem; color: #1f77b4; text-align:center; font-weight:700; margin-bottom:10px;}
#       .model-box { border:1px solid #e0e0e0; border-radius:8px; padding:12px; background:#fafafa; }
#       .selected-model { border-color:#4CAF50; background:#f0f8f0; box-shadow: 0 4px 8px rgba(76,175,80,0.08); }
#       .validation-box { border:1px solid #ff9800; border-radius:8px; padding:10px; background:#fff8ef; }
#       .source-box { border:1px solid #d0d7de; border-radius:6px; padding:8px; background:#f5f7fa; margin-bottom:6px;}
#       .metric-table { border-collapse: collapse; width:100%; }
#       .metric-table th, .metric-table td { border: 1px solid #e6e6e6; padding:8px; text-align:center; }
#       .metric-table th { background: #fafafa; }
#       .winner-cell { background: #e6f4ea; font-weight:700; }
#       .loser-cell { background: #fff6f6; }
#       .neutral-cell { background:#ffffff; }
#       .small { font-size:0.9rem; color:#666; }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # =========================================================
# #                     UTILITY FUNCTIONS
# # =========================================================
# def format_response(result: Dict[str, Any]) -> str:
#     if not isinstance(result, dict):
#         return str(result)
#     if "generation" in result:
#         return result["generation"]
#     if "answer" in result:
#         return result["answer"]
#     return json.dumps(result, indent=2)


# # -------------------- EXTRACT METRICS --------------------
# def extract_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Accepts output from updated generate.py:
#         result["validation_result"] = { winner, scores, metrics }
#     Ensures table always displays correctly.
#     """

#     default = {
#         "rouge1": None, "rouge2": None, "rougeL": None,
#         "bleu": None, "meteor": None, "bert_f1": None,
#         "cosine_sim": None, "faithfulness": None,
#         "terminology_precision": None, "coverage": None
#     }

#     output = {
#         "gemini_metrics": dict(default),
#         "perplexity_metrics": dict(default),
#         "gemini_score": None,
#         "perplexity_score": None
#     }

#     # NEW: updated generate.py always puts metrics here
#     vr = result.get("validation_result", None)
#     if vr and isinstance(vr, dict):
#         output["gemini_metrics"] = vr.get("gemini_metrics", default)
#         output["perplexity_metrics"] = vr.get("perplexity_metrics", default)
#         output["gemini_score"] = vr.get("gemini_score")
#         output["perplexity_score"] = vr.get("perplexity_score")
#         return output

#     # Fallback (very unlikely)
#     return output


# # -------------------- METRIC TABLE DATAFRAME --------------------
# def build_metrics_table(gem, perp, gem_score, perp_score):
#     rows = [
#         ("ROUGE-1", "rouge1"),
#         ("ROUGE-2", "rouge2"),
#         ("ROUGE-L", "rougeL"),
#         ("BLEU", "bleu"),
#         ("METEOR", "meteor"),
#         ("BERT-F1", "bert_f1"),
#         ("CosineSim", "cosine_sim"),
#         ("Faithfulness", "faithfulness"),
#         ("Terminology Precision", "terminology_precision"),
#         ("Coverage", "coverage"),
#     ]

#     ranges = {
#         "rouge1": "0.4–0.6 OK, >0.6 strong",
#         "rouge2": "0.2–0.4 OK, >0.4 strong",
#         "rougeL": "0.4–0.6 OK, >0.6 strong",
#         "bleu": "0.2–0.4 OK, >0.4 strong",
#         "meteor": "0.2–0.4 OK, >0.4 strong",
#         "bert_f1": ">0.4 good, >0.6 strong",
#         "cosine_sim": ">0.7 good",
#         "faithfulness": ">0.6 good",
#         "terminology_precision": ">0.6 good",
#         "coverage": ">0.6 good",
#     }

#     table = []
#     for label, key in rows:

#         def fmt(x):
#             try:
#                 return f"{float(x):.3f}"
#             except:
#                 return "n/a"

#         table.append({
#             "Metric": label,
#             "Gemini": fmt(gem.get(key)),
#             "Perplexity": fmt(perp.get(key)),
#             "Good Range": ranges[key]
#         })

#     table.append({
#         "Metric": "Composite Score",
#         "Gemini": f"{gem_score:.4f}" if gem_score else "n/a",
#         "Perplexity": f"{perp_score:.4f}" if perp_score else "n/a",
#         "Good Range": "Higher is better"
#     })

#     return pd.DataFrame(table)


# # -------------------- RENDER HTML TABLE --------------------
# def render_html_metrics_table(df, gem_score, perp_score, overall_winner):
#     html = []
#     html.append("<div class='model-box'><h4>📊 Metric Comparison</h4>")
#     html.append("<table class='metric-table'>")
#     html.append("<thead><tr><th>Metric</th><th>Gemini</th><th>Perplexity</th><th>Good Range</th></tr></thead><tbody>")

#     for _, row in df.iterrows():

#         def try_float(v):
#             try:
#                 return float(v)
#             except:
#                 return None

#         g = try_float(row["Gemini"])
#         p = try_float(row["Perplexity"])

#         if g is None or p is None:
#             gcls = pcls = "neutral-cell"
#         else:
#             if abs(g - p) < 1e-9:
#                 gcls = pcls = "neutral-cell"
#             elif g > p:
#                 gcls = "winner-cell"
#                 pcls = "loser-cell"
#             else:
#                 pcls = "winner-cell"
#                 gcls = "loser-cell"

#         html.append(
#             f"<tr>"
#             f"<td>{row['Metric']}</td>"
#             f"<td class='{gcls}'>{row['Gemini']}</td>"
#             f"<td class='{pcls}'>{row['Perplexity']}</td>"
#             f"<td class='small'>{row['Good Range']}</td>"
#             f"</tr>"
#         )

#     html.append("</tbody></table>")

#     if overall_winner:
#         html.append(
#             f"<div style='margin-top:8px; padding:5px; background:#eef7ff; border-radius:6px;'>"
#             f"🏆 <b>Overall Winner:</b> {overall_winner.upper()}</div>"
#         )

#     html.append("</div>")
#     return "\n".join(html)


# # =========================================================
# #               STREAMLIT SESSION STATE
# # =========================================================
# if "query_history" not in st.session_state:
#     st.session_state.query_history = []
# if "last_result" not in st.session_state:
#     st.session_state.last_result = None
# if "current_answer" not in st.session_state:
#     st.session_state.current_answer = ""
# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = f"user_session_{datetime.now().timestamp()}"

# # =========================================================
# #               UI LAYOUT
# # =========================================================
# st.markdown('<div class="main-header">🤖 Adaptive RAG System — Metrics Dashboard</div>', unsafe_allow_html=True)

# left, right = st.columns([2, 1])

# # =========================================================
# #                       LEFT COLUMN
# # =========================================================
# with left:
#     st.subheader("Ask a Question")
#     question = st.text_area("Your question:", height=110)

#     if st.button("🚀 Run Query", use_container_width=True):

#         if not question.strip():
#             st.error("Please enter a valid question.")
#             st.stop()

#         st.session_state.last_result = None
#         st.session_state.current_question = question

#         from src.workflow.graph import app

#         config = {"configurable": {"thread_id": st.session_state.thread_id}}
#         final_state = None

#         try:
#             for output in app.stream({"question": question}, config=config):
#                 for _, v in output.items():
#                     final_state = v
#         except Exception as e:
#             st.error(f"Execution error: {e}")
#             st.stop()

#         st.session_state.last_result = final_state

#         if final_state:
#             ans = format_response(final_state)
#             st.session_state.query_history.append({"question": question, "answer": ans})
#             st.session_state.current_answer = ans

#     st.markdown("---")

#     # =========================================================
#     #                     DISPLAY RESULTS
#     # =========================================================
#     if st.session_state.last_result:
#         result = st.session_state.last_result

#         st.markdown("### 🎯 Final Answer")
#         model = result.get("chosen_model", "N/A")
#         st.success(f"Selected Model: {model}")

#         st.markdown(f"<div class='model-box selected-model'>{format_response(result)}</div>", unsafe_allow_html=True)

#         # Validation reasoning
#         if result.get("validation_reasoning"):
#             st.markdown("### 🧠 Validation Reasoning")
#             st.markdown(f"<div class='validation-box'>{result['validation_reasoning']}</div>", unsafe_allow_html=True)

#         # Retrieved sources
#         if result.get("documents"):
#             st.markdown("### 📚 Retrieved Sources")
#             unique = set()
#             for d in result["documents"]:
#                 try:
#                     src = d.metadata.get("source", "Unknown")
#                 except:
#                     src = "Unknown"
#                 unique.add(src)

#             for i, s in enumerate(sorted(unique), 1):
#                 st.markdown(f"<div class='source-box'>{i}. {s}</div>", unsafe_allow_html=True)

#         # =========================================================
#         #                METRIC EXTRACTION & DISPLAY
#         # =========================================================
#         st.markdown("### 📈 Metric Evaluation")

#         metrics = extract_metrics(result)

#         df = build_metrics_table(
#             metrics["gemini_metrics"],
#             metrics["perplexity_metrics"],
#             metrics["gemini_score"],
#             metrics["perplexity_score"]
#         )

#         winner = None
#         if metrics["gemini_score"] is not None and metrics["perplexity_score"] is not None:
#             winner = "gemini" if metrics["gemini_score"] >= metrics["perplexity_score"] else "perplexity"

#         html = render_html_metrics_table(df, metrics["gemini_score"], metrics["perplexity_score"], winner)
#         st.markdown(html, unsafe_allow_html=True)

#         with st.expander("Raw Metric Data"):
#             st.json(metrics)

# # =========================================================
# #                      RIGHT COLUMN
# # =========================================================
# with right:
#     st.subheader("Parallel Model Outputs")

#     if st.session_state.last_result:
#         r = st.session_state.last_result

#         st.markdown("#### 🔷 Gemini Output")
#         st.markdown(f"<div class='model-box'>{r.get('gemini_answer', 'N/A')}</div>", unsafe_allow_html=True)

#         st.markdown("#### 🔶 Perplexity Output")
#         st.markdown(f"<div class='model-box'>{r.get('perplexity_answer', 'N/A')}</div>", unsafe_allow_html=True)
#     else:
#         st.info("Outputs will appear here after running a query.")



# # app.py — Adaptive RAG System (Streamlit UI, metrics-enabled)
# import streamlit as st
# from dotenv import load_dotenv
# import os
# import json
# from datetime import datetime
# from typing import Any, Dict, Optional
# import pandas as pd

# # Load environment
# load_dotenv()

# st.set_page_config(
#     page_title="Adaptive RAG System",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ---------- Styles ----------
# st.markdown(
#     """
#     <style>
#       .main-header { font-size: 2.4rem; color: #1f77b4; text-align:center; font-weight:700; margin-bottom:10px;}
#       .model-box { border:1px solid #e0e0e0; border-radius:8px; padding:12px; background:#fafafa; }
#       .selected-model { border-color:#4CAF50; background:#f0f8f0; box-shadow: 0 4px 8px rgba(76,175,80,0.08); }
#       .validation-box { border:1px solid #ff9800; border-radius:8px; padding:10px; background:#fff8ef; }
#       .source-box { border:1px solid #d0d7de; border-radius:6px; padding:8px; background:#f5f7fa; margin-bottom:6px;}
#       .metric-good { color: #2E7D32; font-weight:600; }
#       .metric-bad { color: #C62828; font-weight:600; }
#       .small { font-size:0.9rem; color:#666; }
#       .metric-table { border-collapse: collapse; width:100%; }
#       .metric-table th, .metric-table td { border: 1px solid #e6e6e6; padding:8px; text-align:center; }
#       .metric-table th { background: #fafafa; }
#       .winner-cell { background: #e6f4ea; font-weight:700; }
#       .loser-cell { background: #fff6f6; }
#       .neutral-cell { background:#ffffff; }
#       .legend { font-size:0.9rem; }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # ---------- Utilities ----------
# def format_response(result: Dict[str, Any]) -> str:
#     if not isinstance(result, dict):
#         return str(result)
#     if "generation" in result:
#         return result["generation"]
#     if "answer" in result:
#         return result["answer"]
#     return json.dumps(result, indent=2)

# def extract_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Find metrics dicts (gemini/perplexity) and composite scores if present.
#     Handles several possible shapes of result:
#       - result['validation_result'] like evaluate_answers(...) returned dict
#       - top-level keys 'gemini_metrics' and 'perplexity_metrics'
#       - top-level 'gemini_score' and 'perplexity_score'
#     Returns a normalized dict:
#       {
#         "gemini_metrics": {...},
#         "perplexity_metrics": {...},
#         "gemini_score": float or None,
#         "perplexity_score": float or None
#       }
#     """
#     default_metrics = {
#         "rouge1": None, "rouge2": None, "rougeL": None, "bleu": None,
#         "meteor": None, "bert_f1": None, "cosine_sim": None,
#         "faithfulness": None, "terminology_precision": None, "coverage": None
#     }

#     out = {
#         "gemini_metrics": dict(default_metrics),
#         "perplexity_metrics": dict(default_metrics),
#         "gemini_score": None,
#         "perplexity_score": None,
#     }

#     # Case 1: validation_result present
#     if "validation_result" in result and isinstance(result["validation_result"], dict):
#         vr = result["validation_result"]
#         out["gemini_metrics"] = vr.get("gemini_metrics", out["gemini_metrics"])
#         out["perplexity_metrics"] = vr.get("perplexity_metrics", out["perplexity_metrics"])
#         out["gemini_score"] = vr.get("gemini_score", out["gemini_score"])
#         out["perplexity_score"] = vr.get("perplexity_score", out["perplexity_score"])
#         return out

#     # Case 2: top-level gemini_metrics / perplexity_metrics
#     if "gemini_metrics" in result or "perplexity_metrics" in result:
#         out["gemini_metrics"] = result.get("gemini_metrics", out["gemini_metrics"])
#         out["perplexity_metrics"] = result.get("perplexity_metrics", out["perplexity_metrics"])
#         out["gemini_score"] = result.get("gemini_score", out["gemini_score"])
#         out["perplexity_score"] = result.get("perplexity_score", out["perplexity_score"])
#         return out

#     # Case 3: sometimes evaluate_answers result was in 'validation' or top-level keys
#     for key in ("validation", "metrics", "eval_result"):
#         if key in result and isinstance(result[key], dict):
#             candidate = result[key]
#             out["gemini_metrics"] = candidate.get("gemini_metrics", out["gemini_metrics"])
#             out["perplexity_metrics"] = candidate.get("perplexity_metrics", out["perplexity_metrics"])
#             out["gemini_score"] = candidate.get("gemini_score", out["gemini_score"])
#             out["perplexity_score"] = candidate.get("perplexity_score", out["perplexity_score"])
#             return out

#     # Case 4: perhaps metrics stored directly as keys in result
#     gm = {}
#     pm = {}
#     found_any = False
#     for m in default_metrics.keys():
#         if m in result:
#             gm[m] = result.get(m)
#             found_any = True
#     if found_any:
#         out["gemini_metrics"] = gm
#         # no perplexity metrics in this format
#         out["perplexity_metrics"] = pm or out["perplexity_metrics"]
#         out["gemini_score"] = result.get("gemini_score", out["gemini_score"])
#         out["perplexity_score"] = result.get("perplexity_score", out["perplexity_score"])
#         return out

#     # Nothing found — return defaults
#     return out

# def build_metrics_table(gem: Dict[str, Any], perp: Dict[str, Any], gem_score: Optional[float], perp_score: Optional[float]):
#     """
#     Returns a pandas DataFrame with rows: Metric, Gemini, Perplexity, GoodRange
#     """
#     # Define the metric names we want to show (and display names)
#     rows = [
#         ("ROUGE-1", "rouge1"),
#         ("ROUGE-2", "rouge2"),
#         ("ROUGE-L", "rougeL"),
#         ("BLEU", "bleu"),
#         ("METEOR", "meteor"),
#         ("BERT-F1", "bert_f1"),
#         ("CosineSim", "cosine_sim"),
#         ("Faithfulness", "faithfulness"),
#         ("Terminology Precision", "terminology_precision"),
#         ("Coverage", "coverage"),
#     ]

#     # Good score ranges (informational)
#     good_ranges = {
#         "rouge1": "0.4–0.6 (decent), >0.6 excellent",
#         "rouge2": "0.2–0.4 (decent), >0.4 excellent",
#         "rougeL": "0.4–0.6 (decent), >0.6 excellent",
#         "bleu": "0.2–0.4 (decent), >0.4 excellent",
#         "meteor": "0.2–0.4 (decent), >0.4 excellent",
#         "bert_f1": ">0.4 good, >0.6 strong",
#         "cosine_sim": ">0.7 good, >0.85 excellent",
#         "faithfulness": ">0.6 good",
#         "terminology_precision": ">0.6 good",
#         "coverage": ">0.6 good"
#     }

#     table_rows = []
#     for display, key in rows:
#         gval = gem.get(key) if gem else None
#         pval = perp.get(key) if perp else None

#         # Format numbers
#         def fmt(v):
#             if v is None:
#                 return "n/a"
#             try:
#                 return f"{float(v):.3f}"
#             except Exception:
#                 return str(v)

#         table_rows.append({
#             "Metric": display,
#             "Gemini": fmt(gval),
#             "Perplexity": fmt(pval),
#             "Good Range": good_ranges.get(key, "—")
#         })

#     # Add composite/score row
#     table_rows.append({
#         "Metric": "Composite Score",
#         "Gemini": f"{gem_score:.4f}" if gem_score is not None else "n/a",
#         "Perplexity": f"{perp_score:.4f}" if perp_score is not None else "n/a",
#         "Good Range": "higher is better (composite)"
#     })

#     df = pd.DataFrame(table_rows)
#     return df

# def render_html_metrics_table(df: pd.DataFrame, gem_score: Optional[float], perp_score: Optional[float], overall_winner: Optional[str]):
#     """
#     Render a HTML table highlighting the winner for the composite score and winners per-row.
#     """
#     # Build HTML headers
#     html = ["<div class='model-box'><h4 style='margin:6px 0;'>📊 Metric Comparison</h4>"]
#     html.append("<table class='metric-table'>")
#     # header
#     html.append("<thead><tr><th>Metric</th><th>Gemini</th><th>Perplexity</th><th>Good Range</th></tr></thead>")
#     html.append("<tbody>")

#     # For each row determine highlight for numeric cells (compare floats where possible)
#     for _, row in df.iterrows():
#         metric = row["Metric"]
#         gcell = row["Gemini"]
#         pcell = row["Perplexity"]
#         good = row["Good Range"]

#         # try parse numeric
#         def to_num(s):
#             try:
#                 return float(s)
#             except Exception:
#                 return None

#         gnum = to_num(gcell)
#         pnum = to_num(pcell)

#         # Decide cell classes
#         if gnum is not None and pnum is not None:
#             if abs(gnum - pnum) < 1e-9:
#                 gclass = pclass = "neutral-cell"
#             elif gnum > pnum:
#                 gclass = "winner-cell"
#                 pclass = "loser-cell"
#             else:
#                 pclass = "winner-cell"
#                 gclass = "loser-cell"
#         else:
#             # non-numeric -> neutral styling
#             gclass = pclass = "neutral-cell"

#         html.append(f"<tr>")
#         html.append(f"<td>{metric}</td>")
#         html.append(f"<td class='{gclass}'>{gcell}</td>")
#         html.append(f"<td class='{pclass}'>{pcell}</td>")
#         html.append(f"<td class='small'>{good}</td>")
#         html.append(f"</tr>")

#     html.append("</tbody></table>")

#     # Add summary / winner banner
#     if overall_winner:
#         winner_label = overall_winner.upper()
#         html.append(f"<div style='margin-top:10px; padding:8px; border-radius:6px; background:#f0f8ff;'>"
#                     f"🏆 <strong>Overall winner:</strong> <span style='font-weight:800;color:#0b63ce'>{winner_label}</span>"
#                     f"</div>")
#     else:
#         html.append(f"<div style='margin-top:10px; padding:8px; border-radius:6px; background:#fff8ef;'>"
#                     f"⚠️ No overall winner (scores missing)</div>")

#     html.append("</div>")
#     return "\n".join(html)

# # ---------- Session state init ----------
# if "query_history" not in st.session_state:
#     st.session_state.query_history = []
# if "last_result" not in st.session_state:
#     st.session_state.last_result = None
# if "feedback_status" not in st.session_state:
#     st.session_state.feedback_status = ""
# if "current_answer" not in st.session_state:
#     st.session_state.current_answer = ""
# if "current_question" not in st.session_state:
#     st.session_state.current_question = ""
# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = f"user_session_{datetime.now().timestamp()}"

# # ---------- UI layout ----------
# st.markdown('<div class="main-header">🤖 Adaptive RAG System — Metrics Dashboard</div>', unsafe_allow_html=True)

# sidebar = st.sidebar
# with sidebar:
#     st.header("Session Overview")
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Total Queries", len(st.session_state.query_history))
#     with col2:
#         if st.session_state.last_result and st.session_state.last_result.get("chosen_model"):
#             cm = st.session_state.last_result["chosen_model"]
#             display = cm.split()[0].upper() if " " in cm else cm.upper()
#             st.metric("Best Model", display)
#         else:
#             st.metric("Best Model", "N/A")
#     st.divider()
#     st.subheader("History (last 5)")
#     if st.session_state.query_history:
#         for i, entry in enumerate(reversed(st.session_state.query_history[-5:]), 1):
#             with st.expander(f"Q{i}: {entry['question'][:60]}...", expanded=False):
#                 st.write(entry["answer"][:300] + ("..." if len(entry["answer"])>300 else ""))
#     else:
#         st.info("No queries yet.")

# # Main columns
# left_col, right_col = st.columns([2, 1])

# with left_col:
#     st.subheader("Ask a Question")
#     question = st.text_area("Enter your question:", height=100, placeholder="e.g., What is RAG evaluation?")

#     btn_col1, btn_col2 = st.columns([1,1])
#     with btn_col1:
#         if st.button("🚀 Get Answer", use_container_width=True):
#             if not question.strip():
#                 st.error("Please enter a valid question.")
#             else:
#                 st.session_state.current_question = question
#                 st.session_state.last_result = None
#                 st.session_state.current_answer = ""
#                 st.session_state.feedback_status = ""

#                 try:
#                     from src.workflow.graph import app
#                 except Exception as e:
#                     st.error(f"Failed to import workflow: {e}")
#                     st.stop()

#                 config = {"configurable": {"thread_id": st.session_state.thread_id}}
#                 full_output = []
#                 try:
#                     for output in app.stream({"question": question}, config=config):
#                         full_output.append(output)
#                     # take last output's value
#                     result = None
#                     if full_output:
#                         last_output = full_output[-1]
#                         # last_output usually is dict like {thread_id: state}
#                         for _, v in last_output.items():
#                             result = v
#                             break
#                     st.session_state.last_result = result
#                     if result:
#                         # append to history
#                         gen = format_response(result)
#                         st.session_state.query_history.append({"question": question, "answer": gen})
#                         st.session_state.current_answer = gen
#                 except Exception as e:
#                     st.error(f"Processing error: {e}")
#                     st.session_state.last_result = {
#                         "generation": f"Error: {e}",
#                         "gemini_answer": "Error",
#                         "perplexity_answer": "Error",
#                         "chosen_model": "error",
#                         "validation_reasoning": str(e)
#                     }

#     with btn_col2:
#         if st.button("🧹 Clear History", use_container_width=True):
#             st.session_state.query_history = []
#             st.session_state.last_result = None
#             st.session_state.current_answer = ""
#             st.session_state.current_question = ""
#             st.experimental_rerun()

#     st.markdown("---")

#     # Results display
#     if st.session_state.last_result:
#         res = st.session_state.last_result
#         # --- top summary ---
#         st.markdown("### 🎯 Final Answer")
#         final_ans = format_response(res)
#         chosen_model = res.get("chosen_model", "N/A")
#         if "fallback" in chosen_model:
#             st.warning(f"Selected Model: {chosen_model}")
#         elif "error" in chosen_model:
#             st.error("System encountered an error")
#         else:
#             st.success(f"Selected Model: {chosen_model}")

#         st.markdown(f"<div class='model-box selected-model'>{final_ans}</div>", unsafe_allow_html=True)

#         # Rewritten and routing info
#         original_q = res.get("original_question", res.get("question", "N/A"))
#         rewritten_q = res.get("rewritten_question", res.get("question", None))
#         route_to = res.get("route", res.get("routed_to", res.get("route_to", None)))

#         st.markdown("### 🔍 Query Info")
#         st.markdown(f"**Original:** {original_q}")
#         if rewritten_q:
#             st.markdown(f"**Rewritten:** {rewritten_q}")
#         if route_to:
#             st.markdown(f"**Routed to:** {route_to}")

#         # Validation reasoning / explanation
#         if res.get("validation_reasoning"):
#             st.markdown("### 🧠 Validation Reasoning")
#             st.markdown(f"<div class='validation-box'>{res.get('validation_reasoning')}</div>", unsafe_allow_html=True)

#         # Retrieved docs
#         if res.get("documents"):
#             st.markdown("### 📚 Retrieved Sources")
#             unique = set()
#             for d in res.get("documents", []):
#                 try:
#                     src = d.metadata.get("source", getattr(d, "source", "Unknown"))
#                 except Exception:
#                     # fallback
#                     src = getattr(d, "source", "Unknown")
#                 unique.add(src)
#             for i, src in enumerate(sorted(unique), 1):
#                 st.markdown(f"<div class='source-box'>**{i}.** {src}</div>", unsafe_allow_html=True)

#         # Extract metrics and render table
#         metrics_info = extract_metrics(res)
#         gem_metrics = metrics_info["gemini_metrics"]
#         perp_metrics = metrics_info["perplexity_metrics"]
#         gem_score = metrics_info["gemini_score"]
#         perp_score = metrics_info["perplexity_score"]

#         # If top-level validation_result exists, use it for display label
#         if "validation_result" in res and isinstance(res["validation_result"], dict):
#             st.markdown("### 📈 Metric Evaluation (from validator)")
#         else:
#             st.markdown("### 📈 Metric Evaluation (computed)")

#         df_metrics = build_metrics_table(gem_metrics or {}, perp_metrics or {}, gem_score, perp_score)

#         # Determine overall winner
#         overall_winner = None
#         try:
#             if gem_score is not None and perp_score is not None:
#                 overall_winner = "gemini" if float(gem_score) >= float(perp_score) else "perplexity"
#             elif res.get("chosen_model"):
#                 overall_winner = res.get("chosen_model")
#         except Exception:
#             overall_winner = res.get("chosen_model", None)

#         # Render as HTML table with highlights
#         html_table = render_html_metrics_table(df_metrics, gem_score, perp_score, overall_winner)
#         st.markdown(html_table, unsafe_allow_html=True)

#         # Also show the raw metrics dict (collapsible)
#         with st.expander("Show raw metric objects"):
#             st.write({"gemini_metrics": gem_metrics, "perplexity_metrics": perp_metrics, "gemini_score": gem_score, "perplexity_score": perp_score})

#         # Feedback buttons
#         st.markdown("---")
#         st.subheader("📊 Feedback")
#         c1, c2 = st.columns([1,1])
#         if c1.button("👍 Helpful"):
#             st.session_state.feedback_status = "positive"
#             # log
#             log_dir = "logs"
#             os.makedirs(log_dir, exist_ok=True)
#             with open(os.path.join(log_dir, "feedback_log.txt"), "a", encoding="utf-8") as f:
#                 f.write(json.dumps({
#                     "ts": datetime.now().isoformat(),
#                     "question": original_q,
#                     "answer": final_ans,
#                     "rating": "positive"
#                 }) + "\n")
#             st.success("Feedback saved — thanks!")
#         if c2.button("👎 Not helpful"):
#             st.session_state.feedback_status = "negative"
#             os.makedirs("logs", exist_ok=True)
#             with open(os.path.join("logs", "feedback_log.txt"), "a", encoding="utf-8") as f:
#                 f.write(json.dumps({
#                     "ts": datetime.now().isoformat(),
#                     "question": original_q,
#                     "answer": final_ans,
#                     "rating": "negative"
#                 }) + "\n")
#             st.warning("Feedback saved — thanks!")

#     else:
#         st.info("Enter a question and click 'Get Answer' to run the Adaptive RAG pipeline.")

# with right_col:
#     st.subheader("Model Responses (parallel)")
#     if st.session_state.last_result:
#         r = st.session_state.last_result
#         gem = r.get("gemini_answer", "Not available")
#         perp = r.get("perplexity_answer", "Not available")
#         st.markdown("#### 🔷 Gemini")
#         st.markdown(f"<div class='model-box'>{gem}</div>", unsafe_allow_html=True)
#         st.markdown("#### 🔶 Perplexity")
#         st.markdown(f"<div class='model-box'>{perp}</div>", unsafe_allow_html=True)
#     else:
#         st.info("Model outputs appear here after you run a query.")

# # Footer
# st.markdown("---")
# st.markdown("<div style='text-align:center;color:#666'>Adaptive RAG System | Multi-Model Evaluation</div>", unsafe_allow_html=True)

# import streamlit as st
# from dotenv import load_dotenv
# import os
# import json
# from datetime import datetime
# from langchain_core.documents import Document

# # Load environment variables
# load_dotenv()

# # Streamlit app configuration - Classic Theme
# st.set_page_config(
#     page_title="Adaptive RAG System", 
#     page_icon="🤖", 
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS for classic styling
# st.markdown("""
# <style>
#     .main-header {
#         font-size: 2.5rem;
#         color: #1f77b4;
#         text-align: center;
#         margin-bottom: 2rem;
#         font-weight: bold;
#     }
#     .model-box {
#         border: 2px solid #e0e0e0;
#         border-radius: 10px;
#         padding: 1.5rem;
#         margin: 1rem 0;
#         background-color: #fafafa;
#     }
#     .selected-model {
#         border-color: #4CAF50;
#         background-color: #f0f8f0;
#         box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
#     }
#     .validation-box {
#         border: 2px solid #ff9800;
#         border-radius: 10px;
#         padding: 1.5rem;
#         margin: 1rem 0;
#         background-color: #fff3e0;
#     }
#     .source-box {
#         border: 1px solid #b0bec5;
#         border-radius: 5px;
#         padding: 1rem;
#         margin: 0.5rem 0;
#         background-color: #eceff1;
#     }
#     .metric-box {
#         text-align: center;
#         padding: 1rem;
#         border-radius: 5px;
#         background-color: #f5f5f5;
#     }
#     .error-box {
#         border: 2px solid #f44336;
#         border-radius: 10px;
#         padding: 1.5rem;
#         margin: 1rem 0;
#         background-color: #ffebee;
#     }
# </style>
# """, unsafe_allow_html=True)

# # --- Utility functions ---
# def format_response(result):
#     """Extract response from workflow result."""
#     if isinstance(result, dict) and "generation" in result:
#         return result["generation"]
#     elif isinstance(result, dict) and "answer" in result:
#         return result["answer"]
#     else:
#         return str(result)

# def log_feedback(question, answer, rating):
#     """Log user feedback to a file."""
#     feedback_entry = {
#         "timestamp": datetime.now().isoformat(),
#         "question": question,
#         "answer": answer,
#         "rating": rating
#     }
#     feedback_dir = "logs"
#     feedback_file = os.path.join(feedback_dir, "feedback_log.txt")
#     try:
#         os.makedirs(feedback_dir, exist_ok=True)
#         with open(feedback_file, "a", encoding="utf-8") as f:
#             f.write(json.dumps(feedback_entry) + "\n")
#         return f"✅ Feedback logged successfully: {rating}"
#     except Exception as e:
#         return f"⚠️ Failed to log feedback: {str(e)}"

# # --- Initialize session state ---
# if "query_history" not in st.session_state:
#     st.session_state.query_history = []
# if "last_result" not in st.session_state:
#     st.session_state.last_result = None
# if "feedback_status" not in st.session_state:
#     st.session_state.feedback_status = ""
# if "current_answer" not in st.session_state:
#     st.session_state.current_answer = ""
# if "current_question" not in st.session_state:
#     st.session_state.current_question = ""
# if "thread_id" not in st.session_state:
#     st.session_state.thread_id = f"user_session_{datetime.now().timestamp()}"

# # Header
# st.markdown('<div class="main-header">🤖 Adaptive RAG System</div>', unsafe_allow_html=True)

# # Sidebar for history and metrics
# with st.sidebar:
#     st.header("Session Overview")
    
#     # Metrics
#     col1, col2 = st.columns(2)
#     with col1:
#         st.metric("Total Queries", len(st.session_state.query_history))
#     with col2:
#         if st.session_state.last_result and st.session_state.last_result.get("chosen_model"):
#             chosen_model = st.session_state.last_result["chosen_model"]
#             # Handle fallback cases
#             if "fallback" in chosen_model:
#                 display_model = chosen_model.split(" ")[0].upper()
#             else:
#                 display_model = chosen_model.upper()
#             st.metric("Best Model", display_model)
#         else:
#             st.metric("Best Model", "N/A")
    
#     st.divider()
    
#     st.subheader("Query History")
#     if st.session_state.query_history:
#         for i, entry in enumerate(reversed(st.session_state.query_history[-5:]), 1):
#             with st.expander(f"Q{i}: {entry['question'][:50]}...", expanded=False):
#                 st.markdown(f"**Answer:** {entry['answer'][:100]}...")
#     else:
#         st.info("No queries yet.")

# # Main content area
# col1, col2 = st.columns([2, 1])

# with col1:
#     # Input section
#     st.subheader("Ask a Question")
#     question = st.text_area(
#         "Enter your question:", 
#         placeholder="e.g., What are AI agents? How do they work?",
#         height=100
#     )
    
#     # Action buttons
#     btn_col1, btn_col2, btn_col3 = st.columns(3)
#     with btn_col1:
#         if st.button("🚀 Get Answer", use_container_width=True, type="primary"):
#             if not question.strip():
#                 st.error("Please enter a valid question.")
#             else:
#                 try:
#                     with st.spinner("🔄 Processing with multiple AI models..."):
#                         st.session_state.last_result = None
#                         st.session_state.feedback_status = ""
#                         st.session_state.current_answer = ""
#                         st.session_state.current_question = question

#                         try:
#                             from src.workflow.graph import app
#                         except ImportError as e:
#                             st.error(f"Failed to import workflow: {str(e)}")
#                             st.stop()

#                         # SIMPLIFIED CONFIG - No manual event loop management
#                         config = {
#                             "configurable": {"thread_id": st.session_state.thread_id},
#                             "recursion_limit": 100
#                         }
                        
#                         try:
#                             # Collect all outputs
#                             full_output = []
#                             for output in app.stream({"question": question}, config=config):
#                                 full_output.append(output)
                            
#                             # Get the final result from the last output
#                             if full_output:
#                                 last_output = full_output[-1]
#                                 for key, value in last_output.items():
#                                     result = value
#                                     break
                            
#                             st.session_state.last_result = result
                            
#                         except Exception as e:
#                             st.error(f"❌ Processing error: {str(e)}")
#                             st.session_state.last_result = {
#                                 "generation": f"Error: {str(e)}",
#                                 "gemini_answer": "Error during processing",
#                                 "perplexity_answer": "Error during processing", 
#                                 "validation_reasoning": "System encountered an error",
#                                 "chosen_model": "error"
#                             }

#                 except Exception as e:
#                     st.error(f"❌ System error: {str(e)}")

#     with btn_col2:
#         if st.button("🗑️ Clear History", use_container_width=True):
#             st.session_state.query_history = []
#             st.session_state.last_result = None
#             st.session_state.feedback_status = ""
#             st.session_state.current_answer = ""
#             st.session_state.current_question = ""
#             st.session_state.thread_id = f"user_session_{datetime.now().timestamp()}"
#             st.rerun()

#     with btn_col3:
#         if st.button("📊 System Info", use_container_width=True):
#             st.info("""
#             **System Architecture:**
#             - 🤖 Gemini Pro: Text generation
#             - 🔍 Perplexity Sonar: Alternative generation  
#             - 🧠 GPT-4o-mini: Answer validation
#             - 📚 Vector Store: Document retrieval
#             - 🌐 Web Search: Fallback option
            
#             **Workflow:**
#             1. Question routing
#             2. Document retrieval & grading
#             3. Parallel model generation
#             4. AI-powered validation
#             5. Best answer selection
#             """)

# # Display results
# if st.session_state.last_result:
#     result = st.session_state.last_result
#     answer = format_response(result)
    
#     # Store in history (only if we have a valid answer)
#     if question and answer and not answer.startswith("Error:"):
#         # Check if this question is already in history to avoid duplicates
#         existing_questions = [entry['question'] for entry in st.session_state.query_history]
#         if question not in existing_questions:
#             st.session_state.current_answer = answer
#             st.session_state.query_history.append({"question": question, "answer": answer})

#     with col1:
#         # Selected Answer Section
#         st.markdown("---")
#         st.subheader("🎯 Selected Best Answer")
        
#         chosen_model = result.get("chosen_model", "")
#         if chosen_model:
#             if "fallback" in chosen_model:
#                 st.warning(f"**Selected Model: {chosen_model.upper()}** (Fallback mode)")
#             elif "error" in chosen_model:
#                 st.error("**System encountered an error**")
#             else:
#                 st.success(f"**Selected Model: {chosen_model.upper()}** (Validated by GPT-4o-mini)")
        
#         # Display answer with appropriate styling
#         if answer.startswith("Error:"):
#             st.markdown(f'<div class="error-box">{answer}</div>', unsafe_allow_html=True)
#         else:
#             st.markdown(f'<div class="model-box selected-model">{answer}</div>', unsafe_allow_html=True)
        
#         # Validation Reasoning
#         if result.get("validation_reasoning"):
#             st.markdown("### 🧠 Validation Reasoning")
#             st.markdown(f'<div class="validation-box">{result["validation_reasoning"]}</div>', unsafe_allow_html=True)

#         # Retrieved Documents
#         if result.get("documents"):
#             st.markdown("### 📚 Retrieved Sources")
#             unique_sources = set()
#             for doc in result.get("documents", []):
#                 source = doc.metadata.get("source", "Unknown Source")
#                 unique_sources.add(source)
            
#             for i, source in enumerate(sorted(unique_sources), 1):
#                 st.markdown(f'<div class="source-box">**Source {i}:** {source}</div>', unsafe_allow_html=True)

#     with col2:
#         # Parallel Model Responses
#         st.markdown("---")
#         st.subheader("🤖 Model Responses")
        
#         # Gemini Response
#         st.markdown("#### 🔷 Gemini Pro")
#         gemini_answer = result.get("gemini_answer", "Not available")
#         if "Error" in gemini_answer:
#             st.markdown(f'<div class="error-box">{gemini_answer}</div>', unsafe_allow_html=True)
#         else:
#             gemini_class = "model-box selected-model" if result.get("chosen_model") == "gemini" else "model-box"
#             st.markdown(f'<div class="{gemini_class}">{gemini_answer}</div>', unsafe_allow_html=True)
        
#         # Perplexity Response  
#         st.markdown("#### 🔶 Perplexity Sonar")
#         perplexity_answer = result.get("perplexity_answer", "Not available")
#         if "Error" in perplexity_answer:
#             st.markdown(f'<div class="error-box">{perplexity_answer}</div>', unsafe_allow_html=True)
#         else:
#             perplexity_class = "model-box selected-model" if result.get("chosen_model") == "perplexity" else "model-box"
#             st.markdown(f'<div class="{perplexity_class}">{perplexity_answer}</div>', unsafe_allow_html=True)

#     # Feedback Section (only show for successful answers)
#     if not answer.startswith("Error:") and st.session_state.current_answer and st.session_state.current_question:
#         st.markdown("---")
#         st.subheader("📊 Feedback")
        
#         feedback_col1, feedback_col2, feedback_col3 = st.columns([1, 1, 2])
        
#         with feedback_col1:
#             if st.button("👍 Helpful", use_container_width=True, key="helpful_btn"):
#                 st.session_state.feedback_status = log_feedback(
#                     st.session_state.current_question,
#                     st.session_state.current_answer,
#                     "positive"
#                 )
#                 st.rerun()
        
#         with feedback_col2:
#             if st.button("👎 Not Helpful", use_container_width=True, key="not_helpful_btn"):
#                 st.session_state.feedback_status = log_feedback(
#                     st.session_state.current_question,
#                     st.session_state.current_answer,
#                     "negative"
#                 )
#                 st.rerun()
        
#         with feedback_col3:
#             if st.session_state.feedback_status:
#                 if "Failed" in st.session_state.feedback_status:
#                     st.warning(st.session_state.feedback_status)
#                 else:
#                     st.success(st.session_state.feedback_status)

# # Initial state message
# elif not st.session_state.last_result and not question:
#     with col1:
#         st.markdown("---")
#         st.info("""
#         ## 🚀 Welcome to Adaptive RAG System
        
#         **How it works:**
#         1. Enter your question in the text area
#         2. Click **"Get Answer"** to process with multiple AI models
#         3. View parallel responses from Gemini and Perplexity
#         4. See which answer was selected as best by GPT-4o-mini
#         5. Provide feedback to help improve the system
        
#         **Features:**
#         - 🤖 Dual-model generation for better accuracy
#         - 🧠 AI-powered answer validation  
#         - 📚 Smart document retrieval
#         - 🌐 Web search fallback
#         - 📊 Transparent decision process
        
#         **Try asking:**
#         - "What are AI agents?"
#         - "Explain prompt engineering"
#         - "How do language models work?"
#         """)

# # Footer
# st.markdown("---")
# st.markdown(
#     "<div style='text-align: center; color: #666;'>"
#     "Adaptive RAG System | Multi-Model AI Validation | Classic Interface"
#     "</div>", 
#     unsafe_allow_html=True
# )


###############################################################Updated code for context based metrics evaluation#########################
# app.py — Adaptive RAG System (Streamlit UI, Context-Based Evaluation)
import streamlit as st
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional
import pandas as pd

# Load environment
load_dotenv()

st.set_page_config(
    page_title="Adaptive RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
#                     CSS STYLES
# =========================================================
st.markdown(
    """
    <style>
      .main-header { font-size: 2.4rem; color: #1f77b4; text-align:center; font-weight:700; margin-bottom:10px;}
      .model-box { border:1px solid #e0e0e0; border-radius:8px; padding:12px; background:#fafafa; }
      .selected-model { border-color:#4CAF50; background:#f0f8f0; box-shadow: 0 4px 8px rgba(76,175,80,0.08); }
      .validation-box { border:1px solid #ff9800; border-radius:8px; padding:10px; background:#fff8ef; }
      .source-box { border:1px solid #d0d7de; border-radius:6px; padding:8px; background:#f5f7fa; margin-bottom:6px;}
      .context-box { border:1px solid #9c27b0; border-radius:8px; padding:10px; background:#f3e5f5; margin:10px 0;}
      .metric-table { border-collapse: collapse; width:100%; }
      .metric-table th, .metric-table td { border: 1px solid #e6e6e6; padding:8px; text-align:center; }
      .metric-table th { background: #fafafa; }
      .winner-cell { background: #e6f4ea; font-weight:700; }
      .loser-cell { background: #fff6f6; }
      .neutral-cell { background:#ffffff; }
      .small { font-size:0.9rem; color:#666; }
      .good-metric { color: #2e7d32; font-weight:600; }
      .bad-metric { color: #c62828; font-weight:600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
#                     UTILITY FUNCTIONS
# =========================================================
def format_response(result: Dict[str, Any]) -> str:
    if not isinstance(result, dict):
        return str(result)
    if "generation" in result:
        return result["generation"]
    if "answer" in result:
        return result["answer"]
    return json.dumps(result, indent=2)

def extract_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metrics from context-based evaluation.
    """
    default = {
        "faithfulness": None, "context_utilization": None, "novel_terms_ratio": None,
        "rouge1": None, "rouge2": None, "rougeL": None, "bleu": None,
        "meteor": None, "bert_f1": None, "cosine_sim": None
    }

    output = {
        "gemini_metrics": dict(default),
        "perplexity_metrics": dict(default),
        "gemini_score": None,
        "perplexity_score": None,
        "evaluation_note": "No evaluation performed"
    }

    vr = result.get("validation_result", None)
    if vr and isinstance(vr, dict):
        output["gemini_metrics"] = vr.get("gemini_metrics", default)
        output["perplexity_metrics"] = vr.get("perplexity_metrics", default)
        output["gemini_score"] = vr.get("gemini_score")
        output["perplexity_score"] = vr.get("perplexity_score")
        output["evaluation_note"] = vr.get("evaluation_note", "Context-based evaluation")
        return output

    return output

def build_metrics_table(gem: Dict, perp: Dict, gem_score: float, perp_score: float) -> pd.DataFrame:
    rows = [
        ("Faithfulness", "faithfulness", ">0.6 good (answer grounded in context)"),
        ("Context Usage", "context_utilization", ">0.4 good (utilizes available context)"),
        ("Novel Terms Ratio", "novel_terms_ratio", "<0.3 good (few hallucinations)"),
        ("BERT F1", "bert_f1", ">0.4 good semantic similarity"),
        ("Cosine Similarity", "cosine_sim", ">0.7 good embedding similarity"),
        ("ROUGE-L", "rougeL", ">0.3 good content overlap"),
        ("METEOR", "meteor", ">0.3 good"),
        ("ROUGE-1", "rouge1", ">0.3 good"),
        ("ROUGE-2", "rouge2", ">0.2 good"),
        ("BLEU", "bleu", ">0.2 decent"),
    ]

    table = []
    for label, key, good_range in rows:
        def fmt(x):
            try:
                return f"{float(x):.3f}"
            except:
                return "n/a"

        table.append({
            "Metric": label,
            "Gemini": fmt(gem.get(key)),
            "Perplexity": fmt(perp.get(key)),
            "Good Range": good_range
        })

    # Composite score row
    table.append({
        "Metric": "Context Consistency Score",
        "Gemini": f"{gem_score:.4f}" if gem_score else "n/a",
        "Perplexity": f"{perp_score:.4f}" if perp_score else "n/a",
        "Good Range": "Higher = better factual consistency"
    })

    return pd.DataFrame(table)

def render_html_metrics_table(df: pd.DataFrame, gem_score: float, perp_score: float, overall_winner: str, evaluation_note: str):
    html = []
    html.append("<div class='model-box'>")
    html.append(f"<h4 style='margin:6px 0;'>📊 Context-Based Evaluation</h4>")
    html.append(f"<p class='small'>{evaluation_note}</p>")
    html.append("<table class='metric-table'>")
    html.append("<thead><tr><th>Metric</th><th>Gemini</th><th>Perplexity</th><th>Target Range</th></tr></thead><tbody>")

    for _, row in df.iterrows():
        def try_float(v):
            try:
                return float(v)
            except:
                return None

        g = try_float(row["Gemini"])
        p = try_float(row["Perplexity"])

        if g is None or p is None:
            gcls = pcls = "neutral-cell"
        else:
            if abs(g - p) < 1e-9:
                gcls = pcls = "neutral-cell"
            elif g > p:
                gcls = "winner-cell"
                pcls = "loser-cell"
            else:
                pcls = "winner-cell"
                gcls = "loser-cell"

        html.append(
            f"<tr>"
            f"<td>{row['Metric']}</td>"
            f"<td class='{gcls}'>{row['Gemini']}</td>"
            f"<td class='{pcls}'>{row['Perplexity']}</td>"
            f"<td class='small'>{row['Good Range']}</td>"
            f"</tr>"
        )

    html.append("</tbody></table>")

    if overall_winner:
        html.append(
            f"<div style='margin-top:10px; padding:10px; background:#e8f5e8; border-radius:6px; border:1px solid #4caf50;'>"
            f"🏆 <strong>Winner:</strong> <span style='font-weight:800;color:#2e7d32'>{overall_winner.upper()}</span> "
            f"| Better context consistency and factual grounding"
            f"</div>"
        )

    html.append("</div>")
    return "\n".join(html)

def display_context_preview(result: Dict[str, Any]):
    """Display a preview of the retrieved context."""
    if result.get("retrieved_context"):
        with st.expander("📋 View Retrieved Context (What both models saw)"):
            context = result["retrieved_context"]
            st.text_area(
                "Context used for generation and evaluation:",
                value=context,
                height=200,
                key="context_preview"
            )
            st.caption(f"Context length: {len(context)} characters")

# =========================================================
#               STREAMLIT SESSION STATE
# =========================================================
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"user_session_{datetime.now().timestamp()}"

# =========================================================
#               UI LAYOUT
# =========================================================
st.markdown('<div class="main-header">🤖 Adaptive RAG System — Context-Based Evaluation</div>', unsafe_allow_html=True)

left, right = st.columns([2, 1])

# =========================================================
#                       LEFT COLUMN
# =========================================================
with left:
    st.subheader("Ask a Question")
    question = st.text_area("Your question:", height=110, placeholder="e.g., What is prompt engineering? How do AI agents work?")

    if st.button("🚀 Run Query", use_container_width=True, type="primary"):

        if not question.strip():
            st.error("Please enter a valid question.")
            st.stop()

        st.session_state.last_result = None
        st.session_state.current_question = question

        from src.workflow.graph import app

        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        final_state = None

        try:
            with st.spinner("🔄 Processing with adaptive RAG pipeline..."):
                for output in app.stream({"question": question}, config=config):
                    for _, v in output.items():
                        final_state = v
        except Exception as e:
            st.error(f"Execution error: {e}")
            st.stop()

        st.session_state.last_result = final_state

        if final_state:
            ans = format_response(final_state)
            st.session_state.query_history.append({"question": question, "answer": ans})
            st.session_state.current_answer = ans

    st.markdown("---")

    # =========================================================
    #                     DISPLAY RESULTS
    # =========================================================
    if st.session_state.last_result:
        result = st.session_state.last_result

        st.markdown("### 🎯 Final Answer")
        model = result.get("chosen_model", "N/A")
        
        # Model selection badge
        if model == "gemini":
            st.success(f"**Selected Model: 🔷 GEMINI** - Better context consistency")
        elif model == "perplexity":
            st.success(f"**Selected Model: 🔶 PERPLEXITY** - Better context consistency") 
        else:
            st.info(f"**Selected Model: {model.upper()}**")

        st.markdown(f"<div class='model-box selected-model'>{format_response(result)}</div>", unsafe_allow_html=True)

        # Validation reasoning
        if result.get("validation_reasoning"):
            st.markdown("### 🧠 Selection Reasoning")
            st.markdown(f"<div class='validation-box'>{result['validation_reasoning']}</div>", unsafe_allow_html=True)

        # Retrieved sources
        if result.get("documents"):
            st.markdown("### 📚 Retrieved Sources")
            unique = set()
            for d in result["documents"]:
                try:
                    src = d.metadata.get("source", "Unknown")
                except:
                    src = "Unknown"
                unique.add(src)

            for i, s in enumerate(sorted(unique), 1):
                st.markdown(f"<div class='source-box'>{i}. {s}</div>", unsafe_allow_html=True)

        # Context preview
        display_context_preview(result)

        # =========================================================
        #                CONTEXT-BASED METRIC EVALUATION
        # =========================================================
        st.markdown("### 📈 Context-Based Evaluation")

        metrics = extract_metrics(result)

        df = build_metrics_table(
            metrics["gemini_metrics"],
            metrics["perplexity_metrics"],
            metrics["gemini_score"],
            metrics["perplexity_score"]
        )

        # Determine overall winner
        winner = None
        if metrics["gemini_score"] is not None and metrics["perplexity_score"] is not None:
            winner = "gemini" if metrics["gemini_score"] >= metrics["perplexity_score"] else "perplexity"

        html = render_html_metrics_table(
            df, 
            metrics["gemini_score"], 
            metrics["perplexity_score"], 
            winner,
            metrics["evaluation_note"]
        )
        st.markdown(html, unsafe_allow_html=True)

        # Key metrics explanation
        with st.expander("💡 Understanding the Metrics"):
            st.markdown("""
            **Context-Based Evaluation Metrics:**
            
            - **Faithfulness**: How much of the answer comes directly from the retrieved context (higher = less hallucination)
            - **Context Usage**: How well the model utilizes the available context information  
            - **Novel Terms Ratio**: Percentage of answer terms not found in context (lower = better)
            - **BERT F1**: Semantic similarity between answer and context
            - **Cosine Similarity**: Embedding-based similarity between answer and context
            - **ROUGE/METEOR/BLEU**: Text overlap and similarity metrics
            
            **Goal**: Select the answer that is most faithful to and consistent with the retrieved context.
            """)

        # Raw metrics data
        with st.expander("🔍 Raw Metric Data"):
            st.json(metrics)

# =========================================================
#                      RIGHT COLUMN
# =========================================================
with right:
    st.subheader("Parallel Model Outputs")
    
    if st.session_state.last_result:
        r = st.session_state.last_result

        # Gemini output
        gemini_class = "model-box selected-model" if r.get("chosen_model") == "gemini" else "model-box"
        st.markdown("#### 🔷 Gemini Output")
        st.markdown(f"<div class='{gemini_class}'>{r.get('gemini_answer', 'N/A')}</div>", unsafe_allow_html=True)

        # Perplexity output  
        perplexity_class = "model-box selected-model" if r.get("chosen_model") == "perplexity" else "model-box"
        st.markdown("#### 🔶 Perplexity Output")
        st.markdown(f"<div class='{perplexity_class}'>{r.get('perplexity_answer', 'N/A')}</div>", unsafe_allow_html=True)
        
        # Scores comparison
        metrics = extract_metrics(r)
        if metrics["gemini_score"] is not None and metrics["perplexity_score"] is not None:
            st.markdown("### 🏆 Score Comparison")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Gemini Score", f"{metrics['gemini_score']:.4f}")
            with col2:
                st.metric("Perplexity Score", f"{metrics['perplexity_score']:.4f}")
                
    else:
        st.info("""
        **How it works:**
        
        1. Ask any question
        2. System retrieves relevant context
        3. Both models generate answers
        4. Answers are evaluated for **context consistency**
        5. Best answer is selected based on factual grounding
        
        **Evaluation focuses on:**
        - Faithfulness to retrieved context
        - Context utilization  
        - Minimizing hallucinations
        - Semantic similarity to context
        """)

# =========================================================
#                     SIDEBAR
# =========================================================
with st.sidebar:
    st.header("Session Overview")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Queries", len(st.session_state.query_history))
    with col2:
        if st.session_state.last_result and st.session_state.last_result.get("chosen_model"):
            cm = st.session_state.last_result["chosen_model"]
            if cm in ["gemini", "perplexity"]:
                display = "🔷 GEMINI" if cm == "gemini" else "🔶 PERPLEXITY"
            else:
                display = cm.upper()
            st.metric("Best Model", display)
        else:
            st.metric("Best Model", "N/A")
    
    st.divider()
    
    st.subheader("Query History")
    if st.session_state.query_history:
        for i, entry in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            with st.expander(f"Q{i}: {entry['question'][:50]}...", expanded=False):
                st.write(entry["answer"][:200] + ("..." if len(entry["answer"]) > 200 else ""))
    else:
        st.info("No queries yet.")
    
    st.divider()
    
    # System info
    with st.expander("System Info"):
        st.markdown("""
        **Evaluation Method:**
        - Context-based metrics
        - No ground truth required
        - Real-time factual consistency check
        
        **Key Metrics:**
        - Faithfulness
        - Context Utilization  
        - Novel Terms Detection
        - Semantic Similarity
        """)

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center;color:#666;font-size:0.9rem;'>Adaptive RAG System | Context-Based Evaluation | Factual Consistency Focus</div>", unsafe_allow_html=True)