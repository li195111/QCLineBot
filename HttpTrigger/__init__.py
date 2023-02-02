import os
import logging

import azure.functions as func

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import ImageSendMessage, MessageEvent, TextSendMessage, StickerSendMessage


def main(req: func.HttpRequest) -> func.HttpResponse:
  logging.info('Python HTTP trigger function processed a request.')
  line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
  webhook: WebhookParser = WebhookParser(os.environ.get('LINE_CHANNEL_SECRET'))

  if req.method == 'POST':
    try:
      signature = req.headers.get('X-LINE-SIGNATURE', '')
      body = req.get_body().decode('utf-8')
      events = webhook.parse(body, signature)
    except InvalidSignatureError:
      logging.warning(f'Invalid Signature Error: {signature}')
      return func.HttpResponse(
          "{'success': False,'msg': 'Invalid Signature Error'}",
          status_code=500)
    except LineBotApiError:
      logging.warning('Line Bot Api Error')
      return func.HttpResponse(
          "{'success': False,'msg': 'Line Bot Api Error'}", status_code=500)
    except Exception as err:
      logging.warning(f'Error - {err}')
      return func.HttpResponse(f'success: False, msg: Error - {err}',
                               status_code=500)
    for event in events:
      if isinstance(event, MessageEvent):
        logging.info(f'Received Msg - {event.message.text}, {event.__dict__}')
        if event.message.type == 'text':
          line_bot_api.reply_message(event.reply_token,
                                     TextSendMessage(text=event.message.text))
        elif event.message.type == 'sticker':
          line_bot_api.reply_message(
              event.reply_token,
              StickerSendMessage(package_id=event.message.packageId,
                                 sticker_id=event.message.stickerId))
    return func.HttpResponse("{'success': True}")
  else:
    logging.warning(f'Invalid Method')
    return func.HttpResponse("{'success': False,'msg': 'Invalid Method'}",
                             status_code=500)
