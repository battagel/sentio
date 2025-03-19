"""
API for Sentio
"""

from prometheus_client import make_wsgi_app

from .prediction import PredictionService

def router(environ, start_fn):
    """
    Route the incoming request to a specific WSGI page
    """
    match environ['PATH_INFO']:
        case "/metrics":
            metrics_app = make_wsgi_app()
            prediction_service = PredictionService.get_instance()
            prediction_service.update_metrics()
            return metrics_app(environ, start_fn)
        case "/author":
            start_fn('200 OK', [])
            return [b'Lovingly built by Matthew Battagel\n']
        case _:
            start_fn('200 OK', [])
            return [b'Sentio Server v0.01\n']
