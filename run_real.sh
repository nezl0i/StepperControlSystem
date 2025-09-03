# run_real.sh
#!/bin/bash
echo "Запуск веб-интерфейса с реальным оборудованием..."
python3 -m src.web_interface --port 5000 --host 0.0.0.0