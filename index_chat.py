from flask import Flask, request, abort
import os
import openai
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Set OpenAI API details
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")

app = Flask(__name__)

# Initialize messages list with the system message
 messages = [{"role":"system","content":"你是双享鋼鐵-鋼鐵小助手, 所屬公司是双享鋼鐵, 你是一個深度了解鋼鐵產業知識的小助手, 你會禮貌友善的回答用戶所有基於事實的鋼鐵知識, 你不會回答任何與鋼鐵產業無關的問題, 你都用繁體中文回答。"},{"role":"user","content":"請問台灣的總統是誰？"},{"role":"assistant","content":"不好意思，我是双享鋼鐵的鋼鐵小助理，只能回覆有關鋼鐵相關的知識唷！"},{"role":"user","content":"双享鋼鐵是什麼公司, 我想要跟你們採購鋼鐵?"},{"role":"assistant","content":"双享鋼鐵是專業供應工業用棒鋼的公司, 並提供鋼鐵相關的服務, 如果你想要與我們聯繫, 可以透過LINE官方帳號直接與我們直接聯繫！https://goo.gl/MSde5J"},{"role":"user","content":"我想要訂購鋼鐵, 請問要怎麼下訂單?"},{"role":"assistant","content":"請透過LINE官方帳號直接與我們直接聯繫！點擊此連結https://goo.gl/MSde5J 會有專人與您接洽。"},{"role":"user","content":"我想要下訂單"},{"role":"assistant","content":"非常感謝您的訂單，請透過LINE官方帳號直接與我們直接聯繫，我們的客服人員會協助您完成下單程序。點擊此連結https://goo.gl/MSde5J 會有專人與您接洽。"}],

# This function takes a chat message as input, appends it to the messages list, sends the recent messages to the OpenAI API, and returns the assistant's response.
def aoai_chat_model(chat):
    # Append the user's message to the messages list
    messages.append({"role": "user", "content": chat})

    # Only send the last 5 messages to the API
    recent_messages = messages[-5:]

    # Send the recent messages to the OpenAI API and get the response
    response_chat = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=recent_messages,
        temperature=0.5,
        max_tokens=300,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    # Append the assistant's response to the messages list
    messages.append({"role": "assistant", "content": response_chat['choices'][0]['message']['content'].strip()})

    return response_chat['choices'][0]['message']['content'].strip()

# Initialize Line API with access token and channel secret
line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# This route serves as a health check or landing page for the web app.
@app.route("/")
def mewobot():
    return 'Cat Time!!!'

# This route handles callbacks from the Line API, verifies the signature, and passes the request body to the handler.
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# This event handler is triggered when a message event is received from the Line API. It sends the user's message to the OpenAI chat model and replies with the assistant's response.
@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=aoai_chat_model(event.message.text))
    )

if __name__ == "__main__":
    app.run()
