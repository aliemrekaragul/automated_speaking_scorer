import google.generativeai as genai
from models.score_models import OffTopicAnalysis
from utils.file_utils import read_file_as_bytes
import re
from task_definitions import TASK_DEFINITIONS
from utils.response_parser import ResponseParser
import time
from typing import Any
from utils.config_manager import ConfigManager
from prompts.off_topic_detection_prompts import SYSTEM_PROMPT

class OffTopicDetectionAgent:
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 60  
    MODEL_NAME = 'models/gemini-1.5-flash'

    def __init__(self):
        self.api_key = ConfigManager.get_api_key("OFF_TOPIC_DETECTION_API_KEY")
        if not self.api_key:
            raise ValueError("OFF_TOPIC_DETECTION_API_KEY not found in configuration")
        self._initialize_model()
        self.prompt_template = "\n".join(SYSTEM_PROMPT)
    
    def _initialize_model(self) -> None:
        """Initialize the Gemini model with API key."""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.MODEL_NAME)

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

    async def analyze_topic_relevance(self, file_path: str) -> OffTopicAnalysis:
        """Analyze if the speech is off-topic using Gemini."""
        try:
            session_id, task_id = self._parse_file_name(file_path)
            task_definition = TASK_DEFINITIONS[session_id][task_id]
            
            audio_bytes = read_file_as_bytes(file_path)
            
            prompt = self.prompt_template.replace("<<TASK_DEFINITION>>", task_definition)
            
            response = await self._generate_content_with_retry(prompt, audio_bytes)
            
            result = ResponseParser.parse_off_topic_response(response.text)
            if result is None:
                raise ValueError(f"Failed to parse response: {response.text}")
            
            return OffTopicAnalysis(**result)
            
        except Exception as e:
            raise ValueError(f"Error analyzing topic relevance: {str(e)}") 