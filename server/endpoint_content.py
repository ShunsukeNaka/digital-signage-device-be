from .common import *
from .functions_times import get_now_str
from .functions_data_management import check_content_type, change_filename, allowed_file, create_square_thumbnail, get_content_path, check_content_type_forPath
from .functions_token import check_token, generate_onetime_token_id
from .static import CONTENTS_PATH, THUMBNAIL_PATH
from flask import current_app

bp = Blueprint("content", __name__)

@bp.route('/get', methods=['POST'])
def get_content_device():
    try:
        data = request.get_json()
        if not data or "token" not in data or "content" not in data or "id" not in data["content"]:
            return jsonify({"status": "error", "responded_at": get_now_str(), "message": "Invalid JSON"}), 400

        token_value = data.get("token")
        result = check_token(token_value, "device")
        if not isinstance(result, Token):
            return result  # エラー時はそのまま返す
        token_obj = result

        user_id = token_obj.user_id
        content_id = data["content"].get('id')

        # DataBaseからuserのデータを取得して照合
        print(user_id)
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return jsonify({"status": "error", "responded_at": get_now_str(), "message": "Not Found"}), 404

        file_path = get_content_path(content_id)
        if file_path is None:
            return jsonify({"status": "error", "responded_at": get_now_str(), "message": "Not Found File"}), 406

        # 新しいワンタイムトークン生成
        token_str = generate_onetime_token_id()
        token_uuid = uuid.UUID(token_str) if isinstance(token_str, str) else token_str

        one_time_token = OneTimeToken(
            id=token_uuid,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )

        db.session.add(one_time_token)
        db.session.commit()

        return jsonify({
            "status": "success",
            "responded_at": get_now_str(),
            "user": {"id": user_id},
            "content": {
                "id": content_id,
                "type": check_content_type_forPath(file_path),
                "url": f"https://be.fukunage.fukunova.jp/send_content/device?id={content_id}",
                "token": token_str
            }
        }), 200

    except Exception as e:
        current_app.logger.exception(e)
        db.session.rollback()
        return jsonify({
            "status": "error",
            "responded_at": get_now_str(),
            "message": "Message can't be shown"
        }), 500

