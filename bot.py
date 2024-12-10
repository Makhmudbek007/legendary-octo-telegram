from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

# Ваш токен Telegram-бота
TOKEN = '7847424001:AAF4uaGDCEjqSzXmVsYzRBD-cJueHN0CuZ0'

# Определяем этапы разговора
WAITING_FOR_TEXT = 1

# Генерация пары RSA-ключей
def generate_rsa_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

# Шифрование текста
def encrypt_message(public_key, message):
    public_key_obj = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(public_key_obj)
    encrypted_message = cipher.encrypt(message.encode('utf-8'))
    return base64.b64encode(encrypted_message).decode('utf-8')

# Хранение ключей в глобальных переменных (упрощённо для примера)
PRIVATE_KEY, PUBLIC_KEY = generate_rsa_keys()

# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Привет! Отправьте мне текст, и я верну его в зашифрованном виде с помощью RSA.")
    return WAITING_FOR_TEXT

# Обработчик текста для шифрования
def encrypt_text(update: Update, context: CallbackContext) -> int:
    user_text = update.message.text
    encrypted_text = encrypt_message(PUBLIC_KEY, user_text)
    update.message.reply_text(f"Ваш зашифрованный текст:\n{encrypted_text}")
    return ConversationHandler.END

# Обработчик отмены
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

# Основная функция
def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # ConversationHandler для управления шагами разговора
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_TEXT: [MessageHandler(Filters.text & ~Filters.command, encrypt_text)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conversation_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
