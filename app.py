from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv

# Load environment variables: 

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

MAX_TOTAL_CANDIDATES = int(os.getenv("MAX_TOTAL_CANDIDATES", "10"))   

TOP_N_TO_DISPLAY = int(os.getenv("TOP_N_TO_DISPLAY", "10"))           

if not CLAUDE_API_KEY:
    print("❌ ERROR: CLAUDE_API_KEY not found. Create .env with CLAUDE_API_KEY=...")
    raise SystemExit(1)

# App: 

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route("/")
def root():
    return send_from_directory(".", "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

@app.route("/health")
def health():
    return jsonify({"ok": True})

@app.route("/config")
def config():
    return jsonify({
        "max_total_candidates": MAX_TOTAL_CANDIDATES,
        "top_n_to_display": TOP_N_TO_DISPLAY
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    def fallback_summary(name, similarity):
        pct = round(float(similarity) * 100)
        return (f"{name} shows a {pct}% match to the job description. "
                "Based on overlapping keywords and experience, they could ramp quickly and "
                "support core responsibilities. (Auto-generated fallback)")

    try:
        data = request.get_json(force=True) or {}
        job_desc = data.get("jobDesc", "")
        resume = data.get("resume", "")
        similarity = float(data.get("similarity", 0.0))
        candidate_name = data.get("candidateName", "Candidate")

        print(f"🎯 Analyze -> {candidate_name} | sim≈{round(similarity*100)}%")

        prompt = f"""You are an expert HR analyst. Evaluate this candidate for the job opening.

JOB DESCRIPTION:
{job_desc}

CANDIDATE RESUME:
{resume}

SIMILARITY SCORE: {round(similarity * 100)}% match

Provide a concise, professional analysis in 2–3 sentences explaining why this candidate would be valuable for this role. Be specific about qualifications and likely contributions."""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01",
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        }

        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            if resp.status_code == 200:
                result = resp.json()
                text = result["content"][0]["text"]
                return jsonify({"success": True, "summary": text})
            else:
                # Claude error — return fallback, but keep success True
                print(f"⚠️ Claude error {resp.status_code}: {resp.text[:200]}...")
                return jsonify({"success": True, "summary": fallback_summary(candidate_name, similarity)})
        except Exception as e:
            # Network/timeout/etc — return fallback, but keep success True
            print(f"⚠️ Claude request failed: {e}")
            return jsonify({"success": True, "summary": fallback_summary(candidate_name, similarity)})

    except Exception as e:
        # Absolute last-resort fallback; still don't drop the candidate
        print(f"❌ Server exception: {e}")
        return jsonify({
            "success": True,
            "summary": "Candidate analysis generated via fallback due to a temporary server issue."
        })

if __name__ == "__main__":
    print("🚀 TalentMatch AI server starting…")
    print("🔒 API key loaded from environment (.env ignored by git)")
    print(f"📊 Limits: max_total_candidates={MAX_TOTAL_CANDIDATES}, top_n_to_display={TOP_N_TO_DISPLAY}")
    print("🌐 Open http://127.0.0.1:8000")
    app.run(debug=True, host="127.0.0.1", port=8000)
