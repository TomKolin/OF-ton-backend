import os
import requests
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# ====== НАСТРОЙКА ЛОГИРОВАНИЯ ======
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====== НАСТРОЙКИ ======
BOT_TOKEN = "8696264655:AAGyn82KU7D1F9nKiBuQLcjQd2p2HHH1PEQ"
YOUR_WALLET = "UQA4aInFqReAIe9UrFhqu-CRzhpLAGwAZJKAEYMO_KIjK0ni"

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
ACCESS_LINK = "https://moicvetu.tilda.ws"   # ← СЮДА ВСТАВЬ СВОЮ ССЫЛКУ
# Если хочешь уникальную ссылку для каждого пользователя — читай ниже
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

MIN_VALUE_NANOTON = 100_000_000   # 0.1 TON
processed = set()

app = Flask(__name__)
CORS(app)


def send_access_link_via_telegram(chat_id, access_url):
    """Отправляет пользователю сообщение со ссылкой на сайт"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        caption = (
            "✅ Оплата успешно получена!\n\n"
            "🔥 Добро пожаловать в OnlyFans Analog 2026!\n\n"
            "Твоя личная ссылка для полного доступа:\n"
            f"👉 {access_url}\n\n"
            "Сохрани ссылку — она работает только для тебя.\n"
            "Приятного просмотра 🔥"
        )
        
        data = {
            'chat_id': chat_id,
            'text': caption,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }
        
        response = requests.post(url, data=data, timeout=20)
        result = response.json()
        
        if result.get('ok'):
            logger.info(f"✅ Ссылка отправлена пользователю {chat_id}")
            return True
        else:
            logger.error(f"Ошибка Telegram API: {result}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при отправке ссылки: {e}")
        return False


@app.route("/")
def home():
    return "✅ Backend работает (OnlyFans Analog mode)"


@app.route("/check_payment", methods=["POST"])
def check_payment():
    data = request.json
    comment = data.get("comment", "").strip()
   
    logger.info(f"🔍 Проверка платежа: {comment}")
   
    if not comment or "_" not in comment:
        return jsonify({"paid": False, "error": "Invalid comment"})
   
    try:
        # Получаем последние транзакции
        url = f"https://toncenter.com/api/v2/getTransactions?address={YOUR_WALLET}&limit=30"
        response = requests.get(url, timeout=15)
        tx_data = response.json()
        
        if "result" not in tx_data:
            return jsonify({"paid": False})
        
        for tx in tx_data["result"]:
            tx_hash = tx.get("transaction_id", {}).get("hash")
            if not tx_hash or tx_hash in processed:
                continue
                
            in_msg = tx.get("in_msg", {})
            value_nanoton = int(in_msg.get("value", 0))
            tx_comment = in_msg.get("message", "").strip()
            
            # Проверяем сумму и комментарий
            if value_nanoton >= MIN_VALUE_NANOTON and tx_comment == comment:
                try:
                    user_id = int(comment.split("_")[1])
                except (IndexError, ValueError):
                    logger.error(f"Не удалось извлечь user_id из комментария: {comment}")
                    continue
                
                # Отправляем ссылку
                success = send_access_link_via_telegram(user_id, ACCESS_LINK)
                
                if success:
                    processed.add(tx_hash)
                    logger.info(f"✅ Доступ отправлен пользователю {user_id} | TX: {tx_hash[:8]}...")
                    return jsonify({"paid": True})
                
    except Exception as e:
        logger.error(f"Ошибка при проверке платежа: {e}")
   
    return jsonify({"paid": False})


@app.route("/test", methods=["GET"])
def test():
    return jsonify({
        "status": "ok",
        "mode": "OnlyFans Analog (link mode)",
        "wallet": YOUR_WALLET
    })


# Для локального запуска
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
