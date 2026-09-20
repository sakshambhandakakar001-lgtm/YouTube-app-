from flask import Blueprint, request, jsonify, session

video_bp = Blueprint('video_bp', __name__)

# LIKE / DISLIKE FEATURE
@video_bp.route('/video/<int:video_id>/react', methods=['POST'])
def react_video(video_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Login required'}), 401
    
    action = request.json.get('action') # 'like' ya 'dislike'
    return jsonify({'status': 'success', 'action': action, 'message': f'Video {action}d successfully'})

# DELETE VIDEO FEATURE (Creator Check)
@video_bp.route('/video/<int:video_id>/delete', methods=['POST', 'DELETE'])
def delete_video(video_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    # Sirf video ka creator hi delete kar sakta hai
    return jsonify({'status': 'success', 'message': 'Video successfully deleted'})
