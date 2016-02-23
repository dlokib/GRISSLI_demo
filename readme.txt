Задания 1 и 2.
Для запуска, необходимо в разных консолях запустить 2 скрипта:
    python3 ./manage.py runserver
и
    ./server.py

Порядок запуска не имеет значения. Оба скрипта отслеживают состояние канала связи.
Обновления на фронтенде происходят каждые 5 минут.

Задание 3.
Запрос написан для БД SQLite.

INSERT INTO Result (number, fullname, position, salary, tax, month)
SELECT Personnel.number, Employee.name || ' ' || Employee.surname,  Personnel.position,
       Employee.salary / 12, Payment.taxes, Payment.month
FROM Employee, Payment, Personnel
WHERE Payment.employeeID = Employee.id AND Personnel.employeeID = Employee.id;

SELECT * FROM Result;
