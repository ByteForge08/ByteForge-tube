import json

def handler(event, context):
    try:
        query = event.get('queryStringParameters', {}) or {}
        url = query.get('url', '')
        
        if not url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL não fornecida'})
            }
        
        video_id = 'demo'
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
        elif 'v=' in url:
            video_id = url.split('v=')[1].split('&')[0]
        
        redirect_url = f"https://onlinevideoconverter.pro/pt/youtube-converter?v={video_id}&t=mp3"
        
        return {
            'statusCode': 302,
            'headers': {
                'Location': redirect_url,
                'Cache-Control': 'no-cache'
            },
            'body': 'Redirecting...'
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
