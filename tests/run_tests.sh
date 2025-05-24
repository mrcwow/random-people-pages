#!/bin/bash

run_functional_test() {
    echo "---"
    echo "Запускаем функциональные тесты"
    echo "---"
    pytest tests.py
}

echo "---"
echo "Запускаем тестирование"

if [ $# -eq 0 ]; then
    run_functional_test
else
    case "$1" in
        functional)
            run_functional_test
            ;;
        *)
            echo "Неизвестный аргумент: $1"
            echo "Правильный запуск: sh $0 [ |functional]"
            ;;
    esac
fi