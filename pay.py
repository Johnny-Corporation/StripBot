from __main__ import *
import threading
import time
import random
from yoomoney import Client
from yoomoney import Quickpay

token = yoomoney_token
client = Client(token)


def accept_payment(message, photos, cost):
    def payment_with_timeout(url, timeout=120.0):
        result = [
            None
        ]  # используем список вместо прямого значения, чтобы иметь возможность изменить его в любом потоке

        def check_payment(label):
            # Проверяем историю операции
            history = client.operation_history(label=label)
            for operation in history.operations:
                if operation.status == "success":
                    result[0] = True
                else:
                    result[0] = False

        markup = types.InlineKeyboardMarkup()
        temp_button = types.InlineKeyboardButton(
            text=templates['ru']["go_pay.txt"],
            url=url,
        )
        markup.add(temp_button)

        bot.send_message(
            message.chat.id,
            templates['ru']["info_about_buy.txt"].format(photos=photos, cost=cost),
            reply_markup=markup,
            parse_mode="HTML",
        )

        start_time = time.time()

        # Запускаем таймеры, пока не истечет общее время ожидания
        while time.time() - start_time < timeout and result[0] is None:
            timer = threading.Timer(2.0, lambda: check_payment(label))
            timer.start()
            timer.join()

        if result[0] is None:
            result[0] = False

        if result[0]:

            users[message.chat.id].apply_payment(int(photos))

            bot.send_message(
                message.chat.id,
                templates['ru']["payment_success.txt"].format(photos=users[message.chat.id].photos_limit-users[message.chat.id].used_photos),
                parse_mode="HTML",
            )
        else:
            bot.send_message(message.chat.id, templates['ru']["payment_canceled.txt"])

    # Генерация случайного 8-значного числа для label
    label = random.randint(10000000, 99999999)

    # Создание формы оплаты
    quickpay = Quickpay(
        receiver="4100118270605528",
        quickpay_form="shop",
        targets="Buy product",
        paymentType="SB",
        sum=cost,  # cost
        label=label,
    )

    # Вызов функции с передачей ссылки
    threading.Thread(
        target=payment_with_timeout, args=(quickpay.redirected_url, 120.0)
    ).start()
