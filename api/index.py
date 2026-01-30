import json
from datetime import datetime

def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'status': 'online',
            'service': 'ByteForgeYT API',
            'version': '2.0',
            'timestamp': datetime.now().isoformat(),
            'endpoints': {
                'GET /api/get_info': 'Informações do vídeo (POST com JSON)',
                'GET /api/download_video?url=URL': 'Download MP4',
                'GET /api/download_audio?url=URL': 'Download MP3'
            }
        })
    }