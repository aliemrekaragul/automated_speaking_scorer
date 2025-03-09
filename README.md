# Automated Speaking Scorer

An automated system for scoring English speaking performances using AI models. The system analyzes audio recordings for grammar, vocabulary, content, fluency, pronunciation, and provides both analytic and holistic scores.

## Features

- Automated scoring of English speaking performances
- Multiple scoring dimensions:
  - Analytic scoring (grammar, vocabulary, content, fluency, pronunciation)
  - Holistic scoring (overall performance)
  - Off-topic detection
- Excel report generation with detailed scoring breakdown
- Support for multiple audio formats (mp3, wav, m4a, aac, ogg, flac)
- Configurable scoring criteria and rubrics

## Project Structure

```
automated_speaking_scorer/
├── agents/                      # Scoring agent implementations
│   ├── analytic_scoring_agent.py    # Handles detailed scoring across dimensions
│   ├── holistic_scoring_agent.py    # Provides overall performance scores
│   ├── off_topic_detection_agent.py # Detects off-topic responses
│   └── score_adjustment_agent.py    # Adjusts and normalizes scores
├── models/                     # Core model implementations
│   └── score_models.py        # Base scoring model definitions
├── utils/                     # Utility functions and helpers
│   ├── excel_utils.py        # Excel file handling utilities
│   ├── file_utils.py         # File operations utilities
│   └── response_parser.py    # Model response parsing utilities
├── ui/                       # User interface components
├── main.py                  # Main application entry point
├── task_definitions.py      # Speaking task definitions
├── requirements.txt         # Python dependencies
└── .env.example            # Example environment variables
```

## Prerequisites

- Python 3.8 or higher
- Required Python packages (listed in requirements.txt)
- Google Cloud API credentials for the Gemini model
- Sufficient disk space for audio processing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/automated_speaking_scorer.git
cd automated_speaking_scorer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Usage

1. Launch the application:
```bash
python main.py
```

2. Configure the application:
   - Click the "Configuration" button in the main window
   - Enter your Google API key (get one from https://makersuite.google.com/app/apikey)
   - Define speaking tasks in the format "task_id: task_description"
   - Click Save to store your configuration

3. Score speaking performances:
   - Click "Select Folder" to choose a directory with audio files
   - Select the desired scoring options
   - Click "Start Scoring" to begin the process
   - Results will be saved in the output directory as Excel files

## Creating Executable

You can create a standalone executable for this application using the following steps:

1. Install the required dependencies (including PyInstaller):
```bash
pip install -r requirements.txt
```

2. Run the build script:
```bash
python build.py
```

The executable will be created in the `dist` directory. On Windows, it will be `dist/SpeakingScorer.exe`, and on macOS/Linux, it will be `dist/SpeakingScorer`.

### Using the Executable

1. Run the executable by double-clicking it
2. Configure the application:
   - Click the "Configuration" button
   - Enter your Google API key
   - Define your speaking tasks
   - Click Save
3. Select a folder containing audio files
4. Choose scoring options and start the process

**Note**: The configuration is stored in a `config.json` file next to the executable. You can update the configuration at any time using the Configuration button.

## Configuration

The system can be configured through the UI or manually by editing `config.json`:

```json
{
    "GOOGLE_API_KEY": "your-api-key-here",
    "TASK_DEFINITIONS": {
        "1": "Describe your favorite hobby",
        "2": "Talk about your future plans",
        // ... add more tasks as needed
    }
}
```

Additional settings that can be configured:
- `MODEL_NAME`: The specific Gemini model to use
- `MAX_RETRIES`: Maximum number of API retry attempts
- `RETRY_DELAY`: Delay between retries in seconds

## Output Format

The Excel output includes:
- Student information
- Task details
- Analytic scores for each dimension
- Holistic overall score
- Off-topic analysis results
- Detailed feedback and comments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
