# SNS Post Generator

## Overview

Generates SNS posts using AI based on YAML files containing person details.

## Environment Variables

1. Copy the Example Environment File

    In the project root directory, there's a file named `.env.example.` This file contains all the necessary environment variables that the application needs, but with placeholder or sample values.

    Create a copy of this file in the same directory and name it `.env`.

2. Edit the .env File

    Replace `SERVER_ENDPOINT` and `OPENAI_API_KEY`.

## Setup

1. Install all required modules and libraries.
2. Place YAML files with person details inside the `people` directory.
3. Each person should have a corresponding `.png` image (their profile picture) in the `people` directory. Ensure the image filename matches the YAML filename.

## How To Use

Run the script:

```bash
pip install requirements.txt
python main.py
```

The generated SNS posts will be saved as .png files in the temp directory.

# Functions
- `generate_situation(yaml_path)`
    
    Generates a possible situation for the SNS post based on the YAML file of the person.

- `generate_instagram_post(yaml_path, situation, save_dir=None)`

    Produces an SNS post mockup based on the situation and saves it to a directory.

# Execution
When you run the main script, it reads every `.yaml` file in the people directory, generates a situation for the person, and then creates an SNS post mockup.

# Notes
AI-generated situations may vary in accuracy. It's advisable to verify the outputs.

# Future Enhancements
- Add diverse situations.
- Improve AI prompt for more contextual posts.