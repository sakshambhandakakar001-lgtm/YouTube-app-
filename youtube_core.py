from flask import Blueprint, jsonify, request, session, render_template_string
import time

youtube_bp = Blueprint('youtube_core', __name__)

# Dummy Data Stores (Database Models/State)
VIDEOS_DB = [
    {
        "id": 1,
        "title": "Song",
        "category": "Music",
        "creator": "Saksham",
        "creator_id": 101,
        "views": "1.2K",
        "likes": 120,
        "dislikes": 5,
        "is_short": False,
        "url": "/static/videos/sample.mp4",
        "summary": "Master video stream optimized with HDR pipeline and auto volume compressor."
    },
    {
        "id": 2,
        "title": "Minecraft Trap Challenge #Shorts",
        "category": "Gaming",
        "creator": "MOG_BOY_",
        "creator_id": 102,
        "views": "15K",
        "likes": 2400,
        "dislikes": 30,
        "is_short": True,
        "url": "/static/videos/short_sample.mp4",
        "summary": "Epic Minecraft short video challenge."
    }
]

COMMENTS_DB = {
    1: [{"user": "Viewer1", "text": "Awesome quality!", "time": "2 hours ago"}]
}

SUBSCRIPTIONS_DB = set()

# --- ROUTES ---

@youtube_bp.route('/api/shorts', methods=['GET'])
def get_shorts():
    shorts = [v for v in VIDEOS_DB if v.get("is_short")]
    return jsonify({"status": "success", "shorts": shorts if shorts else VIDEOS_DB})

@youtube_bp.route('/api/video/<int:video_id>/like', methods=['POST'])
def like_video(video_id):
    for v in VIDEOS_DB:
        if v["id"] == video_id:
            v["likes"] += 1
            return jsonify({"status": "success", "likes": v["likes"], "message": "Liked!"})
    return jsonify({"status": "error", "message": "Video not found"}), 404

@youtube_bp.route('/api/video/<int:video_id>/subscribe', methods=['POST'])
def subscribe_channel(video_id):
    for v in VIDEOS_DB:
        if v["id"] == video_id:
            creator = v["creator"]
            if creator in SUBSCRIPTIONS_DB:
                SUBSCRIPTIONS_DB.remove(creator)
                return jsonify({"status": "success", "subscribed": False, "message": f"Unsubscribed from {creator}"})
            else:
                SUBSCRIPTIONS_DB.add(creator)
                return jsonify({"status": "success", "subscribed": True, "message": f"Subscribed to {creator}!"})
    return jsonify({"status": "error", "message": "Channel not found"}), 404

@youtube_bp.route('/api/video/<int:video_id>/comments', methods=['GET', 'POST'])
def handle_comments(video_id):
    if request.method == 'POST':
        data = request.get_json() or {}
        comment_text = data.get('comment', '').strip()
        if not comment_text:
            return jsonify({"status": "error", "message": "Empty comment"}), 400
        
        new_comment = {
            "user": session.get('username', 'Guest User'),
            "text": comment_text,
            "time": "Just now"
        }
        COMMENTS_DB.setdefault(video_id, []).append(new_comment)
        return jsonify({"status": "success", "comment": new_comment})
    
    return jsonify({"status": "success", "comments": COMMENTS_DB.get(video_id, [])})

@youtube_bp.route('/api/analytics', methods=['GET'])
def get_analytics():
    return jsonify({
        "status": "success",
        "analytics": {
            "balance": "$4,200.50",
            "subscribers": "1,250",
            "total_views": "48.5K",
            "watch_time_hours": "1,320"
        }
    })
