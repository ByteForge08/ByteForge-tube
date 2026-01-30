import json
import re
import yt_dlp
import urllib.parse

def limpar_url(url):
    if "list=" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url

def get_best_audio_url(url):
    """Obtém URL direta de áudio"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'socket_timeout': 30,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Procurar formato de áudio
            formats = info.get('formats', [])
            
            # Filtrar áudio puro (sem vídeo)
            audio_formats = []
            for f in formats:
                if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                    audio_formats.append(f)
            
            if audio_formats:
                # Ordenar por bitrate
                audio_formats.sort(key=lambda x: x.get('abr', 0) or 0, reverse=True)
                best_audio = audio_formats[0]
                
                return {
                    'success': True,
                    'url': best_audio.get('url'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'abr': best_audio.get('abr', 'N/A'),
                    'ext': best_audio.get('ext', 'm4a')
                }
            else:
                # Fallback para qualquer formato com áudio
                for f in formats:
                    if f.get('acodec') != 'none':
                        return {
                            'success': True,
                            'url': f.get('url'),
                            'title': info.get('title'),
                            'duration': info.get('duration'),
                            'abr': f.get('abr', 'N/A'),
                            'ext': f.get('ext', 'mp4')
                        }
                
                return {
                    'success': False,
                    'error': 'Nenhum formato de áudio encontrado'
                }
                
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

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
        
        video_url = limpar_url(raw_url)
        
        result = get_best_audio_url(video_url)
        
        if result['success']:
            # Redirecionar para áudio direto
            return {
                'statusCode': 302,
                'headers': {
                    'Location': result['url'],
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Content-Disposition': f'attachment; filename="{urllib.parse.quote(result["title"][:50])}.{result["ext"]}"'
                },
                'body': 'Redirecting to audio...'
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': result['error']})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }
