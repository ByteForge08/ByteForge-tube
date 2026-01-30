import json
import yt_dlp

def handler(event, context):
    try:
        print("DEBUG: get_info.py chamado")
        
        # Parse seguro
        query = event.get('queryStringParameters', {}) or {}
        url = query.get('url', '')
        
        # Se não tiver na query, tenta no body
        if not url and event.get('body'):
            try:
                body = json.loads(event.get('body'))
                url = body.get('url', '')
            except:
                pass
        
        if not url:
            return {
                'statusCode': 200,  # 200 em vez de 400 para teste
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': 'URL não fornecida',
                    'debug': 'Forneça ?url=... na URL'
                })
            }
        
        # Config simples
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': True,
                    'title': info.get('title', 'Sem título'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration_string', ''),
                    'video_id': info.get('id', ''),
                    'url': url
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 200,  # 200 para evitar erro no frontend
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Use os botões de download diretamente'
            })
        }
