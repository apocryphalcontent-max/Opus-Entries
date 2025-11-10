# FILE 25: KUBERNETES DEPLOYMENT
# ===============================
# Production Kubernetes manifests for Opus Maximus.
# Optimized for: 16-Core CPU | 16GB+ VRAM Nodes (Edits 2, 3, 4 applied to configs)
# File 15 of 20: Infrastructure (K8s)

# ============================================================================
# kubernetes/namespace.yaml
# ============================================================================
apiVersion: v1
kind: Namespace
metadata:
  name: opus-maximus
  labels:
    name: opus-maximus
---
# ============================================================================
# kubernetes/configmap.yaml
# ============================================================================
apiVersion: v1
kind: ConfigMap
metadata:
  name: opus-config
  namespace: opus-maximus
data:
  OPUS_DEBUG: "false"
  OPUS_LOG_LEVEL: "INFO"
  CUDA_VISIBLE_DEVICES: "0"
  # Edit 3: Increased context window to match 16GB VRAM capacity
  MODEL_N_CTX: "16384"
  # Edit 2: Optimized batch size for DDR5 bandwidth
  MODEL_N_BATCH: "1024"
  MIN_WORD_COUNT: "10000"
---
# ============================================================================
# kubernetes/statefulset.yaml
# ============================================================================
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: opus-maximus
  namespace: opus-maximus
spec:
  serviceName: opus-maximus
  replicas: 1
  selector:
    matchLabels:
      app: opus-maximus
  template:
    metadata:
      labels:
        app: opus-maximus
    spec:
      containers:
      - name: opus-maximus
        image: opus-maximus:latest
        imagePullPolicy: IfNotPresent
        # Resource requests and limits
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            # Edit 8: Allow full 32GB RAM usage
            memory: "32Gi"
            # Edit 4: Allow full 16-core CPU usage
            cpu: "16"
            nvidia.com/gpu: "1"
        # Environment variables
        envFrom:
        - configMapRef:
            name: opus-config
        # Volume mounts
        volumeMounts:
        - name: entries-storage
          mountPath: /app/GENERATED_ENTRIES_MASTER
        - name: corpus-storage
          mountPath: /app/OPUS_MAXIMUS_INDIVIDUALIZED
        - name: models-storage
          mountPath: /app/models
        - name: logs
          mountPath: /app/logs
        # Liveness and readiness probes
        livenessProbe:
          exec:
            command:
            - python3
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          exec:
            command:
            - python3
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 10
          periodSeconds: 10
      # Node selector for GPU
      nodeSelector:
        accelerator: nvidia-gpu
      # Volumes
      volumes:
      - name: entries-storage
        persistentVolumeClaim:
          claimName: entries-pvc
      - name: corpus-storage
        persistentVolumeClaim:
          claimName: corpus-pvc
      - name: models-storage
        persistentVolumeClaim:
          claimName: models-pvc
      - name: logs
        emptyDir: {}
---
# ============================================================================
# kubernetes/pvc.yaml - Persistent Volume Claims
# ============================================================================
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: entries-pvc
  namespace: opus-maximus
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 500Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: corpus-pvc
  namespace: opus-maximus
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 100Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: models-pvc
  namespace: opus-maximus
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 200Gi
---
# ============================================================================
# kubernetes/service.yaml
# ============================================================================
apiVersion: v1
kind: Service
metadata:
  name: opus-maximus
  namespace: opus-maximus
spec:
  type: LoadBalancer
  ports:
  - port: 8501
    targetPort: 8501
    name: dashboard
  selector:
    app: opus-maximus
---
# ============================================================================
# kubernetes/hpa.yaml - Horizontal Pod Autoscaling
# ============================================================================
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: opus-maximus-hpa
  namespace: opus-maximus
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: StatefulSet
    name: opus-maximus
  minReplicas: 1
  maxReplicas: 3
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
---
# ============================================================================
# kubernetes/ingress.yaml
# ============================================================================
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: opus-maximus-ingress
  namespace: opus-maximus
spec:
  ingressClassName: nginx
  rules:
  - host: opus-maximus.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: opus-maximus
            port:
              number: 8501
  tls:
  - hosts:
    - opus-maximus.local
    secretName: opus-tls