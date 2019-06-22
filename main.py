from model_manager import StyleTransferManager
from telegram_token import token
import numpy as np
from PIL import Image
from io import BytesIO

# В бейзлайне пример того, как мы можем обрабатывать две картинки, пришедшие от пользователя.
# При реалиазации первого алгоритма это Вам не понадобится, так что можете убрать загрузку второй картинки.
# Если решите делать модель, переносящую любой стиль, то просто вернете код)

modelManager = StyleTransferManager()
first_image_file = {}


def process_image(chat_id, bot, image_info):
    try:
        image_file = bot.get_file(image_info)
    except Exception as exception:
        print(exception.__str__())
        bot.sendMessage(chat_id, text="К сожалению связь прервалась... Пришли картинку еще раз")
        return

    if chat_id in first_image_file:
        try:
            # первая картинка, которая к нам пришла станет content image, а вторая style image
            content_image_stream = BytesIO()
            first_image_file[chat_id].download(out=content_image_stream)
            del first_image_file[chat_id]

            style_image_stream = BytesIO()
            image_file.download(out=style_image_stream)
            bot.sendMessage(chat_id, text="Я получил обе картинки и сейчас займусь их обработкой. Это может занять до 10 минут. Когда все будет готово, я пришлю стилизованную картинку.")
            output = modelManager.simple_transfer_style(content_image_stream, style_image_stream)

            # теперь отправим назад фото
            output_stream = BytesIO()
            output.save(output_stream, format='PNG')
            output_stream.seek(0)
            bot.sendMessage(chat_id, text="А вот и долгожданный результат!")
            bot.send_photo(chat_id, photo=output_stream)
            bot.sendMessage(chat_id, text="Ну как? Нравиться? Присылай еще картинки!")
            print("Sent Photo to user")
        except Exception as exception:
            print(exception.__str__())
            bot.sendMessage(chat_id, text="Упс... что-то пошло не так. Давай начнем сначала.")
            return
    else:
        first_image_file[chat_id] = image_file
        bot.sendMessage(chat_id, text="Я получил картинку для применения стиля. Пришли вторую картинку со стилем, который надо применить к первой картинке")


def send_prediction_on_photo(bot, update):
    # Нам нужно получить две картинки, чтобы произвести перенос стиля, но каждая картинка приходит в
    # отдельном апдейте, поэтому в простейшем случае мы будем сохранять id первой картинки в память,
    # чтобы, когда уже придет вторая, мы могли загрузить в память уже сами картинки и обработать их.
    chat_id = update.message.chat_id
    print("Got image from {}".format(chat_id))

    # получаем информацию о картинке
    if len(update.message.photo) >= 1:
        image_info = update.message.photo[-1]
        process_image(chat_id, bot, image_info)
    else:
        bot.sendMessage(chat_id, text="Прилите картинку")

def start(bot, update):
    chat_id = update.message.chat_id
    bot.sendMessage(chat_id, text="Привет! Я бот, который умеет стилизовывать картинки!")
    bot.sendMessage(chat_id, text="Пришли мне картинку, которую надо стилизовать.")


if __name__ == '__main__':
    from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
    import logging

    # Включим самый базовый логгинг, чтобы видеть сообщения об ошибках
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
    # используем прокси, так как без него у меня ничего не работало.
    # если есть проблемы с подключением, то попробуйте убрать прокси или сменить на другой
    # проекси ищется в гугле как "socks4 proxy"
    #updater = Updater(token=token, request_kwargs={'proxy_url': 'socks4://168.195.171.42:44880'})
    #updater = Updater(token=token, request_kwargs={'proxy_url': 'socks4://192.169.216.124:8800'})
    #updater = Updater(token=token, request_kwargs={'proxy_url': 'http://nl-84-91-2.friproxy.biz:443'})
    #updater = Updater(token=token)
    updater = Updater(token=token, request_kwargs={'proxy_url': 'socks4://89.27.175.95:4145'})

    # В реализации большого бота скорее всего будет удобнее использовать Conversation Handler
    # вместо назначения handler'ов таким способом
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, send_prediction_on_photo))
    updater.dispatcher.add_handler(CommandHandler('start',start))
    updater.start_polling()
