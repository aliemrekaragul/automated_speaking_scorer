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
- User-friendly configuration interface
- Session-based task management
- Automatic task ID generation
- Real-time scoring progress tracking
- Detailed error logging and reporting

## Project Structure

```
automated_speaking_scorer/
├── agents/                      # Scoring agent implementations
│   ├── analytic_scoring_agent.py    # Handles detailed scoring across dimensions
│   ├── holistic_scoring_agent.py    # Provides overall performance scores
│   ├── off_topic_detection_agent.py # Detects off-topic responses
│   └── score_adjustment_agent.py    # Adjusts and normalizes scores
├── prompts/                    # AI model prompts for scoring
│   ├── analytic_scoring_prompts.py  # Prompts for analytic scoring
│   ├── holistic_scoring_prompts.py  # Prompts for holistic scoring
│   └── off_topic_detection_prompts.py # Prompts for off-topic detection
├── utils/                     # Utility functions and helpers
│   ├── config_manager.py     # Configuration management
│   ├── excel_utils.py        # Excel file handling utilities
│   ├── file_utils.py         # File operations utilities
│   └── response_parser.py    # Model response parsing utilities
├── ui/                       # User interface components
│   ├── __init__.py
│   └── main_window.py       # Main application window
├── resources/               # Application resources
│   └── app_icon.ico        # Application icon
├── main.py                  # Main application entry point
├── build.py                # Build script for executable
├── SpeakingScorer.spec     # PyInstaller specification
├── task_definitions.py      # Speaking task definitions
├── config.example.json     # Example configuration file
└── requirements.txt         # Python dependencies
```

## Prerequisites

- Python 3.8 or higher
- Required Python packages (listed in requirements.txt)
- Google API keys for:
  - Analytic Scoring
  - Holistic Scoring
  - Off-topic Detection
- Sufficient disk space for audio processing

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aliemrekaragul/automated_speaking_scorer.git
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

## Usage

1. Launch the application:
```bash
python main.py
```

2. Configure the application:
   - Click the "Configuration" button in the main window
   - Enter your API keys (get them from https://makersuite.google.com/app/apikey)
   - Define speaking tasks using the session management interface
   - Tasks are automatically assigned IDs (t1, t2, etc.)
   - Click Save to store your configuration

3. Score speaking performances:
   - Click "Select Folder" to choose a directory with audio files
   - Select the desired scoring options
   - Click "Start Scoring" to begin the process
   - Monitor progress in real-time
   - Results will be saved in the output directory as Excel files

## Creating Executable

1. Install PyInstaller and other dependencies:
```bash
pip install -r requirements.txt
```

2. Build the executable:
```bash
python build.py
```

The executable will be created in the `dist` directory as `Speaking Scorer.exe` (Windows) or `Speaking Scorer` (macOS/Linux).

### Using the Executable

1. Run the executable
2. Configure the application:
   - Click the "Configuration" button
   - Enter your API keys
   - Create sessions and define tasks
   - Tasks IDs are automatically generated
   - Click Save
3. Select a folder containing audio files
4. Choose scoring options and start the process

**Important Notes**: 
- The configuration is stored in `config.json` next to the executable
- API keys must be set before scoring can begin
- Error logs are stored in the same directory as the executable

## Configuration

The system looks for configuration in the following locations and order:

1. `config.json` in the same directory as the executable (when running the .exe) or in the project root directory (when running from source)
2. Environment variables in the system
   - No .env file is used directly
   - Environment variables must be set in the system settings
   - Only used for API keys if they're not found in config.json

An example configuration file is provided as `config.example.json`. To get started:

1. Copy the example config:
```bash
cp config.example.json config.json
```

2. Edit `config.json` with your API keys and task definitions

The `config.json` file structure:

```json
{
    "ANALYTIC_SCORING_API_KEY": "your-key-here",
    "HOLISTIC_SCORING_API_KEY": "your-key-here",
    "OFF_TOPIC_DETECTION_API_KEY": "your-key-here",
    "TASK_DEFINITIONS": {
        "1": {
            "t1": "Task description for session 1, task 1",
            "t2": "Task description for session 1, task 2"
        },
        "2": {
            "t1": "Task description for session 2, task 1",
            "t2": "Task description for session 2, task 2"
        }
    }
}
```

Configuration can be managed through:
1. The built-in configuration UI (recommended)
   - Opens when clicking the "Configuration" button
   - Changes are automatically saved to config.json
   - Provides user-friendly interface for task management

2. Direct editing of config.json (advanced users)
   - Must follow the exact JSON structure shown above
   - Be careful with JSON syntax
   - See config.example.json for a complete example with sample tasks

When running the executable:
- Place config.json in the same folder as the .exe file
- The app will create config.json if it doesn't exist
- All changes made through the UI are saved to this file

When running from source:
- config.json should be in the project root directory
- The app will create it if it doesn't exist
- Changes are saved relative to the main.py location

## Output Format

The Excel output includes:
- Student information
- Task details
- Analytic scores for each dimension
- Holistic overall score
- Off-topic analysis results
- Detailed feedback and comments
- Error logs (if any)

## Error Handling

The application includes comprehensive error handling:
- Missing API keys are reported clearly
- Scoring errors are logged with timestamps
- Failed scoring attempts can be retried
- Error logs are saved for troubleshooting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
