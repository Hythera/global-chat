import os
import requests

api_url = os.getenv('API_URL')
api_key = os.getenv('API_KEY')
server_id = os.getenv('SERVER_ID')


headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}


restart_endpoint = f'{api_url}/servers/{server_id}/power'

payload = {
    'signal': 'restart'
}

response = requests.post(restart_endpoint, json=payload, headers=headers)