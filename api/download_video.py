import json
import re
import yt_dlp

def handler(event, context):
    try:
        # Parsear query string
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
        
        # Configurar yt-dlp para vídeo
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'http_chunk_size': 10485760,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Obter informações primeiro
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'video')
            
            # Gerar URL direta (não baixar no servidor)
            # O Vercel tem limite de 50MB para respostas, então retornamos a URL
            formats = info.get('formats', [])
            video_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('vcodec') != 'none']
            
            if video_formats:
                # Pegar a melhor qualidade
                best_format = max(video_formats, key=lambda x: x.get('filesize', 0) or x.get('quality', 0))
                direct_url = best_format.get('url')
                
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
                        'download_link': f'<a href="{direct_url}" download="{title}.mp4">Clique para baixar MP4</a>'
                    })
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Nenhum formato MP4 encontrado'})
                }
                
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }