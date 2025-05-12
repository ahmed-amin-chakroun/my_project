# client_test.py
import numpy as np
import tritonclient.http as httpclient

client = httpclient.InferenceServerClient(url="localhost:8000")

input_data = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)

inputs = [httpclient.InferInput("input", input_data.shape, "FP32")]
inputs[0].set_data_from_numpy(input_data)

outputs = [httpclient.InferRequestedOutput("output")]

response = client.infer("dummy_model", inputs=inputs, outputs=outputs)
print("Output:", response.as_numpy("output"))

