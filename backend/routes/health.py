from flask import Blueprint, jsonify
from datetime import datetime
import psutil
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        from models import db
        
        # Check database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    # Check system resources
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': os.environ.get('APP_VERSION', '1.0.0'),
        'checks': {
            'database': db_status,
            'memory_usage': f"{memory.percent}%",
            'disk_usage': f"{disk.percent}%"
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

@health_bp.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    try:
        from prometheus_client import generate_latest, CollectorRegistry, Counter, Histogram, Gauge
        
        # Create custom registry
        registry = CollectorRegistry()
        
        # Add some basic metrics
        request_count = Counter('app_requests_total', 'Total requests', registry=registry)
        memory_usage = Gauge('app_memory_usage_bytes', 'Memory usage in bytes', registry=registry)
        
        # Update metrics
        memory = psutil.virtual_memory()
        memory_usage.set(memory.used)
        
        # Generate Prometheus format
        metrics_output = generate_latest(registry)
        
        return metrics_output, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except ImportError:
        return jsonify({'error': 'Metrics not available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    """Readiness check for Kubernetes"""
    try:
        from models import db
        
        # Check if application is ready to serve requests
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'not ready',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@health_bp.route('/live', methods=['GET'])
def liveness_check():
    """Liveness check for Kubernetes"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
