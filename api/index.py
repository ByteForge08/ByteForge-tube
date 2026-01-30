import json
from datetime import datetime

def handler(event, context):
    """Health check simples"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'status': 'online',
            'service': 'ByteForgeYT',
            'timestamp': datetime.now().isoformat(),
            'endpoints': {
                'GET /api/health': 'Esta página',
                'POST /api/get_info': 'Informações do vídeo (JSON com {"url": "..."})',
                'GET /download/video?url=URL': 'Download MP4',
                'GET /download/audio?url=URL': 'Download MP3'
            }
        })
    }
