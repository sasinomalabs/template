from kubernetes import client, config

config.load_incluster_config()

# Create API instance
v1 = client.CoreV1Api()

# List all pods in the cluster
pods = v1.list_pod_for_all_namespaces()
for pod in pods.items:
    print(f"Pod Name: {pod.metadata.name}, Namespace: {pod.metadata.namespace}")
