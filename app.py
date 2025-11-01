import gradio as gr
from diffusers import StableDiffusionPipeline
import torch

# --- 1. Load the Model ---
# This is the Stable Diffusion v1.5 model. It's downloaded the first time you run the app.
# Using 'fp16' (16-bit precision) saves memory and is faster on modern GPUs.
# We explicitly set a low-resource-friendly model path for a quick start.
model_id = "runwayml/stable-diffusion-v1-5"
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Loading model on device: {device}")

try:
    # Load the pipeline. The 'torch_dtype=torch.float16' is key for speed and memory.
    if device == "cuda":
        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        pipe = pipe.to(device)
    else:
        # Fallback for CPU, will be very slow but works for testing
        pipe = StableDiffusionPipeline.from_pretrained(model_id)
        pipe = pipe.to(device)

    print("Model loaded successfully!")
    
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please ensure your environment is set up correctly and try again.")
    exit()


# --- 2. Define the Generation Function ---
# This function is called every time a user clicks the 'Generate' button.
def generate_image(prompt, num_inference_steps, guidance_scale):
    """Generates an image based on the prompt using the Stable Diffusion pipeline."""
    
    # Simple error handling for an empty prompt
    if not prompt:
        return None 
    
    print(f"Generating image for prompt: '{prompt}'")
    
    # The core generation call
    image = pipe(
        prompt, 
        num_inference_steps=num_inference_steps,  # Controls quality vs speed
        guidance_scale=guidance_scale             # Controls adherence to the prompt
    ).images[0]
    
    return image


# --- 3. Create the Gradio Interface ---
# Define the input and output components for the web interface
iface = gr.Interface(
    fn=generate_image, 
    title="Custom Stable Diffusion Generator",
    description="Enter a prompt and click Generate! (Note: Running on CPU is very slow.)",
    inputs=[
        gr.Textbox(label="Prompt", placeholder="A photorealistic painting of an astronaut riding a horse in a digital art style..."),
        gr.Slider(minimum=10, maximum=100, step=1, value=50, label="Inference Steps (Quality/Time)", info="More steps = higher quality, slower generation."),
        gr.Slider(minimum=1, maximum=20, step=0.5, value=7.5, label="Guidance Scale (Prompt Adherence)", info="Higher scale = model sticks closer to the prompt.")
    ],
    outputs=gr.Image(type="pil", label="Generated Image"),
    allow_flagging="never"
)

# --- 4. Launch the App ---
if __name__ == "__main__":
    iface.launch()