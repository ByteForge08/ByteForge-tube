import json
import re
import yt_dlp

def limpar_url(url):
    if "list=" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url

def handler(event, context):
    try:
        # Parse request
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event.get('body'))
            except:
                pass
        
        raw_url = body.get('url', '') or event.get('queryStringParameters', {}).get('url', '')
        video_url = limpar_url(raw_url)
        
        if not video_url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL inválida'})
            }

        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            'extract_flat': False,
            'socket_timeout': 30,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            url_video = info.get('url') or (info.get('formats')[-1].get('url') if info.get('formats') else None)

            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('vcodec') == 'none']
            
            if audio_formats:
                url_audio = audio_formats[-1].get('url')
            else:
                url_audio = url_video

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'title': info.get('title'),
                    'thumbnail': info.get('thumbnail'),
                    'url_video': url_video,
                    'url_audio': url_audio,
                    'duration': info.get('duration_string'),
                    'video_id': info.get('id')
                })
            }
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
