# Triton Inference Client (Dummy Model)

This is a minimal example of using NVIDIA Triton Inference Server with a simple client and a dummy model for inference. The goal is to demonstrate how to interact with Triton using a Python client.

## 🧠 What’s Inside

- A basic Triton client script
- A dummy model placed inside the model repository
- Docker command to run Triton server on CPU

## 🐳 Running Triton Server on CPU

Make sure you have Docker installed, then run the following command from the root of the project:

```bash
docker run --rm -p8000:8000 -p8001:8001 -p8002:8002 \
  -v $(pwd)/triton_client/model:/models \
  nvcr.io/nvidia/tritonserver:24.01-py3 tritonserver --model-repository=/models
```

This will start the Triton server and load the model from `triton_client/model`.

## 🧪 Running the Client

After the server is up and running, execute the client script:

```bash
python triton_client/client.py
```

This script sends a dummy inference request to Triton and prints the result.

## 📁 Project Structure

```
triton-client-project/
├── triton_client/
│   ├── client.py
│   └── model/
│       └── dummy_model/   # Your dummy model directory
│           ├── config.pbtxt
│           └── 1/
│               └── model.onnx  # Or any supported model format
└── README.md
```

## 📌 Requirements

- Python 3.7+
- `tritonclient` Python package (Install via: `pip install tritonclient[http]`)
- Docker

## 📚 References

- [Triton Inference Server Documentation](https://github.com/triton-inference-server/server)
- [Triton Python Client Examples](https://github.com/triton-inference-server/client)

---

Feel free to clone, modify, and experiment with this setup to better understand inference serving using Triton.
