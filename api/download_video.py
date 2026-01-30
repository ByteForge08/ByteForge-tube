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
        
        # Limpar URL
        if "list=" in raw_url:
            match = re.search(r"v=([a-zA-Z0-9_-]{11})", raw_url)
            if match:
                video_url = f"https://www.youtube.com/watch?v={match.group(1)}"
            else:
                video_url = raw_url
        else:
            video_url = raw_url
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])
            
            # Encontrar melhor formato MP4
            video_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
            
            if video_formats:
                best = max(video_formats, key=lambda x: x.get('filesize', 0) or 0)
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': True,
                        'title': info.get('title'),
                        'url': best.get('url'),
                        'quality': best.get('format_note', 'N/A')
                    })
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Formato MP4 não encontrado'})
                }
                
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
