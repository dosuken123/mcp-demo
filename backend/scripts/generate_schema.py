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
ANTHROPIC_MODEL = "claude-3-7-sonnet-20250219"
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

Convert this JSON schema into pydantic models for the schema.py file.
Copy descriptions of the JSON schema to the pydantic models as docstrings.
If the field `type` is `object`, all keys must be defined as fields of an Pydantic Model.
If the field `type` is not `object` or undefined, define a type alias instead of using BaseModel.
If `enum` keyword is used with string values, use StrEnum from enum module.
If `const` keyword is used, set it as the default value of the field.
Use `Field` of pydantic feature as much as possible. If the field name starts with underscore, do not use `Field` class.
Do not omit for brevity.
Do not add docsstrings or comments that does not exist in the JSON schema.
Do not use `Union` as the subclass.
Do not use `RootModel` or `__root__` of pydantic features.
Return only code blocks.
"""
    
    if current_file:
        prompt += f"""
For the reference, here is the current schema.py file:

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
        ],
        "thinking": {
            "type": "enabled",
            "budget_tokens": 30000
        }
    }
    
    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def extract_python_code(response):
    """Extract Python code from the Anthropic API response"""
    # print("response", response['content'])
    text_block = [content for content in response['content'] if content.get('type')=='text'][0]
    # Get the text from the first content block
    content = text_block['text']
    
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

    header = f"""# This file is auto-generated based on {JSON_SCHEMA_URL} - do not modify manually.

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
