echo /share/ha-scheduler
mkdir -p /share/ha-scheduler

chmod -R 777 /share/ha-scheduler

echo Run APP!
#export FLASK_ENV=development
python3 /home/app.py