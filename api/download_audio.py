import json
import re

def extract_video_id(url):
    if not url:
        return None
    
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def handler(event, context):
    try:
        query_params = {}
        
        if isinstance(event, dict):
            query_params = event.get('queryStringParameters', {}) or {}
        
        raw_url = query_params.get('url', '')
        
        if not raw_url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL não fornecida'})
            }
        
        video_id = extract_video_id(raw_url)
        
        if not video_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL do YouTube inválida'})
            }
        
        # Redirecionar para serviço externo
        return {
            'statusCode': 302,
            'headers': {
                'Location': f'https://loader.to/api/button/?url=https://youtube.com/watch?v={video_id}&f=mp3&color=ff0000',
                'Access-Control-Allow-Origin': '*'
            },
            'body': 'Redirecting...'
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
