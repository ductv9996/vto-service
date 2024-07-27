# UP SERVICES
## Run broker
- Installation
```
sudo apt-get update
sudo apt-get install rabbitmq-server
sudo apt-get install redis-server
```
- Start broker service
```
sudo service rabbitmq-server start
sudo service redis-server start
```
- Check status
```
sudo systemctl status rabbitmq-server
sudo systemctl status redis-server
```
- Restart
```
sudo systemctl restart rabbitmq-server
sudo systemctl restart redis-server
```
## Celery worker
```
celery -A worker.worker worker -l INFO --pool=solo
uvicorn apps.api:app --host 0.0.0.0 --port 8888
```
## setup google cloud token
## tmux
```
tmux new -s fastapi
tmux attach -t fastapi

tmux new -s celery
tmux attach -t celery
```

Stop your app node by below command.
sudo rabbitmqctl stop_app
Reset your node by below command. Removes the node from any cluster it belongs to, removes all data from the management database, such as configured users and vhosts, and deletes all persistent messages.(Be careful while using it.) To backup your data before reset look here
sudo rabbitmqctl reset
Start your Node by below command.
sudo rabbitmqctl start_app
Restart your vhost by below commad.
sudo rabbitmqctl restart_vhost