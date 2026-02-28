import random
import time

def next_state(state: str, event: str) -> str:
    transitions = {
        "NEW": {
            "PAY_OK": "PAID",
            "PAY_FAIL": "CANCELLED",
        },
        "PAID": {
            "COMPLETE": "DONE",
            "CANCEL": "CANCELLED",
        },
        "DONE": {},
        "CANCELLED": {},
    }

    return transitions.get(state, {}).get(event, state)


class OrderSaga:
    def __init__(self):
        self.state = "NEW"

    def reserve(self):
        print("Резерв товара выполнен")

    def cancel_reserve(self):
        print("Отмена резерва...")

        # retry пока не получится
        while True:
            success = random.choice([True, False])
            if success:
                print("Резерв успешно отменён")
                break
            print("Ошибка отмены, повторяем...")
            time.sleep(1)

    def pay(self):
        print("Попытка оплаты...")
        return random.choice([True, False])

    def complete(self):
        print("Заказ завершён")

    def run(self):
        print(f"Начальное состояние: {self.state}")

        # Шаг 1 — резерв
        self.reserve()

        # Шаг 2 — оплата
        payment_success = self.pay()

        if payment_success:
            self.state = next_state(self.state, "pay_success")
            print(f"Состояние: {self.state}")

            # Шаг 3 — завершение
            self.state = next_state(self.state, "complete")
            self.complete()
            print(f"Состояние: {self.state}")

        else:
            print("Оплата не прошла")
            self.cancel_reserve()
            self.state = next_state(self.state, "pay_failed")
            print(f"Состояние: {self.state}")