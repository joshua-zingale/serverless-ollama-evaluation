# serverless-ollama-evaluation
A project for my cloud computing course: compares efficiency and effectiveness of serverfull vs. serverless LM APIs. A group project between Joshua Zingale and Benjamin Bravo.

To set up our KNative environment, run kube-slave/setup-slave.sh on each slave node and run kube-master/setup-master.sh on the master node. All slave nodes must then be joined to the master with the join command printed out by the master node.

Once the master and all of its slave nodes are initialized, the Ollama service may be started with
```bash
kn service create ollama   --image docker.io/jzing002/cs208-server   --label app=ollama  --port 11434 --concurrency-limit 4 --request cpu=8000m,memory=48Gi
```
After this, the client may be run from any computer to connect to the KNative provided ingress for the Ollama service. The client will send prompts to the service, which then responds with streamed responses, which the client receives, collecting metrics thereon. To run the client, the environment variable OLLAMA_URL must be set to `http://{MASTER NODE URL/IP}/`. The client may be run from the client/ directory with
```bash
python3 client.py --load sinusoidal --load_params 0.1 6 600 1800 --output_filename sinusoidal-0.1-6-600-1800
```
to send a sinusoidal load pattern with a minimum of 0.1 requests per second and maximum of 6 requests per second, changing the load over a period of 600 seconds and ending the load after 1800 seconds. Finally, the above command saves the collected data in client/data/results/sinusoidal-0.1-6-600-1800.json

There are other load functions, the parameters for which can be discerned from viewing their function definitions in client/load_functions.py.


To download data from prometheus, use `client/pull_prometheus_data.py`.

All of the collected data from our experiment is located in `data/presentation/`. To generate graphs for these data, run `client/graph_data.py`, which will populate the images in `client/data/images/`.