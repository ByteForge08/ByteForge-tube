import json
import re
import yt_dlp

def limpar_url(url):
    if not url:
        return ""
    if "list=" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url

def parse_body(body):
    """Parse body seguro para evitar erros JSON"""
    if not body:
        return {}
    
    # Se for string, tenta parsear como JSON
    if isinstance(body, str):
        try:
            return json.loads(body)
        except:
            # Se falhar, tenta extrair URL de query string
            if 'url=' in body:
                from urllib.parse import parse_qs
                parsed = parse_qs(body)
                return {'url': parsed.get('url', [''])[0]}
            return {}
    
    # Se já for dict, retorna
    elif isinstance(body, dict):
        return body
    
    return {}

def handler(event, context):
    try:
        # Verificar se é um evento Vercel
        if isinstance(event, dict) and 'body' in event:
            # Parse body seguro
            body_data = parse_body(event.get('body'))
            
            # Tentar pegar URL do body ou query string
            raw_url = body_data.get('url') or event.get('queryStringParameters', {}).get('url', '')
        else:
            # Formato antigo ou direto
            raw_url = ''
            if isinstance(event, dict):
                raw_url = event.get('url', '')
            elif isinstance(event, str) and 'url=' in event:
                from urllib.parse import parse_qs
                parsed = parse_qs(event)
                raw_url = parsed.get('url', [''])[0]
        
        video_url = limpar_url(raw_url)
        
        if not video_url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL inválida', 'received': raw_url[:50] if raw_url else 'empty'})
            }

        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            'extract_flat': False,
            'socket_timeout': 30,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            url_video = info.get('url')
            if not url_video and info.get('formats'):
                url_video = info.get('formats')[-1].get('url')
            
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('vcodec') == 'none']
            
            if audio_formats:
                url_audio = audio_formats[-1].get('url')
            else:
                url_audio = url_video

            response = {
                'success': True,
                'title': info.get('title'),
                'thumbnail': info.get('thumbnail'),
                'url_video': url_video,
                'url_audio': url_audio,
                'duration': info.get('duration_string'),
                'video_id': info.get('id')
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
                },
                'body': json.dumps(response)
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR: {str(e)}")
        print(f"TRACEBACK: {error_details}")
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Erro interno',
                'details': str(e),
                'type': type(e).__name__
            })
        }
