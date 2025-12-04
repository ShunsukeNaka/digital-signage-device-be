from .common import *
from .functions_times import get_now_str
from .functions_token import check_token
from .functions_data_management import get_content_path, check_content_type_forPath_ext
from .functions_check_update import update_device_true
from .static import UPDATE_INDEX_CONTENT_SET

bp = Blueprint("device", __name__)

@bp.route('/setting/get', methods=['POST'])
def device_content_get_device():
    try:
        data = request.get_json()
        token = data.get("token")

        if not token:
            return jsonify({"status": "error", "responded_at": get_now_str(), "message": "Invalid JSON"}), 400           

        # トークンチェック
        result = check_token(token, "device")
        if not isinstance(result, Token):
            return result
        checked_token = result

        device_id = checked_token.device_id

        # デバイス取得
        device = Device.query.filter_by(user_id=checked_token.user_id, id=device_id).first()
        if not device:
            return jsonify({"error": "Device not found", "responded_at": get_now_str()}), 404

        # 設定取得（ORM）
        device_setting = DeviceSetting.query.filter_by(device_id=device_id).first()


        if device_setting and device_setting.settings:
            settings = device_setting.settings  # dict
            contents = settings.get("contents", [])

        # contents の各要素に ext を追加
        for content in contents:
            content_id = content.get("id")
            if content_id:
                path = get_content_path(content_id)
                if path is None:
                    return jsonify({"error": "File not found", "responded_at": get_now_str()}), 404
                ext = check_content_type_forPath_ext(path)
                content["ext"] = ext

        if not device_setting:
            return jsonify({
                "status": "no_settings",
                "responded_at": get_now_str(),
                "device": device.id,
                "settings": None
            }), 200

        return jsonify({
            "status": "success",
            "responded_at": get_now_str(),
            "device": device.id,
            "settings": {
                "type": device_setting.settings.get("type"),
                "created_at": device_setting.created_at,
                "contents":contents # device_setting.settings  # JSONBはdictとして返る
            }
        }), 200

    except Exception as e:
        bp.logger.info(e)
        return jsonify({
            "status": "error",
            "responded_at": get_now_str(),
            "message": f'message: {e}'
        }), 500
