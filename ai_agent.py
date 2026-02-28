import os
import json
import re
import time
import requests
from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from models import User

aria_bp = Blueprint('aria', __name__)


# ─────────────────────────────────────────────
#  RAG: Oral Health Knowledge Base (Compact)
# ─────────────────────────────────────────────

ORAL_HEALTH_RAG = """
=== ORAL HEALTH REFERENCE ===

ORAL CANCER: 6th most common cancer globally. #1 in Indian men (tobacco/betel nut). Early detection: 80%+ 5-year survival vs 30% late-stage.

RISK FACTORS: Tobacco (6x risk), betel/paan/gutkha, alcohol (6x; +tobacco=15x), HPV-16, sun exposure (lip), poor hygiene, family history, age>40.

SYMPTOMS: White/red patches, non-healing ulcer>2-3 weeks, lump/thickening, pain/numbness, difficulty chewing/swallowing, ear pain, voice change, unexplained bleeding, trismus (<3 fingers).

PAIN: None=no discomfort (early-stage). Mild=slight/occasional. Moderate=consistent, affects eating. High=intense, affects daily life.
BLEEDING: Unexplained oral bleeding (not from brushing) = concerning.
SWELLING: None=normal. Mild=slight. Moderate=noticeable. Severe=affects function.
TRISMUS: Open mouth wide, fit 3 fingers vertically. Pass=normal. Fail=restricted (fibrosis/tumor).

HABITS: Tobacco chewing=submucous fibrosis, 8-10x risk. Smoking=5-6x risk. Alcohol=6x risk. Combined tobacco+alcohol=15-30x risk. More years=higher risk.

PHOTOS: Front View=mouth wide open, tongue relaxed. Left Lateral=turn right, open mouth. Right Lateral=turn left, open mouth. Good lighting, no filters, 15-20cm distance.

RESULTS: Low Risk=continue 6-month checkups. High Risk=needs urgent biopsy/exam. AI screening is a TOOL, not diagnosis.

SEE DOCTOR IF: Sore>3 weeks, unexplained bleeding/pain/numbness, difficulty swallowing, white/red patches, any lump.
"""


# ─────────────────────────────────────────────
#  System Prompt Builder (Compact)
# ─────────────────────────────────────────────

def get_system_prompt(patient_name, doctors_list):
    docs = "\n".join([
        f"  - ID={d['id']}: Dr. {d['name']} ({d['spec']})"
        for d in doctors_list
    ])

    return f"""You are Dr. Yashaswini — a warm, friendly female AI doctor for O-Scan Diagnostics oral cancer screening.

PERSONALITY: Warm, caring, empathetic. Use simple language. Address patient by name. Keep to 2-3 SHORT sentences. Sound human, not robotic.

LANGUAGE: Reply in whatever language the patient uses (Hindi, Kannada, Telugu, Tamil, etc). JSON keys always in English. Only "speech" value in patient's language.

PATIENT: "{patient_name}"

DOCTORS:
{docs}

{ORAL_HEALTH_RAG}

COLLECT THESE FIELDS ONE AT A TIME (ask, wait, acknowledge, next):
1. doctor_id → Ask which doctor. Store numeric ID.
2. pain_level → "None"|"Mild"|"Moderate"|"High"
3. bleeding → "Yes"|"No"
4. swelling → "None"|"Mild"|"Moderate"|"Severe"
5. duration → Free text.
6. history → Free text.
7. habits → "Tobacco","Alcohol","Smoking" or "None"
8. tobacco_years → ONLY if Tobacco mentioned. Number.
9. alcohol_years → ONLY if Alcohol mentioned. Number.
10. smoking_years → ONLY if Smoking mentioned. Number.
11. trismus_test → "Pass"|"Fail"|"Not answered"
12. mouth_pain → "Yes"|"No"|"Not answered"
13. extra_details → Anything else.
14. photo_1 → FRONT VIEW (action_type="request_photo", photo_index=1)
15. photo_2 → LEFT SIDE (photo_index=2)
16. photo_3 → RIGHT SIDE (photo_index=3)

RULES:
- [SESSION_START]: Greet: "Hi [name]! I'm Dr. Yashaswini, guiding your quick oral screening. Which doctor would you like?"
- ONE question per turn. Acknowledge warmly first.
- Map: "a bit"→"Mild", "bad"→"High", "yeah"→"Yes", "nope"/"no"→"No"/"None"
- Medical questions: answer using RAG, then continue.
- NEVER diagnose. Say "the doctor will review".
- Skip habit-year questions for habits not mentioned.
- Don't re-ask filled fields.

RESPOND ONLY valid JSON:
{{"speech":"text","action_type":"fill_field"|"request_photo"|"submit"|null,"field":"field_name"|null,"value":"value"|null,"photo_index":1|2|3|null,"is_complete":false|true}}"""


# ─────────────────────────────────────────────
#  Gemini API Call (Optimized for speed)
# ─────────────────────────────────────────────

def _fallback(msg):
    return {
        "speech": msg,
        "action_type": None, "field": None, "value": None,
        "photo_index": None, "is_complete": False
    }


def call_gemini(messages, system_prompt):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key or api_key == "your_gemini_api_key_here":
        return _fallback(
            "The AI service is not configured. Please add your Gemini API key to the .env file."
        )

    # Build Gemini content
    contents = []
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    # Models ordered by speed & free quota
    MODELS = [
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.5-flash-lite",
    ]

    raw = ""
    for model in MODELS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{model}:generateContent?key={api_key}"
        )

        gen_config = {
            "temperature": 0.75,
            "maxOutputTokens": 200,  # Short replies = faster
        }
        if "2.5" in model:
            gen_config["thinkingConfig"] = {"thinkingBudget": 0}

        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": gen_config
        }

        for attempt in range(1):  # Single attempt per model for speed
            try:
                resp = requests.post(url, json=payload, timeout=10)

                if resp.status_code == 429:
                    print(f"[Dr.Y] {model} => 429 rate limit (attempt {attempt+1})")
                    if attempt == 0:
                        time.sleep(1)  # Minimal wait
                        continue
                    else:
                        break  # try next model

                if resp.status_code != 200:
                    print(f"[Dr.Y] {model} => HTTP {resp.status_code}")
                    break

                raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                raw = raw.strip()

                # Strip markdown code fences
                if raw.startswith("```"):
                    parts = raw.split("```")
                    raw = parts[1] if len(parts) > 1 else raw
                    if raw.lower().startswith("json"):
                        raw = raw[4:]
                raw = raw.strip()

                result = json.loads(raw)

                # Validate required fields
                if "speech" not in result:
                    result["speech"] = "Could you repeat that?"
                for key in ["action_type", "field", "value", "photo_index", "is_complete"]:
                    if key not in result:
                        result[key] = None if key != "is_complete" else False

                print(f"[Dr.Y] Success with {model}")
                return result

            except json.JSONDecodeError:
                m_json = re.search(r'\{.*\}', raw, re.DOTALL)
                if m_json:
                    try:
                        result = json.loads(m_json.group(0))
                        if "speech" in result:
                            for key in ["action_type", "field", "value", "photo_index", "is_complete"]:
                                if key not in result:
                                    result[key] = None if key != "is_complete" else False
                            return result
                    except Exception:
                        pass
                print(f"[Dr.Y] {model} => JSON parse fail")
                break

            except Exception as e:
                print(f"[Dr.Y] {model} => Error: {e}")
                if attempt == 0:
                    time.sleep(1)  # Reduced from 3s
                    continue
                break

    return _fallback("I'm having a small connection issue right now. Could you try again in a moment?")




# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────

@aria_bp.route('/aria/start', methods=['POST'])
@login_required
def aria_start():
    """Initialize Dr. Yashaswini session and get the first greeting."""
    doctors = User.query.filter_by(role='doctor').all()
    doctors_data = [
        {
            "id": d.id,
            "name": d.username,
            "spec": getattr(d, 'specialization', None) or "General Dentistry"
        }
        for d in doctors
    ]

    # Reset session state
    session['aria_history'] = []
    session['aria_patient'] = current_user.username
    session['aria_doctors'] = doctors_data
    session['aria_form'] = {}

    system_prompt = get_system_prompt(current_user.username, doctors_data)
    boot_messages = [{"role": "user", "content": "[SESSION_START] Begin the intake."}]
    response = call_gemini(boot_messages, system_prompt)

    session['aria_history'] = [
        {"role": "user", "content": "[SESSION_START] Begin the intake."},
        {"role": "assistant", "content": response.get("speech", "")}
    ]

    return jsonify({
        "response": response,
        "doctors": doctors_data,
        "patient_name": current_user.username
    })


@aria_bp.route('/aria/chat', methods=['POST'])
@login_required
def aria_chat():
    """Send a patient message to Dr. Yashaswini and get a response."""
    data = request.get_json()
    user_message = (data.get('message') or '').strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history = session.get('aria_history', [])
    patient_name = session.get('aria_patient', current_user.username)
    doctors_list = session.get('aria_doctors', [])
    form_data = session.get('aria_form', {})

    # Compact context — only field names, not values (reduce tokens)
    filled_keys = list(form_data.keys()) if form_data else []
    context_prefix = f"[FILLED: {','.join(filled_keys)}] " if filled_keys else ""
    context_msg = f"{context_prefix}{user_message}"

    system_prompt = get_system_prompt(patient_name, doctors_list)
    history.append({"role": "user", "content": context_msg})

    response = call_gemini(history, system_prompt)
    history.append({"role": "assistant", "content": response.get("speech", "")})

    # Track filled fields server-side
    if response.get("action_type") == "fill_field" and response.get("field"):
        form_data[response["field"]] = response.get("value", "")

    # Keep last 20 messages (reduced from 30 — less tokens)
    session['aria_history'] = history[-14:]
    session['aria_form'] = form_data

    return jsonify(response)
