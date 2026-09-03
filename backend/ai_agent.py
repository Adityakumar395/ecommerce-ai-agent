import os
import json
import re
from typing import TypedDict, List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file reliably
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

# Fetch the OpenRouter API key securely
openrouter_key = os.getenv("OPENROUTER_API_KEY")

# Define the State for LangGraph
class AgentState(TypedDict):
    reviews: List[Dict]
    days: int
    chart_data: Dict
    report_html: str

# Initialize the LLM with request_timeout and max_tokens to prevent indefinite hanging
llm = ChatOpenAI(
    temperature=0.2,
    model="nvidia/nemotron-3.5-lightning:free",
    api_key=openrouter_key,
    base_url="https://openrouter.ai/api/v1",
    request_timeout=8,
    max_tokens=1200
)

# ============================================================
# Positive / Negative keyword lists for fast local sentiment
# ============================================================
_POS_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "love", "loved", "best",
    "perfect", "fantastic", "wonderful", "happy", "satisfied", "impressive",
    "beautiful", "nice", "fast", "smooth", "comfortable", "recommend",
    "superb", "brilliant", "premium", "worth", "stylish", "durable",
    "easy", "reliable", "sturdy", "clear", "crisp", "handy", "top",
}
_NEG_WORDS = {
    "bad", "worst", "terrible", "horrible", "poor", "hate", "hated", "slow",
    "waste", "disappointed", "disappointing", "broken", "defective", "cheap",
    "useless", "awful", "faulty", "issue", "problem", "complaint", "worse",
    "pathetic", "refund", "return", "damaged", "fail", "failed", "fails",
    "overheating", "overheat", "drains", "drain", "lag", "laggy", "noisy",
    "flimsy", "uncomfortable", "unreliable", "mediocre", "regret",
}

def _classify_review(text: str) -> str:
    """Fast keyword-based sentiment classification — instant, deterministic."""
    words = set(re.findall(r'[a-z]+', text.lower()))
    pos_score = len(words & _POS_WORDS)
    neg_score = len(words & _NEG_WORDS)
    if pos_score > neg_score:
        return "positive"
    elif neg_score > pos_score:
        return "negative"
    return "neutral"

def build_structured_report(reviews_data: List[Dict], days: int, chart_data: Dict) -> str:
    """High-quality analytical report generator used as instant fallback if LLM is slow/offline."""
    pos = chart_data.get("positive", 0)
    neg = chart_data.get("negative", 0)
    neu = chart_data.get("neutral", 0)
    total = pos + neg + neu or len(reviews_data) or 1
    
    pos_pct = round((pos / total) * 100)
    neg_pct = round((neg / total) * 100)
    neu_pct = 100 - pos_pct - neg_pct

    # Group reviews
    grouped = {"negative": [], "positive": [], "neutral": []}
    for item in reviews_data:
        sentiment = _classify_review(item.get("review", ""))
        grouped[sentiment].append(item)

    html = f"""<h2>E-Commerce Business Report</h2>

<h3>Overview</h3>
<p>Analysis of <strong>{len(reviews_data)}</strong> customer reviews collected over the past <strong>{days} days</strong>.</p>
<ul>
    <li><strong>Positive Reviews:</strong> {pos} ({pos_pct}%)</li>
    <li><strong>Negative Reviews:</strong> {neg} ({neg_pct}%)</li>
    <li><strong>Neutral Reviews:</strong> {neu} ({neu_pct}%)</li>
</ul>

<h3>Customer Reviews</h3>
"""

    if grouped["negative"]:
        html += "<h3>Negative Reviews</h3>\n<ul>\n"
        for r in grouped["negative"]:
            html += f'    <li><strong>{r.get("product", "Product")}:</strong> "{r.get("review", "")}"</li>\n'
        html += "</ul>\n"

    if grouped["positive"]:
        html += "<h3>Positive Reviews</h3>\n<ul>\n"
        for r in grouped["positive"]:
            html += f'    <li><strong>{r.get("product", "Product")}:</strong> "{r.get("review", "")}"</li>\n'
        html += "</ul>\n"

    if grouped["neutral"]:
        html += "<h3>Neutral Reviews</h3>\n<ul>\n"
        for r in grouped["neutral"]:
            html += f'    <li><strong>{r.get("product", "Product")}:</strong> "{r.get("review", "")}"</li>\n'
        html += "</ul>\n"

    html += "<h3>Improvement Plan</h3>\n<ul>\n"
    if grouped["negative"]:
        # Group negative reviews by product
        neg_by_product = {}
        for r in grouped["negative"]:
            p_name = r.get("product", "Product")
            neg_by_product.setdefault(p_name, []).append(r.get("review", ""))

        for p_name, p_reviews in neg_by_product.items():
            plan_item = _generate_product_improvement_plan(p_name, p_reviews)
            html += f"    <li>{plan_item}</li>\n"
    else:
        html += "    <li><strong>Overall Quality:</strong> No negative reviews recorded in this timeframe. Continue monitoring customer feedback and maintain current quality standards.</li>\n"
    html += "</ul>"

    return html

def _generate_product_improvement_plan(product_name: str, reviews: List[str]) -> str:
    """Generates a targeted, actionable improvement plan for a specific product with negative reviews."""
    combined_text = f"{product_name} {' '.join(reviews)}".lower()
    review_quotes = ' | '.join(f'"{r}"' for r in reviews)
    
    actions = []
    if any(w in combined_text for w in ["sound", "audio", "bass", "distortion", "noise", "volume", "loud"]):
        actions.append("Audio Quality: Conduct acoustic audits on sound equipment and recalibrate driver diaphragm frequency response to eliminate sound distortion")
    if any(w in combined_text for w in ["keyboard", "key", "keys", "switch", "switches", "typing"]):
        actions.append("Hardware Durability: Upgrade switch contact durability and keycap membrane assembly to prevent keys failing under regular use")
    if any(w in combined_text for w in ["battery", "drain", "drains", "charge", "charging", "powerbank", "power"]):
        actions.append("Hardware & Battery: Audit battery cell supply chain and charging BMS IC circuits to eliminate premature power failure, and implement enhanced power management firmware")
    if any(w in combined_text for w in ["stuck", "sofa", "vacuum", "clean", "cleaning", "hair"]):
        actions.append("Navigation & Mechanics: Upgrade obstacle avoidance navigation algorithms and lower clearance bumper profile to prevent unit entrapment")
    if any(w in combined_text for w in ["app", "connect", "connection", "wifi", "bluetooth", "drop", "drops"]):
        actions.append("Software & Firmware: Deploy firmware optimization to resolve wireless drop-outs and stabilize companion app synchronization")
    if any(w in combined_text for w in ["slow", "lag", "laggy", "freeze", "performance"]):
        actions.append("System Performance: Optimize background services and thermal dissipation to eliminate processing latency")
    
    if any(w in combined_text for w in ["refund", "return", "broken", "defective", "waste", "stopped working"]):
        actions.append("Logistics & Support: Proactively reach out to affected customers to handle warranty replacements and issue immediate refunds for defective units")
    elif not actions:
        actions.append("Quality Assurance: Strengthen component inspection on the manufacturing line and tighten pre-dispatch quality checks")

    action_text = "; ".join(actions) + "."
    return f"<strong>{product_name}</strong> (Feedback: {review_quotes}) — <em>Action Plan:</em> {action_text}"

# Node 1: Local Sentiment Analyst — instant, no API call
def analyze_sentiment_node(state: AgentState):
    reviews_data = state["reviews"]
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for review in reviews_data:
        sentiment = _classify_review(review.get("review", ""))
        counts[sentiment] += 1
    return {"chart_data": counts}

# Node 2: Report Writer — LLM call with instant fallback if slow or rate-limited
def generate_report_node(state: AgentState):
    reviews_data = state["reviews"]
    days = state["days"]
    chart_data = state["chart_data"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert E-Commerce Business Analyst. Write a comprehensive HTML report.
DO NOT include any thinking, reasoning, or preamble — go straight to the HTML output.
Strict formatting rules:
1. 'Overview': Show the exact count of positive, negative, and neutral reviews.
2. 'Customer Reviews': Group them STRICTLY by sentiment using headings (e.g., <h3>Negative Reviews</h3>, <h3>Positive Reviews</h3>, <h3>Neutral Reviews</h3>).
3. Under each sentiment heading, list the reviews in this exact format: <strong>Product Name:</strong> "Exact review text".
4. 'Improvement Plan': For EVERY product that received negative feedback or complaints, give the exact product name in bold first, mention the customer's specific issue, followed by a targeted, actionable improvement plan specifically for that product covering Hardware & Battery, Audio Quality, Mechanics, or Logistics & Support (e.g., <li><strong>Product Name:</strong> (Issue: "...") — Action Plan: ...</li>).
5. Use professional HTML: <h2>, <h3>, <ul>, <li>, <strong>, <em>. DO NOT use markdown backticks (```html)."""),
        ("human", "Timeframe: {days} days.\nSentiment Breakdown: {chart_data}\nRaw Reviews: {reviews}")
    ])

    clean_html = ""
    try:
        chain = prompt | llm
        response = chain.invoke({
            "days": days,
            "chart_data": chart_data,
            "reviews": reviews_data
        })

        clean_html = response.content.replace("```html", "").replace("```", "").strip()

        # Remove any "thinking process" preamble if the model included it
        html_start = re.search(r'<h[1-6]', clean_html, re.IGNORECASE)
        if html_start and html_start.start() > 50:
            clean_html = clean_html[html_start.start():]

        # Verify output looks like valid HTML report
        if len(clean_html) < 100 or "<h" not in clean_html:
            clean_html = build_structured_report(reviews_data, days, chart_data)

    except Exception as e:
        print(f"LLM report generation fallback triggered: {e}")
        clean_html = build_structured_report(reviews_data, days, chart_data)

    return {"report_html": clean_html}

# Build the LangGraph Workflow
workflow = StateGraph(AgentState)

workflow.add_node("sentiment_analyst", analyze_sentiment_node)
workflow.add_node("report_writer", generate_report_node)

workflow.set_entry_point("sentiment_analyst")
workflow.add_edge("sentiment_analyst", "report_writer")
workflow.add_edge("report_writer", END)

app_agent = workflow.compile()