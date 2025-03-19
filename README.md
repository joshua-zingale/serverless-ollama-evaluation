# serverless-ollama-evaluation
A project for my cloud computing course: compares efficiency and effectiveness of serverfull vs. serverless LM APIs.


To initialize a worker node for nginx,
```
sudo apt update
sudo apt -y install docker.io
sudo docker run --rm --network host -e OLLAMA_HOST=0.0.0.0:80 jzing002/cs208-server
```

To initialize NGINX node,
```
sudo apt update
sudo apt -y install docker.io
docker run --network host  --name my-custom-nginx-container -v /users/jzing002/nginx.conf:/etc/nginx/nginx.conf:ro --rm nginx
```


Get prometheus pod count data
```
curl -G --data-urlencode 'query=count(kube_pod_container_status_running{pod=~"ollama.*"}) or vector(0)' --data-urlencode 'start=1741824153' --data-urlencode 'end=1741824903' --data-urlencode 'step=10s' http://128.110.216.196:9090/api/v1/query_range
```

Ollama service
```
kn service create ollama   --image docker.io/jzing002/cs208-server   --label app=ollama  --port 11434 --concurrency-limit 4 --request cpu=8000m,memory=48Gi
```


8 pods idle: CPU seconds per second: 0.011, bytes of ram: 300023808
12 pods idle: CPU seconds per second: 0.015, bytes of ram: 445743104