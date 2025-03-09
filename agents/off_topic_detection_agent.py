import google.generativeai as genai
from models.score_models import OffTopicAnalysis
from utils.file_utils import read_file_as_bytes
import os
import json
import re
from task_definitions import TASK_DEFINITIONS
from utils.response_parser import ResponseParser
import time
from typing import Any, Optional

class OffTopicResponseParser:
    """
    Utility class to parse off-topic detection API responses.
    """
    @staticmethod
    def parse(response: str) -> dict:
        try:
            parsed = json.loads(response)
            return {
                "is_off_topic": parsed.get("off_topic", False),
                "confidence": 0.95,  # High confidence since it's a binary decision
                "explanation": "The response is " + ("not " if not parsed.get("off_topic", False) else "") + "relevant to the given topic."
            }
        except json.JSONDecodeError:
            match = re.search(r'\{.*?\}', response, re.DOTALL)
            if match:
                json_str = match.group(0).replace('\n', '').replace('\\', '')
                try:
                    parsed = json.loads(json_str)
                    return {
                        "is_off_topic": parsed.get("off_topic", False),
                        "confidence": 0.95,  # High confidence since it's a binary decision
                        "explanation": "The response is " + ("not " if not parsed.get("off_topic", False) else "") + "relevant to the given topic."
                    }
                except json.JSONDecodeError:
                    return None
            else:
                return None

class OffTopicDetectionAgent:
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 60  # seconds
    MODEL_NAME = 'models/gemini-1.5-flash'

    def __init__(self):
        self._initialize_model()
        self._initialize_prompt_template()
    
    def _initialize_model(self) -> None:
        """Initialize the Gemini model with API key."""
        api_key = os.getenv("OFF_TOPIC_DETECTION_API_KEY")
        if not api_key:
            raise ValueError("OFF_TOPIC_DETECTION_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(self.MODEL_NAME)

    def _initialize_prompt_template(self) -> None:
        """Initialize the scoring prompt template."""
        prompt_lines = [
            "You are an expert in analyzing whether a student's speech response is on-topic or off-topic.",
            "You will be provided with a task definition and an audio file of a student's response.",
            "Analyze if the response addresses the given task or goes off-topic.",
            "Consider partial relevance and tangential discussions in your analysis.",
            "DO NOT punish the student for incomplete final sentences because the audio files are trimmed at a time limit after the performance is recorded.",
            "Reply as JSON in this format: { off_topic: boolean, confidence: number, explanation: string }",
            "The confidence should be between 0 and 1, indicating how certain you are about your assessment.",
            "The explanation should briefly justify your decision.",
            "",
            "<TASK_DEFINITION>",
            "<<TASK_DEFINITION>>",
            "</TASK_DEFINITION>"
        ]
        self.prompt_template = "\n".join(prompt_lines)
    
    def _parse_file_name(self, file_path: str) -> tuple[str, str]:
        """Parse the file name to get session and task IDs."""
        match = re.search(r'-(\d+)-t(\d+)\.mp3$', file_path)
        if not match:
            raise ValueError(f"Invalid file name format: {file_path}")
        session_id, task_id = match.groups()
        return session_id, f"t{task_id}"
    
    async def _generate_content_with_retry(self, prompt: str, audio_bytes: bytes) -> Any:
        """Generate content with retry logic for handling rate limits."""
        retry_count = 0
        last_exception = None
        
        while retry_count < self.MAX_RETRIES:
            try:
                return self.model.generate_content([
                    prompt,
                    {
                        "mime_type": "audio/mp3",
                        "data": audio_bytes
                    }
                ])
            except Exception as e:
                last_exception = e
                if "429" in str(e):  # Rate limit error
                    retry_count += 1
                    if retry_count < self.MAX_RETRIES:
                        # Exponential backoff
                        delay = self.INITIAL_RETRY_DELAY * (2 ** (retry_count - 1))
                        print(f"Rate limit reached. Retrying in {delay} seconds... (Attempt {retry_count + 1}/{self.MAX_RETRIES})")
                        time.sleep(delay)
                        continue
                raise ValueError(f"Error generating content: {str(e)}")
        
        raise ValueError(f"Max retries ({self.MAX_RETRIES}) exceeded. Last error: {str(last_exception)}")

    async def analyze_topic_relevance(self, file_path: str) -> OffTopicAnalysis:
        """Analyze if the speech is off-topic using Gemini."""
        try:
            # Get the task definition based on file name
            session_id, task_id = self._parse_file_name(file_path)
            task_definition = TASK_DEFINITIONS[session_id][task_id]
            
            audio_bytes = read_file_as_bytes(file_path)
            
            prompt = self.prompt_template.replace("<<TASK_DEFINITION>>", task_definition)
            
            # Generate content with retry logic
            response = await self._generate_content_with_retry(prompt, audio_bytes)
            
            # Parse the response
            result = ResponseParser.parse_off_topic_response(response.text)
            if result is None:
                raise ValueError(f"Failed to parse response: {response.text}")
            
            # Create and return OffTopicAnalysis object
            return OffTopicAnalysis(**result)
            
        except Exception as e:
            raise ValueError(f"Error analyzing topic relevance: {str(e)}") 