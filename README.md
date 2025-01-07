# PM Coach

## Summary
A brief description of your project goes here. Please replace this text with a concise explanation of what your project does and its main features.

## Requirements
- Python 3.8 or higher
- pip (Python package installer)

## Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/yourproject.git
   cd yourproject
   ```

   Make sure to modify your .env file with your Jira info and OpenAI API keys.
   ```bash
   cp .env.example .env
   ```

2. Install required dependencies
   Locally:
   ```bash
   pip install -r requirements.txt
   ```

   Docker:
   ```bash
   docker build -t pm-coach .
   ```

3. Run the application
   Locally:
   ```bash
   fastapp run app.py
   ```

   Or if using Docker: 
   ```bash
   docker run -e JIRA_SERVER="" \
           -e JIRA_EMAIL="" \
           -e JIRA_API_TOKEN="" \
           -e WEBHOOK_SECRET="" \
           -e OPENAI_API_KEY="" \
           pm-coach
   ```