python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct \
  --gpu-memory-utilization 0.95 \
  --max-model-len 8192
