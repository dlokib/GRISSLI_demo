������� 1 � 2.
��� �������, ���������� � ������ �������� ��������� 2 �������:
    python3 ./manage.py runserver
�
    ./server.py

������� ������� �� ����� ��������. ��� ������� ����������� ��������� ������ �����.
���������� �� ��������� ���������� ������ 5 �����.

������� 3.
������ ������� ��� �� SQLite.

INSERT INTO Result (number, fullname, position, salary, tax, month)
SELECT Personnel.number, Employee.name || ' ' || Employee.surname,  Personnel.position,
       Employee.salary / 12, Payment.taxes, Payment.month
FROM Employee, Payment, Personnel
WHERE Payment.employeeID = Employee.id AND Personnel.employeeID = Employee.id;

SELECT * FROM Result;
