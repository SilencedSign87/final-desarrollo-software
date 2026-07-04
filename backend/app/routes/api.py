from flask_openapi3 import APIBlueprint

api_bp = APIBlueprint('api', __name__)

@api_bp.get('/health')
def health():
    """Health check de la API"""
    return {'status': 'ok'}