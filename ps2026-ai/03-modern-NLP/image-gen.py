from huggingface_hub import InferenceClient

client = InferenceClient(
    api_key="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"
)

image = client.text_to_image(
    prompt="A futuristic city at sunset",
    model="black-forest-labs/FLUX.1-dev"
)

image.show()
image.save("output.png")