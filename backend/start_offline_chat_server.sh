./venv/bin/python -m llama_cpp.server \
	--model ./model/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf \
	--model_alias default \
	--n_gpu_layers -1 \
	--n_ctx 0 \
	--n_threads 4
