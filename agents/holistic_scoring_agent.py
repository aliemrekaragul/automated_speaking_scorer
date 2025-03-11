import google.generativeai as genai
from models.score_models import HolisticScore
from utils.file_utils import read_file_as_bytes
import os
import re
from task_definitions import TASK_DEFINITIONS
from utils.response_parser import ResponseParser
import time
from typing import Any, Optional
import json
import requests
from utils.config_manager import ConfigManager

class HolisticScoringAgent:
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 60  # seconds
    MODEL_NAME = 'models/gemini-1.5-flash'

    def __init__(self):
        self.api_key = ConfigManager.get_api_key("HOLISTIC_SCORING_API_KEY")
        if not self.api_key:
            raise ValueError("HOLISTIC_SCORING_API_KEY not found in configuration")
        self._initialize_model()
        self._initialize_prompt_template()
    
    def _initialize_model(self) -> None:
        """Initialize the Gemini model with API key."""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.MODEL_NAME)

    def _initialize_prompt_template(self) -> None:
        """Initialize the scoring prompt template."""
        prompt_lines = [
            "You are a speaking performance classifier for students of English as a second language.",
            "See the task and the band definitions below.",
            "You will be provided with an audio file of a response to the given task.",
            "Consider the student's overall performance and classify the student into a band.",
            "DO NOT punish the student for incomplete final sentences because the audio files are trimmed at a time limit after the performance is recorded.",
            "Reply as JSON in this format: { overall_score: number }",
            "",
            "<TASK_DEFINITION>",
            "<<TASK_DEFINITION>>",
            "</TASK_DEFINITION>",
            "",
            "<BAND_DEFINITIONS>",
            "85-100: Intermediate or higher",
            "70-84: Pre-intermediate",
            "60-69: Elementary",
            "35-59: Beginner",
            "0-34: Foundations",
            "</BAND_DEFINITIONS>"
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
                        delay = self.INITIAL_RETRY_DELAY * (2 ** (retry_count - 1))
                        print(f"Rate limit reached. Retrying in {delay} seconds... (Attempt {retry_count + 1}/{self.MAX_RETRIES})")
                        time.sleep(delay)
                        continue
                raise ValueError(f"Error generating content: {str(e)}")
        
        raise ValueError(f"Max retries ({self.MAX_RETRIES}) exceeded. Last error: {str(last_exception)}")

    async def score_performance(self, file_path: str) -> HolisticScore:
        """Score the speaking performance holistically using Gemini."""
        try:
            session_id, task_id = self._parse_file_name(file_path)
            task_definition = TASK_DEFINITIONS[session_id][task_id]
            
            audio_bytes = read_file_as_bytes(file_path)
            
            prompt = self.prompt_template.replace("<<TASK_DEFINITION>>", task_definition)
            
            response = await self._generate_content_with_retry(prompt, audio_bytes)
            
            result = ResponseParser.parse_holistic_response(response.text)
            if result is None:
                raise ValueError(f"Failed to parse response: {response.text}")
            
            return HolisticScore(**result)
            
        except Exception as e:
            raise ValueError(f"Error scoring performance: {str(e)}") 