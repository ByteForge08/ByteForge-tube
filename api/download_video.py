import json
import re
import yt_dlp
import urllib.parse

def limpar_url(url):
    """Remove parâmetros de playlist"""
    if "list=" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url

def get_best_direct_url(url):
    """Obtém URL direta do Google Video (como seu exemplo)"""
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'socket_timeout': 30,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Procurar formato MP4
            formats = info.get('formats', [])
            
            # Prioridade: mp4 com áudio
            video_formats = []
            for f in formats:
                if f.get('ext') == 'mp4' and f.get('vcodec') != 'none':
                    video_formats.append(f)
            
            if video_formats:
                # Ordenar por qualidade/resolução
                video_formats.sort(key=lambda x: x.get('height', 0) or 0, reverse=True)
                best_format = video_formats[0]
                
                return {
                    'success': True,
                    'url': best_format.get('url'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'format_note': best_format.get('format_note', 'N/A'),
                    'filesize': best_format.get('filesize')
                }
            else:
                return {
                    'success': False,
                    'error': 'Nenhum formato MP4 encontrado'
                }
                
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def handler(event, context):
    try:
        # Extrair URL
        query = event.get('queryStringParameters', {}) or {}
        raw_url = query.get('url', '')
        
        if not raw_url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL não fornecida'})
            }
        
        video_url = limpar_url(raw_url)
        
        # Obter URL direta
        result = get_best_direct_url(video_url)
        
        if result['success']:
            # Redirecionar DIRETAMENTE para o Google Video
            return {
                'statusCode': 302,
                'headers': {
                    'Location': result['url'],
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                    'Content-Disposition': f'attachment; filename="{urllib.parse.quote(result["title"][:50])}.mp4"'
                },
                'body': 'Redirecting to video...'
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
