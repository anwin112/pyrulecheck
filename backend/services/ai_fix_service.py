import json
import os
import time
from google import genai  # type: ignore
from google.genai.errors import ClientError  # type: ignore
import logging
import uuid
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RateLimitError(Exception):
    pass

def generate_fixes_for_issues(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a list of critical/major issues and passes them to the Gemini API
    to suggest secure fixes. If the API fails or is not configured, returns an empty list.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not found. Skipping AI fix generation.")
        print("ai_fix_service: GEMINI_API_KEY not found.")
        return []

    try:
        print(f"ai_fix_service: Received {len(issues)} issues to process.")
        client = genai.Client(api_key=api_key)
        # Using the available newer model alias since 1.5 is region-locked or deprecated for this key
        
        system_prompt = (
            "You are a senior Python security engineer.\n\n"
            "You will receive a list of vulnerabilities already detected by a static rule engine.\n\n"
            "Your task:\n"
            "- Explain why each issue is dangerous\n"
            "- Suggest secure and production-ready fixes\n"
            "- Provide a corrected code snippet\n"
            "- Follow best practices\n"
            "- Keep explanations concise but technical\n"
            "- Do not re-detect issues\n"
            "- Do not hallucinate additional vulnerabilities\n\n"
            "Return your response strictly in this JSON format:\n"
            '{\n'
            '  "fix_suggestions": [\n'
            '    {\n'
            '      "fix_id": "<generate a unique string identifier like SEC-001>",\n'
            '      "file": "<filename>",\n'
            '      "line": <integer>,\n'
            '      "issue_type": "<type of issue>",\n'
            '      "risk_explanation": "<concise technical explanation>",\n'
            '      "recommended_fix_explanation": "<concise fix explanation>",\n'
            '      "secure_code_example": "<corrected code snippet>"\n'
            '    }\n'
            '  ]\n'
            '}'
        )

        
        # Prepare the subset of data to send to avoid excessive token usage
        simplified_issues = []
        for issue in issues:
            simplified_issues.append({
                "file": issue.get("file"),
                "line": issue.get("line"),
                "issue_type": issue.get("rule_id"),
                "description": issue.get("message")
            })

        user_prompt = json.dumps({"issues": simplified_issues})
        
        full_prompt = f"{system_prompt}\n\nHere are the detected issues:\n{user_prompt}"
        
        max_retries = 1 # No retries for rate limits to prevent spamming the quota
        
        try:
            response = client.models.generate_content(
                model=os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash'),
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            print("ai_fix_service: Received response from Gemini.")
            result_json = json.loads(response.text)
            with open("debug_api.txt", "a") as f:
                f.write(f"Raw response: {response.text}\n")
            suggestions = result_json.get("fix_suggestions", [])
            
            # Ensure a fix_id exists in case the model dropped it
            for s in suggestions:
                if not s.get("fix_id"):
                    s["fix_id"] = str(uuid.uuid4())
                    
            return suggestions
            
        except ClientError as e:
            if e.code == 429:
                logger.warning(f"Rate limited by Gemini API. Aborting to save quota.")
                print(f"ai_fix_service: Rate limited (429).")
                raise RateLimitError("Gemini API Rate Limit Exceeded")
            else:
                logger.error(f"Gemini API request failed: {e}")
                with open("debug_api.txt", "a") as f: f.write(f"ClientError: {e}\n")
                raise e
        except Exception as e:
            logger.error(f"Gemini API fix generation failed: {e}")
            with open("debug_api.txt", "a") as f: f.write(f"Exception: {e}\n")
            raise e

    except RateLimitError as e:
        raise e
    except Exception as e:
        print(f"ai_fix_service: exception: {e}")
        logger.error(f"Gemini API fix generation failed: {e}")
        with open("debug_api.txt", "a") as f: f.write(f"Final Exception: {e}\n")
        return []

