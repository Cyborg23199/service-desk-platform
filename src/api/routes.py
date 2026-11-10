from flask import request, jsonify
from api import api_bp
from models import db, User, Incident, Comment

# --- USERS ENDPOINTS ---
@api_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get all users
    ---
    responses:
      200:
        description: List of all registered users
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@api_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
          properties:
            name:
              type: string
            email:
              type: string
    responses:
      201:
        description: User created successfully
      400:
        description: Invalid input
      409:
        description: Email already registered
    """
    data = request.get_json() or {}
    if not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email are required'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


# --- INCIDENTS ENDPOINTS ---
@api_bp.route('/incidents', methods=['GET'])
def get_incidents():
    """
    Get all incidents
    ---
    responses:
      200:
        description: List of all incidents
    """
    incidents = Incident.query.all()
    return jsonify([inc.to_dict() for inc in incidents]), 200

@api_bp.route('/incidents/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    """
    Get incident by ID
    ---
    parameters:
      - name: incident_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Incident details
      404:
        description: Incident not found
    """
    incident = Incident.query.get_or_404(incident_id)
    return jsonify(incident.to_dict()), 200

@api_bp.route('/incidents', methods=['POST'])
def create_incident():
    """
    Create a new incident
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - description
          properties:
            title:
              type: string
            description:
              type: string
            priority:
              type: string
              default: MEDIUM
            status:
              type: string
              default: OPEN
    responses:
      201:
        description: Incident created successfully
      400:
        description: Missing required fields
    """
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
    """
    Update an existing incident
    ---
    parameters:
      - name: incident_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            priority:
              type: string
            status:
              type: string
    responses:
      200:
        description: Incident updated successfully
      404:
        description: Incident not found
    """
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
    """
    Delete an incident
    ---
    parameters:
      - name: incident_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Incident deleted successfully
      404:
        description: Incident not found
    """
    incident = Incident.query.get_or_404(incident_id)
    db.session.delete(incident)
    db.session.commit()
    return jsonify({'message': f'Incident {incident_id} deleted successfully'}), 200


# --- COMMENTS ENDPOINTS ---
@api_bp.route('/incidents/<int:incident_id>/comments', methods=['GET'])
def get_comments(incident_id):
    """
    Get comments for a specific incident
    ---
    parameters:
      - name: incident_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of comments for the incident
      404:
        description: Incident not found
    """
    Incident.query.get_or_404(incident_id)
    comments = Comment.query.filter_by(incident_id=incident_id).all()
    return jsonify([c.to_dict() for c in comments]), 200

@api_bp.route('/incidents/<int:incident_id>/comments', methods=['POST'])
def add_comment(incident_id):
    """
    Add a comment to an incident
    ---
    parameters:
      - name: incident_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - comment
          properties:
            user_id:
              type: integer
            comment:
              type: string
    responses:
      201:
        description: Comment added successfully
      400:
        description: Missing required fields
      404:
        description: Incident or user not found
    """
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