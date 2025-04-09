import vertexai
from vertexai.preview import model_garden

vertexai.init(project="techbio-c-suite-copilot", location="us-east1")

model = model_garden.OpenModel("google/txgemma@txgemma-27b-chat")
endpoint = model.deploy(
  accept_eula=True,
  machine_type="a3-highgpu-2g",
  accelerator_type="NVIDIA_H100_80GB",
  accelerator_count=2,
  serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20250114_0916_RC00_maas",
  endpoint_display_name="google_txgemma-27b-chat-mg-one-click-deploy",
  model_display_name="google_txgemma-27b-chat-1743580936097",
)