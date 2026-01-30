import json
import re
import yt_dlp

def limpar_url(url):
    """Remove parâmetros de playlist para evitar travamentos"""
    if not url:
        return ""
    if "list=" in url:
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    return url

def handler(event, context):
    try:
        # Parsear requisição
        body = json.loads(event.get('body', '{}')) if event.get('body') else {}
        raw_url = body.get('url', '')
        video_url = limpar_url(raw_url)
        
        if not video_url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL inválida'})
            }

        # Configurações do yt-dlp (igual ao seu)
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            'extract_flat': False,
            'socket_timeout': 30,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Encontrar URL do vídeo
            url_video = info.get('url')
            if not url_video and info.get('formats'):
                # Pegar o último formato (geralmente melhor qualidade)
                url_video = info.get('formats')[-1].get('url')
            
            # Encontrar URL do áudio
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('vcodec') == 'none']
            
            if audio_formats:
                url_audio = audio_formats[-1].get('url')
            else:
                url_audio = url_video  # Fallback

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
                    'duration_seconds': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count')
                })
            }
            
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Erro ao analisar vídeo.', 'details': str(e)})
        }