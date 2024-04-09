#Retainnig this file beacuse... 
import json

def format_json_string(data_string):
    try:
        # Try to parse the string as JSON
        data = json.loads(data_string)
        # If successful, convert the Python object back to a formatted JSON string
        formatted_data = json.dumps(data, indent=4)
    except json.JSONDecodeError:
        # If the string is not valid JSON, format it as a JSON-like string
        lines = data_string.split(', ')
        formatted_lines = ['\t' + line for line in lines]
        formatted_data = '{\n' + ',\n'.join(formatted_lines) + '\n}'
    
    return formatted_data