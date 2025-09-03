# run_simulated.sh
#!/bin/bash
echo "Запуск веб-интерфейса в режиме симуляции..."
python3 -m src.web_interface --simulate --port 5000 --host 0.0.0.0