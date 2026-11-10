from flask import request, jsonify
from api import api_bp
from models import db, User, Incident, Comment

# --- USERS ENDPOINTS ---
@api_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

# --- INCIDENTS ENDPOINTS ---
@api_bp.route('/incidents', methods=['GET'])
def get_incidents():
    incidents = Incident.query.all()
    return jsonify([inc.to_dict() for inc in incidents]), 200

@api_bp.route('/incidents/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    return jsonify(incident.to_dict()), 200

@api_bp.route('/incidents', methods=['POST'])
def create_incident():
    data = request.get_json() or {}
    if not data.get('title') or not data.get('description'):
        return jsonify({'error': 'Title and description are required'}), 400

    incident = Incident(
        title=data['title'],
        description=data['description'],
        priority=data.get('priority', 'MEDIUM'),
        status=data.get('status', 'OPEN')
    )
    db.session.add(incident)
    db.session.commit()
    return jsonify(incident.to_dict()), 201

@api_bp.route('/incidents/<int:incident_id>', methods=['PUT'])
def update_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    data = request.get_json() or {}

    if 'title' in data:
        incident.title = data['title']
    if 'description' in data:
        incident.description = data['description']
    if 'priority' in data:
        incident.priority = data['priority']
    if 'status' in data:
        incident.status = data['status']

    db.session.commit()
    return jsonify(incident.to_dict()), 200

@api_bp.route('/incidents/<int:incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    incident = Incident.query.get_or_404(incident_id)
    db.session.delete(incident)
    db.session.commit()
    return jsonify({'message': f'Incident {incident_id} deleted successfully'}), 200

# --- COMMENTS ENDPOINTS ---
@api_bp.route('/incidents/<int:incident_id>/comments', methods=['GET'])
def get_comments(incident_id):
    Incident.query.get_or_404(incident_id)
    comments = Comment.query.filter_by(incident_id=incident_id).all()
    return jsonify([c.to_dict() for c in comments]), 200

@api_bp.route('/incidents/<int:incident_id>/comments', methods=['POST'])
def add_comment(incident_id):
    Incident.query.get_or_404(incident_id)
    data = request.get_json() or {}
    
    if not data.get('user_id') or not data.get('comment'):
        return jsonify({'error': 'user_id and comment content are required'}), 400
        
    User.query.get_or_404(data['user_id'])

    comment = Comment(
        incident_id=incident_id,
        user_id=data['user_id'],
        comment=data['comment']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201