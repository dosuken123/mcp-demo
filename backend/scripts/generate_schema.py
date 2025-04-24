#!/usr/bin/env python3
"""
generate_schema.py - Generates Pydantic models from JSON schema using Anthropic API

This script:
1. Downloads the JSON schema from the MCP repository
2. Sends the schema to Anthropic's API with a prompt to create Pydantic classes
3. Extracts the code from the response
4. Saves the output to mcp/schema.py
"""

import os
import json
import sys
import requests
import re
from pathlib import Path

# Configuration
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = "claude-3-7-sonnet-20250219"  # Using Opus for the best code generation
JSON_SCHEMA_URL = os.environ.get("JSON_SCHEMA_URL")
OUTPUT_FILE = "backend/mcp/schema.py"

def download_schema():
    """Download the JSON schema from GitHub"""
    print("Downloading JSON schema...")
    response = requests.get(JSON_SCHEMA_URL)
    response.raise_for_status()
    return response.text

def call_anthropic_api(schema):
    """Call the Anthropic API with the schema to generate Pydantic classes"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    print(f"Calling Anthropic API using model {ANTHROPIC_MODEL}...")
    
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    if os.path.isfile(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as file:
            current_file = file.read()
    else:
        current_file = ""

    
    prompt = f"""
```json
{schema}
```

Convert this JSON schema into Pydantic classes for a python project.
Copy descriptions in the JSON schema to the Pydantic classes as docstrings.
Use StrEnum module if it's enum structure that uses string type for the values.
If the root `type` is not `object` or undefined, define a type alias instead of using BaseModel.
Do not omit for brevity.
Do not add docsstrings that does not exist in the JSON schema.
Do not use Fields module if the name of the field starts with underscore.
Do not use Union module as the subclass.
Do not use RootModel or __root__ of Pydantic features.
Return only code blocks.
"""
    
    if current_file:
        prompt += f"""
For the reference, here is the current Pydantic classes:

```python
{current_file}
```
"""
        
    # print(f"prompt: {prompt}")
    
    data = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 64000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def extract_python_code(response):
    """Extract Python code from the Anthropic API response"""
    # Get the text from the first content block
    content = response['content'][0]['text']
    
    # Extract code between Python code blocks
    code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
    
    if not code_blocks:
        # Try without language specifier
        code_blocks = re.findall(r'```\n(.*?)```', content, re.DOTALL)
    
    if not code_blocks:
        raise ValueError("No Python code blocks found in the response")
    
    # Join all code blocks - typically there should be just one
    return "\n\n".join(code_blocks)

def save_code(code, output_path):
    """Save the generated code to the output file"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    header = f"""
# This file is auto-generated based on {JSON_SCHEMA_URL} - do not modify manually.
"""

    code = header + code
    
    with open(output_path, 'w') as f:
        f.write(code)
    
    print(f"Schema generated at {output_path}")

def main():
    try:
        # Download the JSON schema
        schema = download_schema()
        
        # Call the Anthropic API
        response = call_anthropic_api(schema)
        
        # Extract the Python code
        code = extract_python_code(response)
        
        # Save the code
        save_code(code, OUTPUT_FILE)
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
