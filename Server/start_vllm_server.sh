#!/usr/bin/env bash

# =========================
# Environment safety flags
# =========================
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export CUDA_VISIBLE_DEVICES=0

# =========================
# Config
# =========================
MODEL_FILE="vllm_model.txt"
MODEL="openai/gpt-oss-20b"
HOST="0.0.0.0"
PORT="8000"

# =========================
# Launch vLLM
# =========================

while true; do

	MODEL=$(cat "$MODEL_FILE")
	python -m vllm.entrypoints.openai.api_server \
	  --model "$MODEL" \
	  --host "$HOST" \
	  --port "$PORT" \
	  --dtype bfloat16 \
	  --gpu-memory-utilization 0.75 \
	  --max-num-batched-tokens 4096 \
	  --enforce-eager
	echo "VLLM Stopped. Restarting..."
	sleep 2
	
	VLLM_PID=$!
	echo $VLLM_PID > /tmp/vllm.pid
	wait $VLLM_PID
done
