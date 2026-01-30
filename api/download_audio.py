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
        
        # Configurar yt-dlp para áudio
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'audio')
            
            # Encontrar formato de áudio
            formats = info.get('formats', [])
            audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            
            if audio_formats:
                best_audio = max(audio_formats, key=lambda x: x.get('filesize', 0) or x.get('abr', 0))
                direct_url = best_audio.get('url')
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    },
                    'body': json.dumps({
                        'success': True,
                        'title': title,
                        'direct_url': direct_url,
                        'message': 'Use o link direto abaixo para baixar',
                        'download_link': f'<a href="{direct_url}" download="{title}.mp3">Clique para baixar MP3</a>'
                    })
                }
            else:
                # Fallback para extrair áudio de formato combinado
                ydl_opts_extract = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'extract_audio': True,
                    'audio_format': 'mp3',
                }
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'success': True,
                        'title': title,
                        'message': 'Áudio precisa de conversão. Use serviço externo.',
                        'external_service': f'https://onlinevideoconverter.pro/pt/youtube-converter?v={info.get("id")}&t=mp3'
                    })
                }
                
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }