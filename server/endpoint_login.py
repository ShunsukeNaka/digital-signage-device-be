from .common import *
from .functions_times import UtcGmt2JST, get_now_str
from .functions_token import add_token

bp = Blueprint("login", __name__)

@bp.route('/', methods=['POST'])
def login_device():
    try:
        if request.method == 'POST':
            data = request.get_json()

            if not data or "user" not in data or "id" not in data["user"] or "pass" not in data["user"] or "id" not in data["device"]:
                return jsonify({"status": "error", "responded_at": get_now_str(), "message": "Invalid JSON"}), 400           

            user_id = data["user"].get("id")
            user_password = data["user"].get("pass")
            device_id = data["device"].get("id")

            # DataBaseからuserのデータを取得して照合
            user = User.query.filter_by(id=user_id).first()
            if user is None:
                return jsonify({"status": "error", "responded_at": get_now_str(), "message": "Unauthorized"}), 401
            if not check_password_hash(user.password, user_password):
                return jsonify({"status": "error", "responded_at": get_now_str(), "message": "Unauthorized"}), 401

            # DataBaseからDeviceのデータを取得して照合
            device = Device.query.filter_by(id=device_id, user_id=user_id).first()
            if device is None:
                return jsonify({"status": "error", "responded_at": get_now_str(), "message": f"Not Found"}), 404
            
            token = add_token(user_id, device_id, "device")
            send_token = token.token
            if token == None:
                send_token = "NO_GENERATE_TOKEN"

            return jsonify({
                "status": "success",
                "responded_at": get_now_str(),
                "user": {
                    "id": user_id,
                    "name": user.name
                },
                "device": {
                    "id": device_id,
                    "name": device.name
                },
                "token": send_token
            }), 200
    except Exception as e:
        print(e)
        return jsonify({
            "status": "error", "responded_at": get_now_str(),
            "message": 'Message is can`t showing'
        }), 500
