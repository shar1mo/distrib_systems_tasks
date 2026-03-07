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
    def __init__(self, force_payment_result=None, force_cancel_result=None):
        self.state = "NEW"
        self.force_payment_result = force_payment_result  # Для тестирования
        self.force_cancel_result = force_cancel_result    # Для тестирования

    def reserve(self):
        print("Резерв товара выполнен")

    def cancel_reserve(self):
        print("Отмена резерва...")
        attempt = 1
        while True:
            if self.force_cancel_result is not None:
                success = self.force_cancel_result
            else:
                success = random.choice([True, False])
                
            if success:
                print(f"Резерв успешно отменён (попытка #{attempt})")
                break
            print(f"Ошибка отмены (попытка #{attempt}), повторяем...")
            attempt += 1
            time.sleep(1)

    def pay(self):
        print("Попытка оплаты...")
        if self.force_payment_result is not None:
            return self.force_payment_result
        return random.choice([True, False])

    def complete(self):
        print("Заказ завершён")

    def run(self):
        print(f"Начальное состояние: {self.state}")
        self.reserve()
        payment_success = self.pay()

        if payment_success:
            self.state = next_state(self.state, "PAY_OK")
            print(f"Состояние после оплаты: {self.state}")
            self.state = next_state(self.state, "COMPLETE")
            self.complete()
            print(f"Конечное состояние: {self.state}")
            return "SUCCESS"
        else:
            print("Оплата не прошла")
            self.cancel_reserve()
            self.state = next_state(self.state, "PAY_FAIL")
            print(f"Конечное состояние: {self.state}")
            return "FAILED"


# Тестирование сценариев
def run_tests():
    print("ТЕСТ 1: Успешная оплата")
    order1 = OrderSaga(force_payment_result=True)
    order1.run()
    
    print("\nТЕСТ 2: Неуспешная оплата (успешная отмена с первой попытки)")
    order2 = OrderSaga(force_payment_result=False, force_cancel_result=True)
    order2.run()
    
    print("\nТЕСТ 3: Неуспешная оплата (отмена со второй попытки)")
    # Сначала False, потом True
    cancel_results = [False, True]
    cancel_index = 0
    
    class TestOrderSaga(OrderSaga):
        def cancel_reserve(self):
            print("Отмена резерва...")
            nonlocal cancel_index
            while True:
                success = cancel_results[cancel_index]
                cancel_index += 1
                if success:
                    print(f"Резерв успешно отменён (попытка #{cancel_index})")
                    break
                print(f"Ошибка отмены (попытка #{cancel_index}), повторяем...")
                time.sleep(1)
    
    order3 = TestOrderSaga(force_payment_result=False)
    order3.run()


if __name__ == "__main__":
    # Запуск обычного режима
    print("СЛУЧАЙНЫЙ РЕЖИМ")
    for i in range(5):
        print(f"\n--- Заказ #{i+1} ---")
        order = OrderSaga()
        order.run()
        time.sleep(1)
    
    # Запуск тестов
    print("ТЕСТОВЫЙ РЕЖИМ")
    run_tests()