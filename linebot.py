import os

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import ImageSendMessage, MessageEvent, TextSendMessage

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
webhook: WebhookParser = WebhookParser(os.environ.get('LINE_CHANNEL_SECRET'))


def callback(request):
  if request.method == 'POST':
    signature = request.META['HTTP_X_LINE_SIGNATURE']
    body = request.body.decode('utf-8')

    try:
      events = webhook.parse(body, signature)
    except InvalidSignatureError:
      return {'state': False}
    except LineBotApiError:
      return {'state': False}
    for event in events:
      if isinstance(event, MessageEvent):
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=event.message.text))
    return {'state': True}
  else:
    return {'state': False}