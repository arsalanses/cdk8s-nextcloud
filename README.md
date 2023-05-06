### useful commands:

```bash
cdk8s synth
```

```bash
kubectl apply -f dist/cdk8s-nextcloud.k8s.yaml
```

```bash
kubectl port-forward my-pod 8080:80
kubectl exec -it my-pod bash
```

```bash
pipenv install --dev
pipenv shell
```