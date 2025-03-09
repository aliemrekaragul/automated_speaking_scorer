import json
import re

class ResponseParser:
    """
    Utility class to parse API responses for different scoring agents.
    """

    @staticmethod
    def parse_analytic_response(response: str) -> dict:
        try:
            parsed = json.loads(response)
            return {
                "grammar": parsed.get("grammar", 0),
                "vocabulary": parsed.get("vocabulary", 0),
                "content": parsed.get("content", 0),
                "fluency": parsed.get("fluency", 0),
                "pronunciation": parsed.get("pronunciation", 0),
                "overall": parsed.get("overall", 0)
            }
        except json.JSONDecodeError:
            match = re.search(r'\{.*?\}', response, re.DOTALL)
            if match:
                json_str = match.group(0).replace('\n', '').replace('\\', '')
                try:
                    parsed = json.loads(json_str)
                    return {
                        "grammar": parsed.get("grammar", 0),
                        "vocabulary": parsed.get("vocabulary", 0),
                        "content": parsed.get("content", 0),
                        "fluency": parsed.get("fluency", 0),
                        "pronunciation": parsed.get("pronunciation", 0),
                        "overall": parsed.get("overall", 0)
                    }
                except json.JSONDecodeError:
                    return None
            else:
                return None

    @staticmethod
    def parse_holistic_response(response: str) -> dict:
        try:
            parsed = json.loads(response)
            return {
                "overall_score": parsed.get("overall_score", 0)
            }
        except json.JSONDecodeError:
            match = re.search(r'\{.*?\}', response, re.DOTALL)
            if match:
                json_str = match.group(0).replace('\n', '').replace('\\', '')
                try:
                    parsed = json.loads(json_str)
                    return {
                        "overall_score": parsed.get("overall_score", 0)
                    }
                except json.JSONDecodeError:
                    return None
            else:
                return None

    @staticmethod
    def parse_off_topic_response(response: str) -> dict:
        try:
            parsed = json.loads(response)
            return {
                "is_off_topic": parsed.get("off_topic", False),
                "confidence": parsed.get("confidence", 0.0),  
                "explanation": parsed.get("explanation", "")  
            }
        except json.JSONDecodeError:
            match = re.search(r'\{.*?\}', response, re.DOTALL)
            if match:
                json_str = match.group(0).replace('\n', '').replace('\\', '')
                try:
                    parsed = json.loads(json_str)
                    return {
                        "is_off_topic": parsed.get("off_topic", False),
                        "confidence": parsed.get("confidence", 0.0),  
                        "explanation": parsed.get("explanation", "")  
                    }
                except json.JSONDecodeError:
                    return None
            else:
                return None 