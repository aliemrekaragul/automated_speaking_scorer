import google.generativeai as genai
from models.score_models import AnalyticScores
from utils.file_utils import read_file_as_bytes
import os
import re
from task_definitions import TASK_DEFINITIONS
from utils.response_parser import ResponseParser
import time
from typing import Any
import json
import requests
from utils.config_manager import ConfigManager

class AnalyticScoringAgent:
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 60  # seconds
    MODEL_NAME = 'models/gemini-1.5-flash'

    def __init__(self):
        self.api_key = ConfigManager.get_api_key("ANALYTIC_SCORING_API_KEY")
        if not self.api_key:
            raise ValueError("ANALYTIC_SCORING_API_KEY not found in configuration")
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
            "See the task and the band definitions for each rubric domain below.",
            "You will be provided with an audio file of a response to the given task.",
            "For each rubric domain, consider the student's performance on the domain and classify the student into a band.",
            "DO NOT punish the student for incomplete final sentences because the audio files are trimmed at a time limit after the performance is recorded.",
            "Reply as JSON in this format: { grammar: number, vocabulary: number, content: number, fluency: number, pronunciation: number, overall: number }",
            "",
            "<TASK_DEFINITION>",
            "<<TASK_DEFINITION>>",
            "</TASK_DEFINITION>",
            "",    
            "<BAND_DEFINITIONS>",
            "<GRAMMAR>",
            "-BAND 5: Place the student here even if there are a lot of grammar errors, but the errors interefere with the meaning in less than 50% of the statements.",
            "Also, place  the student here if there  is at least one complicated sentence, sentences with a relative clause, a noun clause, or an adverbial clause.",
            "This band corresponds to Intermediate or higher levels.",
            "-BAND 4: Place the student here even if there are a lot of grammar errors, but the errors interefere with the meaning in less than 50% of the statements.",
            "This band corresponds to Elementary level.",
            "-BAND 3: Place the student here if there are a lot of grammar errors, and the errors interefere with the meaning during more than 50% of the statements.",
            "This band corresponds to Beginner level.",
            "-BAND 2: Place the student here if there are a lot of grammar errors, and the errors interefere with the meaning during more than 70% of the statements.",
            "This band corresponds to Beginner level.",
            "-BAND 1: Place the student here if there are a lot of grammar errors, and the errors interefere with the meaning during more than 90% of the statements.",
            "This band corresponds to Foundations level.",
            "</GRAMMAR>",
            "",
            "<VOCABULARY>",
            "-BAND 5: Place the student here even if there are a lot of incorrect use of vocabulary items to deal with topic, but these errors interefere with the meaning in less than 50% of the statements.",
            "Also, place  the student here if there  is at least one complex vocabulary item, idiomatic expression, or phrasal verb that corresponds to upper-intermediate or a higher level..",
            "This band corresponds to Intermediate or higher levels.",
            "-BAND 4: Place the student here even if there are a lot of incorrect use of vocabulary items to deal with topic, but these errors interefere with the meaning in less than 50% of the statements.",
            "This band corresponds to Elementary level.",
            "-BAND 3: Place the student here if there are a lot of incorrect use of vocabulary items to deal with topic, and these errors interefere with the meaning during more than 50% of the statements.",
            "This band corresponds to Beginner level.",
            "-BAND 2: Place the student here if there are a lot of incorrect use of vocabulary items to deal with topic, and these errors interefere with the meaning during more than 70% of the statements.",
            "This band corresponds to Beginner level.",
            "-BAND 1: Place the student here if there are a lot of incorrect use of vocabulary items to deal with topic, and these errors interefere with the meaning during more than 90% of the statements.",
            "This band corresponds to Foundations level.",
            "</VOCABULARY>",
            "",
            "<CONTENT>",
            "-BAND 5: Place the student here if there is at least one example or explanation relevant to the topic.",
            "This band corresponds to Intermediate or higher levels.",
            "-BAND 4: Place the student here even if the content is repeated, but some of the ideas are clear.",
            "This band corresponds to Elementary level.",
            "-BAND 3: Place the student here if lack of content (repetition or no explanation/examplification) make most of the ideas unclear.",
            "This band corresponds to Beginner level.",
            "-BAND 2: Place the student here if there is no content that almost none of the ideas are clear.",
            "This band corresponds to Beginner level.",
            "-BAND 1: Place the student here if there is no or very little understandable content.",
            "This band corresponds to Foundations level.",
            "</CONTENT>",
            "",
            "<FLUENCY>",    
            "-BAND 5: Place the student here even if there are  a lot of hesitation with pauses. Verbal stutters and filler words are present almost after every two or three words.",
            "This band corresponds to Intermediate or higher levels.",
            "-BAND 4: Place the student here even if there are a lot of hesitation with pauses. Verbal stutters and filler words are present almost after every two or three words.",
            "This band corresponds to Elementary level.",
            "-BAND 3: Place the student here if there are a lot of hesitation with pauses. Verbal stutters and filler words are present almost after every word.",
            "This band corresponds to Beginner level.",
            "-BAND 2: Place the student here if there are a lot of hesitation and very long pauses. Verbal stutters and filler words are present almost after every word.",
            "This band corresponds to Beginner level.",
            "-BAND 1: Place the student here if the performance is so much paused that there is only a couple of meaningful words and the rest is verbal stutters like 'uh' or 'hmm'. ",
            "This band corresponds to Foundations level.",
            "</FLUENCY>",
            "",
            "<PRONUNCIATION>",
            "-BAND 5: Place the student here even if there are a lot of pronunciation errors, but these errors rarely  (less than 40% of the time) interefere with the meaning.",
            "Also, place  the student here if there  is at least one complex word or phrase, which corresponds to upper-intermediate or a higher level, pronounced correctly.",
            "This band corresponds to Intermediate or higher levels.",
            "-BAND 4: Place the student here even if there are a lot of pronunciation errors, but these errors sometimes  (less than 50% of the time) interefere with the meaning.",
            "But some of the ideas are clear.",
            "This band corresponds to Elementary level.",
            "-BAND 3: Place the student here if there are a lot of pronunciation errors, and these errors usually  (more than 50% of the time) interefere with the meaning.",
            "This band corresponds to Beginner level.",
            "-BAND 2: Place the student here if there are a lot of pronunciation errors, and these errors mostly  (more than 70% of the time) interefere with the meaning.",
            "Almost none of the ideas are clear.",
            "This band corresponds to Beginner level.",
            "-BAND 1: Place the student here if there are a lot of pronunciation errors, and these errors almost always  (more than 90% of the time) interefere with the meaning.",
            "This band corresponds to Foundations level.",
            "</PRONUNCIATION>",
            "",
            "<OVERALL>",
            "-BAND 5: Intermediate",
            "-BAND 4: Pre-intermediate",
            "-BAND 3: Elementary",
            "-BAND 2: Beginner",
            "-BAND 1: Foundations",
            "</OVERALL>",
            "</BAND_DEFINITIONS>"
        ]
        self.prompt_template = "\n".join(prompt_lines)
    
    def _parse_file_name(self, file_path: str) -> tuple[str, str]:
        """Parse the file name to get session and task IDs."""
        # Extract session and task IDs from file name (e.g., 231101013-6-t1.mp3)
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

    async def score_performance(self, file_path: str) -> AnalyticScores:
        """Score the speaking performance analytically using Gemini."""
        try:
            session_id, task_id = self._parse_file_name(file_path)
            task_definition = TASK_DEFINITIONS[session_id][task_id]
            
            audio_bytes = read_file_as_bytes(file_path)
            
            prompt = self.prompt_template.replace("<<TASK_DEFINITION>>", task_definition)
            
            response = await self._generate_content_with_retry(prompt, audio_bytes)
            
            scores_dict = ResponseParser.parse_analytic_response(response.text)
            if scores_dict is None:
                raise ValueError(f"Failed to parse response: {response.text}")
            
            return AnalyticScores(**scores_dict)
            
        except Exception as e:
            raise ValueError(f"Error scoring performance: {str(e)}") 