# Saga для проекта logs-s13

## Шаги бизнес-процесса

1. NEW — объект создан
2. Попытка оплаты
   - Если PAY_OK → PAID
   - Если PAY_FAILED → CANCELLED (запускается компенсация)
3. Если состояние PAID и событие COMPLETE → DONE
4. При необходимости можно выполнить CANCEL → CANCELLED

## Переходы состояний

NEW --PAY_OK--> PAID  
NEW --PAY_FAILED--> CANCELLED  
PAID --COMPLETE--> DONE  
PAID --CANCEL--> CANCELLED  

DONE и CANCELLED — финальные состояния