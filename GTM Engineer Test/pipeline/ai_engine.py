import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Ensure Python can resolve core directory modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import get_db_connection


def generate_ai_gtm_recommendation(keyword, video_data_list):
    """
    Feeds high-ranking market videos into Gemini to generate
    dynamic, smart, data-driven GTM recommendations.
    """
    # Force the engine to use the dedicated Gemini credential
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ AI Engine Error: GEMINI_API_KEY is missing from your .env file!")
        return False

    client = genai.Client(api_key=api_key)

    # Format a clean payload
    market_signals = ""
    for v in video_data_list:
        market_signals += f"- Title: {v['title']} | Creator: {v['channel']} | Views: {v['views']:,} | Category Profile: {v['format']}\n"

    prompt = f"""
    You are an elite YouTube Content Strategist and B2B Growth Engineer who builds high-CTR video concepts.
    We are tracking the market landscape for the competitor/keyword: "{keyword}".

    Here is the live metadata and performance metrics (view counts) for the top 5 videos winning the feed right now:
    {market_signals}

    Based on this real-world performance data, synthesize a hyper-actionable video concept that will outperform these competitors. 
    Avoid high-level corporate buzzwords, generic advice, or vague marketing terminology. Be concrete, specific, and direct.

    You MUST output your response strictly in the following structured layout. Do not write any generic introduction, pleasantries, or extra conversational text outside these sections.

    TOPIC: [A hyper-specific core subject matter, NOT a broad category. Max 4 words. Example: "Claude Artifacts Automation" instead of "AI Search Visibility"]
    FORMAT: [The explicit architectural delivery blueprint of the video, e.g., Product Tutorial, Copycat teardown, Feature stress-test]
    ANGLE: [A literal, copy-pasteable, high-CTR YouTube Video Title under 60 characters. Must use curiosity loops, brackets, or high-intent hooks. Do NOT make it a corporate campaign slogan.]
    REASONING: [A brutal, numbers-driven mathematical justification. Explicitly contrast the view counts of the top performing video against the lowest performing video from the payload to prove why this exact format and title will win.]
    """

    try:
        # Utilizing fast, cost-efficient inference models
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text

        # Parse output fields safely by stripping markdown asterisks
        topic, video_format, angle, reasoning = "AI Signal Discovery", "Standard Content", "Dynamic Hook Variant", text
        for line in text.split("\n"):
            clean_line = line.replace("*", "").strip()  # ◄--- For clearing markdown bolding tokens

            if clean_line.startswith("TOPIC:"):
                topic = clean_line.replace("TOPIC:", "").strip()
            elif clean_line.startswith("FORMAT:"):
                video_format = clean_line.replace("FORMAT:", "").strip()
            elif clean_line.startswith("ANGLE:"):
                angle = clean_line.replace("ANGLE:", "").strip()
            elif clean_line.startswith("REASONING:"):
                reasoning = clean_line.replace("REASONING:", "").strip()

        # Commit the AI insights straight to the recommendations table
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO recommendations (topic, format, angle, reasoning)
                    VALUES (%s, %s, %s, %s);
                """, (topic, video_format, angle, reasoning))

        print(f"🤖 Live Gemini AI Recommendation successfully generated and logged for keyword: {keyword}")
        return True
    except Exception as e:
        print(f"❌ AI Engine generation breakdown: {e}")
        return False