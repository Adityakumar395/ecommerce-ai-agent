import os
import re
import datetime
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, text
from ai_agent import app_agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables reliably
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)
load_dotenv()

app = FastAPI()

# Allow frontend to connect with backend securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint 1: Generate full report and chart data
@app.get("/api/report")
def generate_ecommerce_report(days: int = 30, db: Session = Depends(get_db)):
    try:
        # Validate and sanitize days input
        if not days or days <= 0:
            days = 30

        # Calculate the date range based on user input
        start_date = datetime.datetime.now() - datetime.timedelta(days=days)
        formatted_date = start_date.strftime('%Y-%m-%d 00:00:00')
        
        # Fetch both product_name and review_text from the database
        query = text(f"SELECT product_name, review_text FROM reviews WHERE created_at >= '{formatted_date}'")
        result = db.execute(query).fetchall()
        
        if not result:
            total_count = db.execute(text("SELECT COUNT(*) FROM reviews")).scalar() or 0
            if total_count > 0:
                return {
                    "status": "error",
                    "message": f"No reviews found in the last {days} days ({total_count} total reviews exist in earlier records). Try selecting 30 or 60 days."
                }
            return {"status": "error", "message": f"No reviews found in the database."}
            
        # Include product name in the dictionary sent to the AI Agent
        reviews_list = [{"product": row[0], "review": row[1]} for row in result]

        # Initialize the state for LangGraph workflow
        initial_state = {
            "reviews": reviews_list,
            "days": days,
            "chart_data": {},
            "report_html": ""
        }
        
        # Execute the LangGraph workflow
        agent_result = app_agent.invoke(initial_state)
        
        # Return the final structured data to the frontend
        return {
            "status": "success",
            "days_analyzed": days,
            "total_reviews": len(reviews_list),
            "report_html": agent_result["report_html"],
            "chart_data": agent_result["chart_data"]
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

_openrouter_rate_limited_until = 0

def is_openrouter_available() -> bool:
    import time
    global _openrouter_rate_limited_until
    return time.time() > _openrouter_rate_limited_until

def mark_openrouter_rate_limited(seconds: int = 300):
    import time
    global _openrouter_rate_limited_until
    _openrouter_rate_limited_until = time.time() + seconds

def answer_from_database(question: str, days: int = 30) -> str:
    """Ultra-intelligent, comprehensive DB analyzer for e-commerce reviews."""
    q = question.lower().strip()
    words = re.findall(r'[a-z0-9]+', q)
    stop_words = {"the", "a", "an", "in", "on", "of", "for", "to", "and", "or", "is", "are", "me", "give", "show", "tell", "what", "which", "how", "from", "with", "about", "database", "db", "data", "can", "you", "please", "batao", "kya", "hai", "saying", "said"}
    meaningful_words = [w for w in words if w not in stop_words]

    with engine.connect() as conn:
        total_count = conn.execute(text("SELECT COUNT(*) FROM reviews")).scalar() or 0
        all_products = [r[0] for r in conn.execute(text("SELECT DISTINCT product_name FROM reviews ORDER BY product_name")).fetchall()]
        all_customers = [r[0] for r in conn.execute(text("SELECT DISTINCT customer_name FROM reviews WHERE customer_name IS NOT NULL AND customer_name != '' ORDER BY customer_name")).fetchall()]

        # Product alias dictionary for fuzzy matching
        product_aliases = {
            "Galaxy Smartphone": ["galaxy", "smartphone", "samsung", "phone", "mobile", "android"],
            "Probook Laptop": ["probook", "laptop", "notebook", "computer", "pc", "hp"],
            "Smartwatch X": ["smartwatch", "watch", "smart watch", "fitness band"],
            "Bluetooth Speaker": ["speaker", "speakers", "bluetooth speaker", "audio speaker"],
            "Noise Cancelling Headphones": ["headphone", "headphones", "noise cancelling", "anc", "earphone", "earphones", "headset"],
            "Smart Coffee Maker": ["coffee", "coffee maker", "brewer", "espresso"],
            "Robot Vacuum": ["vacuum", "robot", "cleaner", "roomba", "cleaning robot"],
            "Fast Charging Powerbank": ["powerbank", "power bank", "charger", "portable charger", "battery pack"],
            "RGB Mechanical Keyboard": ["keyboard", "mechanical keyboard", "rgb", "typing keyboard", "keyboards"]
        }

        # ---------------------------------------------------------------------
        # 1. Match specific product from question
        # ---------------------------------------------------------------------
        matched_product = None
        for prod_name, aliases in product_aliases.items():
            if prod_name.lower() in q:
                matched_product = prod_name
                break
            for al in aliases:
                if re.search(r'\b' + re.escape(al) + r'\b', q):
                    matched_product = prod_name
                    break
            if matched_product:
                break

        if matched_product:
            prod_reviews = conn.execute(text("SELECT review_text, sentiment, customer_name FROM reviews WHERE product_name = :p ORDER BY created_at DESC"), {"p": matched_product}).fetchall()
            pos = sum(1 for r in prod_reviews if r[1] == 'positive')
            neg = sum(1 for r in prod_reviews if r[1] == 'negative')
            neu = sum(1 for r in prod_reviews if r[1] == 'neutral')

            # Check if user asked specifically for negative/complaints of this product
            if any(w in q for w in ["bad", "worst", "issue", "issues", "problem", "problems", "complaint", "complaints", "negative", "drawback", "flaw", "kharab", "bekar"]):
                neg_reviews = [r for r in prod_reviews if r[1] == 'negative']
                if neg_reviews:
                    lines = [f"Negative feedback / issues for {matched_product} ({len(neg_reviews)} reviews):"]
                    for r in neg_reviews:
                        cust = f" (by {r[2]})" if r[2] else ""
                        lines.append(f"- \"{r[0]}\"{cust}")
                    return "\n".join(lines)
                else:
                    return f"Great news! There are no negative reviews recorded for {matched_product} in the database."

            # Check if user asked specifically for positive/benefits of this product
            if any(w in q for w in ["good", "best", "positive", "great", "recommend", "love", "loved", "benefit", "pros", "accha", "badhiya"]):
                pos_reviews = [r for r in prod_reviews if r[1] == 'positive']
                if pos_reviews:
                    lines = [f"Positive highlights for {matched_product} ({len(pos_reviews)} reviews):"]
                    for r in pos_reviews:
                        cust = f" (by {r[2]})" if r[2] else ""
                        lines.append(f"- \"{r[0]}\"{cust}")
                    return "\n".join(lines)
                else:
                    return f"No positive reviews found for {matched_product} yet."

            # General inquiry for this product
            lines = [f"Analysis for {matched_product} ({len(prod_reviews)} total reviews):"]
            lines.append(f"- Sentiment Breakdown: {pos} Positive, {neg} Negative, {neu} Neutral")
            lines.append("Customer Feedback:")
            for r in prod_reviews:
                cust = f" (by {r[2]})" if r[2] else ""
                lines.append(f"- [{r[1].capitalize()}]: \"{r[0]}\"{cust}")
            return "\n".join(lines)

        # ---------------------------------------------------------------------
        # 2. Specific Customer lookup: "what did Rahul say", "reviews by Priya"
        # ---------------------------------------------------------------------
        for c in all_customers:
            if re.search(r'\b' + re.escape(c.lower()) + r'\b', q):
                c_reviews = conn.execute(text("SELECT product_name, review_text, sentiment FROM reviews WHERE LOWER(customer_name) = :c"), {"c": c.lower()}).fetchall()
                if c_reviews:
                    lines = [f"Reviews submitted by {c} ({len(c_reviews)} total):"]
                    for r in c_reviews:
                        lines.append(f"- {r[0]} [{r[2].capitalize()}]: \"{r[1]}\"")
                    return "\n".join(lines)

        # ---------------------------------------------------------------------
        # 3. Feature / Aspect based search (battery, camera, display, sound, cleaning, etc.)
        # ---------------------------------------------------------------------
        feature_keywords = {
            "battery": ["battery", "drains", "drain", "charge", "charging", "backup", "mah", "powerbank"],
            "camera": ["camera", "photo", "picture", "lens", "video", "photos"],
            "display": ["display", "screen", "oled", "amoled", "colors", "bright"],
            "sound": ["sound", "audio", "bass", "mids", "treble", "speaker", "noise", "volume", "music"],
            "keyboard": ["keyboard", "typing", "keys", "switches", "mechanical"],
            "performance": ["fast", "slow", "speed", "smooth", "ssd", "lag", "laggy", "performance"],
            "cleaning": ["clean", "cleaning", "hair", "sofa", "animal", "vacuum", "dust"],
            "connectivity": ["app", "connect", "connection", "bluetooth", "wifi", "drops"]
        }
        for feature_name, f_words in feature_keywords.items():
            if any(re.search(r'\b' + re.escape(fw) + r'\b', q) for fw in f_words):
                conditions = " OR ".join([f"LOWER(review_text) LIKE :kw_{idx}" for idx in range(len(f_words))])
                params = {f"kw_{idx}": f"%{w}%" for idx, w in enumerate(f_words)}
                f_reviews = conn.execute(text(f"SELECT product_name, review_text, sentiment, customer_name FROM reviews WHERE {conditions}"), params).fetchall()
                if f_reviews:
                    lines = [f"Found {len(f_reviews)} customer feedback mentions regarding '{feature_name}':"]
                    for r in f_reviews:
                        cust = f" (by {r[3]})" if r[3] else ""
                        lines.append(f"- {r[0]} [{r[2].capitalize()}]: \"{r[1]}\"{cust}")
                    return "\n".join(lines)

        # ---------------------------------------------------------------------
        # 3b. Improvement Plan intent
        # ---------------------------------------------------------------------
        if any(w in q for w in ["improvement plan", "improvement", "improve", "action plan", "recommendations"]):
            neg_rows = conn.execute(text("""
                SELECT product_name, review_text 
                FROM reviews 
                WHERE sentiment = 'negative' 
                ORDER BY product_name
            """)).fetchall()

            # Also check for battery / hardware drainage issues mentioned in other reviews
            battery_rows = conn.execute(text("""
                SELECT product_name, review_text 
                FROM reviews 
                WHERE (LOWER(review_text) LIKE '%drain%' OR LOWER(review_text) LIKE '%battery%')
                  AND sentiment != 'negative'
                ORDER BY product_name
            """)).fetchall()

            if not neg_rows and not battery_rows:
                return "All products currently have positive feedback. Maintain current quality standards."

            lines = ["Product-Specific Improvement Plan (Targeted Solutions for Negative Reviews & Issues):"]

            product_negatives = {}
            for p, r in neg_rows:
                product_negatives.setdefault(p, []).append(r)

            for prod, revs in product_negatives.items():
                issues = " | ".join(f'"{r}"' for r in revs)
                c_text = f"{prod} {' '.join(revs)}".lower()
                actions = []

                if any(w in c_text for w in ["sound", "audio", "bass", "distortion", "noise", "volume", "loud"]):
                    actions.append("Audio Quality: Conduct acoustic audits on sound equipment, recalibrate driver diaphragm frequency response to eliminate distortion, and upgrade internal audio amplification circuits")
                if any(w in c_text for w in ["keyboard", "key", "keys", "switch", "switches", "typing"]):
                    actions.append("Hardware Durability: Upgrade switch contact durability and keycap membrane assembly to prevent keys failing under regular use, and tighten factory pre-dispatch inspections")
                if any(w in c_text for w in ["battery", "drain", "drains", "charge", "charging", "powerbank", "power"]):
                    actions.append("Hardware & Battery: Audit battery cell supply chain and charging BMS IC circuits to eliminate premature power cut-offs, and implement enhanced power management firmware")
                if any(w in c_text for w in ["stuck", "sofa", "vacuum", "clean", "cleaning", "hair"]):
                    actions.append("Navigation & Mechanics: Upgrade obstacle avoidance navigation algorithms and implement lower-clearance bumper profiling to prevent entrapment under low-profile furniture")
                if any(w in c_text for w in ["refund", "money", "waste", "defective", "return"]):
                    actions.append("Logistics & Support: Capitalize on positive delivery sentiment while proactively addressing return requests for defective units and issuing expedited replacements to restore customer trust")
                if not actions:
                    actions.append("Quality Assurance: Overhaul end-to-end component testing and strengthen pre-dispatch quality checks on the manufacturing line")

                lines.append(f"\n- Product: {prod}\n  Negative Review: {issues}\n  Improvement Plan: {'; '.join(actions)}.")

            if battery_rows:
                lines.append("\nPortable Items Battery Optimization Plan:")
                b_prods = {}
                for p, r in battery_rows:
                    b_prods.setdefault(p, []).append(r)
                for prod, revs in b_prods.items():
                    issues = " | ".join(f'"{r}"' for r in revs)
                    lines.append(f"- Product: {prod}\n  Identified Feedback: {issues}\n  Improvement Plan: Hardware & Battery: Investigate rapid battery drainage under continuous usage (e.g., 5G / high-brightness display) and deploy enhanced power management firmware for portable items.")

            return "\n".join(lines)

        # ---------------------------------------------------------------------
        # 4. Negative / Complaints / Worst intent across all products
        # ---------------------------------------------------------------------
        if any(w in q for w in ["worst", "negative", "bad", "problem", "problems", "issue", "issues", "kharab", "bekar", "complaint", "complaints", "defective", "fail", "failed", "broken", "disappointed", "refund"]):
            neg_rows = conn.execute(text("""
                SELECT product_name, review_text, customer_name 
                FROM reviews 
                WHERE sentiment = 'negative' 
                ORDER BY product_name
            """)).fetchall()
            if neg_rows:
                lines = [f"Found {len(neg_rows)} negative reviews across products:"]
                for r in neg_rows:
                    cust = f" (by {r[2]})" if r[2] else ""
                    lines.append(f"- {r[0]}: \"{r[1]}\"{cust}")
                return "\n".join(lines)
            return "No negative reviews found in the database."

        # ---------------------------------------------------------------------
        # 5. Positive / Best / Top intent across all products
        # ---------------------------------------------------------------------
        if any(w in q for w in ["best", "positive", "good", "top", "accha", "badhiya", "recommend", "love", "favorite", "great", "excellent", "superb", "satisfaction"]):
            pos_counts = conn.execute(text("""
                SELECT product_name, COUNT(*) as c 
                FROM reviews 
                WHERE sentiment = 'positive' 
                GROUP BY product_name 
                ORDER BY c DESC
            """)).fetchall()
            if pos_counts:
                lines = ["Top rated products with positive feedback:"]
                for r in pos_counts:
                    sample = conn.execute(text("SELECT review_text, customer_name FROM reviews WHERE product_name = :p AND sentiment='positive' LIMIT 1"), {"p": r[0]}).fetchone()
                    quote = f": \"{sample[0]}\"" if sample else ""
                    lines.append(f"- {r[0]} ({r[1]} positive reviews){quote}")
                return "\n".join(lines)

        # ---------------------------------------------------------------------
        # 6. Neutral / Mixed reviews inquiry
        # ---------------------------------------------------------------------
        if any(w in q for w in ["neutral", "average", "okay", "mixed"]):
            neu_rows = conn.execute(text("""
                SELECT product_name, review_text, customer_name 
                FROM reviews 
                WHERE sentiment = 'neutral'
            """)).fetchall()
            if neu_rows:
                lines = [f"Found {len(neu_rows)} neutral/mixed reviews:"]
                for r in neu_rows:
                    cust = f" (by {r[2]})" if r[2] else ""
                    lines.append(f"- {r[0]}: \"{r[1]}\"{cust}")
                return "\n".join(lines)
            return "No neutral reviews found in the database."

        # ---------------------------------------------------------------------
        # 7. Customer directory / listing intent: "who reviewed", "list customers", "who are the customers"
        # ---------------------------------------------------------------------
        customer_triggers = ["who reviewed", "who bought", "customer name", "customer names", "reviewers", "who gave reviews", "saare customer", "list customers", "who are the customers"]
        if any(trigger in q for trigger in customer_triggers) or (("customer" in q or "customers" in q or "buyers" in q) and any(w in q for w in ["who", "all", "list", "names", "name", "saare", "har"])):
            lines = [f"There are {len(all_customers)} customers who submitted reviews:"]
            for i, c in enumerate(all_customers, 1):
                c_prods = [r[0] for r in conn.execute(text("SELECT DISTINCT product_name FROM reviews WHERE customer_name = :c"), {"c": c}).fetchall()]
                lines.append(f"{i}. {c} (Reviewed: {', '.join(c_prods)})")
            return "\n".join(lines)

        # ---------------------------------------------------------------------
        # 8. Product Listing intent
        # Examples: "give me all product name in the database", "what products do you have",
        # "which products are there in db", "list items", "show catalog", "saare product"
        # ---------------------------------------------------------------------
        product_list_keywords = ["product", "products", "item", "items", "device", "devices", "catalog", "inventory", "goods", "models"]
        asking_for_list = any(w in q for w in ["all", "list", "names", "name", "every", "each", "show", "give", "available", "exist", "which", "what", "saare", "sab", "kitne", "there"])
        
        if (any(kw in q for kw in product_list_keywords) and asking_for_list) or q in ["products", "all products", "product names", "list products", "items"]:
            lines = [f"Found {len(all_products)} distinct products in the database:"]
            for i, p in enumerate(all_products, 1):
                p_reviews = conn.execute(text("SELECT sentiment, COUNT(*) FROM reviews WHERE product_name = :p GROUP BY sentiment"), {"p": p}).fetchall()
                s_dict = {r[0]: r[1] for r in p_reviews}
                total_p = sum(s_dict.values())
                summary_parts = []
                if s_dict.get('positive'): summary_parts.append(f"{s_dict['positive']} positive")
                if s_dict.get('negative'): summary_parts.append(f"{s_dict['negative']} negative")
                if s_dict.get('neutral'): summary_parts.append(f"{s_dict['neutral']} neutral")
                breakdown = f" ({', '.join(summary_parts)})" if summary_parts else ""
                lines.append(f"{i}. {p} - {total_p} review{'s' if total_p != 1 else ''}{breakdown}")
            return "\n".join(lines)

        # ---------------------------------------------------------------------
        # 9. Count / statistics / breakdown intent
        # ---------------------------------------------------------------------
        if any(w in q for w in ["total", "count", "how many", "kitne", "summary", "stats", "statistics", "breakdown", "percentage", "metrics"]):
            stats = conn.execute(text("SELECT sentiment, COUNT(*) FROM reviews GROUP BY sentiment")).fetchall()
            stat_dict = {r[0]: r[1] for r in stats}
            pos = stat_dict.get('positive', 0)
            neg = stat_dict.get('negative', 0)
            neu = stat_dict.get('neutral', 0)
            return (
                f"Database Analytics Summary:\n"
                f"- Total Reviews: {total_count}\n"
                f"- Total Distinct Products: {len(all_products)}\n"
                f"- Total Customers: {len(all_customers)}\n"
                f"- Positive Reviews: {pos} ({round(pos/total_count*100 if total_count else 0)}%)\n"
                f"- Negative Reviews: {neg} ({round(neg/total_count*100 if total_count else 0)}%)\n"
                f"- Neutral Reviews: {neu} ({round(neu/total_count*100 if total_count else 0)}%)"
            )

        # ---------------------------------------------------------------------
        # 10. Keyword Search on review text with user's words
        # ---------------------------------------------------------------------
        search_words = [w for w in meaningful_words if len(w) >= 3]
        if search_words:
            conditions = " OR ".join([f"LOWER(review_text) LIKE :sw_{i} OR LOWER(product_name) LIKE :sw_{i} OR LOWER(customer_name) LIKE :sw_{i}" for i in range(len(search_words))])
            params = {f"sw_{i}": f"%{w}%" for i, w in enumerate(search_words)}
            matched_reviews = conn.execute(text(f"SELECT product_name, review_text, sentiment, customer_name FROM reviews WHERE {conditions} LIMIT 5"), params).fetchall()
            if matched_reviews:
                lines = [f"Found {len(matched_reviews)} reviews matching your query:"]
                for r in matched_reviews:
                    cust = f" (by {r[3]})" if r[3] else ""
                    lines.append(f"- {r[0]} [{r[2].capitalize()}]: \"{r[1]}\"{cust}")
                return "\n".join(lines)

        # ---------------------------------------------------------------------
        # 11. General Overview & Prompt Suggestions
        # ---------------------------------------------------------------------
        stats = conn.execute(text("SELECT sentiment, COUNT(*) FROM reviews GROUP BY sentiment")).fetchall()
        stat_dict = {r[0]: r[1] for r in stats}
        return (
            f"Here is an overview of the database:\n"
            f"- Total Reviews: {total_count} across {len(all_products)} products\n"
            f"- Sentiment: {stat_dict.get('positive', 0)} Positive, {stat_dict.get('negative', 0)} Negative, {stat_dict.get('neutral', 0)} Neutral\n\n"
            f"You can ask me specific questions like:\n"
            f"- 'Give me all product names in the database'\n"
            f"- 'What are the worst products with complaints?'\n"
            f"- 'What do customers say about battery or camera?'\n"
            f"- 'Show reviews for Galaxy Smartphone or Laptop'\n"
            f"- 'Who are the customers who submitted reviews?'"
        )

# Endpoint 2: Chat with data feature
@app.get("/api/chat")
def chat_with_data(question: str, days: int = 30):
    try:
        if not days or days <= 0:
            days = 30

        # If OpenRouter was recently rate-limited (HTTP 429), use database analyzer directly and immediately
        if not is_openrouter_available() or not os.getenv("OPENROUTER_API_KEY"):
            return {"reply": answer_from_database(question, days)}

        models_to_try = [
            "nvidia/nemotron-3.5-lightning:free",
            "liquid/lfm-2.5-2.6b:free"
        ]

        schema = """
Table: reviews
Columns:
- id (INT, primary key)
- product_name (VARCHAR)
- customer_name (VARCHAR)
- review_text (TEXT)
- sentiment (VARCHAR: 'positive', 'negative', or 'neutral')
- created_at (DATETIME)
"""
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        sql_prompt = (
            f"You are a MySQL expert for this database schema:\n{schema}\n"
            f"Current timestamp: {now}\n"
            f"User Question: {question}\n\n"
            f"Rules:\n"
            f"1. Generate ONLY a valid MySQL SELECT query.\n"
            f"2. Consider reviews from the last {days} days if relevant (using created_at).\n"
            f"3. The 'sentiment' column contains 'positive', 'negative', or 'neutral'.\n"
            f"4. The user may ask in English or Hinglish. Understand their intent.\n"
            f"5. Enclose the query in a ```sql code block.\n"
        )

        sql_clean = ""
        for m in models_to_try:
            try:
                chat_llm = ChatOpenAI(
                    temperature=0,
                    model=m,
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1",
                    request_timeout=8,
                    max_tokens=600
                )
                sql_response = chat_llm.invoke(sql_prompt).content.strip()
                code_blocks = re.findall(r"```(?:sql)?\s*([\s\S]*?)\s*```", sql_response, re.IGNORECASE)
                if code_blocks:
                    candidate = code_blocks[-1].strip()
                else:
                    select_match = re.search(r"\b(SELECT\s+[\s\S]+?)(?:;|\n\s*\n|$)", sql_response, re.IGNORECASE)
                    candidate = select_match.group(1).strip() if select_match else ""

                candidate = candidate.rstrip(";").strip()
                if candidate.upper().startswith("SELECT"):
                    sql_clean = candidate
                    break
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "rate limit" in err_str:
                    mark_openrouter_rate_limited(300)
                    break
                continue

        # If LLM could not generate SQL, use smart database analyzer directly
        if not sql_clean:
            return {"reply": answer_from_database(question, days)}

        # Security check: only SELECT allowed, block destructive keywords
        forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "RENAME"]
        tokens = [t.upper() for t in re.findall(r"[a-zA-Z]+", sql_clean)]
        if not sql_clean.upper().startswith("SELECT") or any(f in tokens for f in forbidden):
            return {"reply": answer_from_database(question, days)}

        # Step 3: Execute query safely against MySQL
        with engine.connect() as conn:
            query_result = conn.execute(text(sql_clean)).fetchall()
            rows_str = str(query_result[:25])

        # Step 4: Answer user's question clearly using the query results
        answer_prompt = (
            f"You are an expert e-commerce business data analyst.\n"
            f"User Question: {question}\n"
            f"Database Result: {rows_str}\n\n"
            f"Analyze the database result and provide a direct, concise, professional answer.\n"
            f"If the user asked in Hinglish or Hindi, answer in friendly Hinglish/English. Otherwise answer in English.\n"
            f"DO NOT use markdown asterisks like ** or *. Provide plain text only.\n"
            f"Use bullet points (- ) or separate lines for multiple items."
        )

        clean_reply = ""
        for m in models_to_try:
            try:
                chat_llm = ChatOpenAI(
                    temperature=0,
                    model=m,
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    base_url="https://openrouter.ai/api/v1",
                    request_timeout=8,
                    max_tokens=600
                )
                raw_ans = chat_llm.invoke(answer_prompt).content.strip()
                clean = raw_ans.replace("**", "").replace("*", "")
                if "```" in clean:
                    clean = re.sub(r"```[\s\S]*?```", "", clean).strip()
                if "here's a thinking process" in clean.lower():
                    lines = [l for l in clean.splitlines() if not l.lower().startswith("here's a thinking process") and not re.match(r"^\s*\d+\.\s+\*\*", l)]
                    clean = "\n".join(lines).strip()
                if clean:
                    clean_reply = clean
                    break
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "rate limit" in err_str:
                    mark_openrouter_rate_limited(300)
                    break
                continue

        if not clean_reply:
            clean_reply = answer_from_database(question, days)

        return {"reply": clean_reply}

    except Exception:
        return {"reply": answer_from_database(question, days)}

# Mount frontend directory to serve UI directly at http://127.0.0.1:8000/
from fastapi.staticfiles import StaticFiles
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)