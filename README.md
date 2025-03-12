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