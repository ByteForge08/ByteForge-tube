import json
import re
import yt_dlp

def handler(event, context):
    try:
        query = event.get('queryStringParameters', {}) or {}
        raw_url = query.get('url', '')
        
        if not raw_url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL não fornecida'})
            }
        
        if "list=" in raw_url:
            match = re.search(r"v=([a-zA-Z0-9_-]{11})", raw_url)
            if match:
                video_url = f"https://www.youtube.com/watch?v={match.group(1)}"
            else:
                video_url = raw_url
        else:
            video_url = raw_url
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if audio_formats:
                best = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': True,
                        'title': info.get('title'),
                        'url': best.get('url'),
                        'bitrate': f"{best.get('abr', 0)}kbps"
                    })
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Formato de áudio não encontrado'})
                }
                
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
