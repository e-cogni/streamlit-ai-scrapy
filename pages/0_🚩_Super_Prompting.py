import requests
import streamlit as st
import random
import string
import time


"# Super Prompting"

image_response = None
image_timestamp = str(time.time())
image_hash = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
image_key = 'image_' + image_timestamp + '-' + image_hash
image_name = lambda: f"{image_key}.png"

# image size options by width and height
imageSizeOptions = {
    'square-1024': (1024, 1024),
    'square-1200': (1200, 1200),
    'square-1600': (1600, 1600),
    'fb-page-cover (1024x664)': (1024, 664),
}

@st.fragment()
def btn_download_image(image_bytes):
    # generate a random filename
    filename = image_name()
    st.download_button(
        label="Download Image",
        data=image_bytes,
        file_name=filename,
        mime="image/png",
    )

def generate_image(model, prompt, negative_prompt, image_dimensions):
    account_id = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
    api_token = st.secrets["CLOUDFLARE_API_TOKEN"]
    headers = {
        "Authorization": f"Bearer {api_token}",
    }
    url = f"https://gateway.ai.cloudflare.com/v1/b70f22c8e75bf434686321ac6f4c7730/ai-cf-test/workers-ai/{model}"
    response = requests.post(
        url,
        headers=headers,
        json={
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "height": imageSizeOptions[image_dimensions][1],
            "width": imageSizeOptions[image_dimensions][0],
        },
    )
    return response

with st.form("text_to_image"):
    # All models at https://developers.cloudflare.com/workers-ai/models/
    model = st.selectbox(
        "Choose your Text-To-Image model",
        options=(
            "@cf/stabilityai/stable-diffusion-xl-base-1.0",
            "@cf/lykon/dreamshaper-8-lcm",
            "@cf/bytedance/stable-diffusion-xl-lightning",
            "@cf/black-forest-labs/flux-1-schnell",
        ),
    )
    prompt = st.text_area("Prompt")
    negative_prompt = st.text_area("Negative Prompt", "Ugly, distort, low resolution, people, malformed, low poly")
    image_dimensions = st.selectbox("Image Size", options=list(imageSizeOptions.keys()))
    submitted = st.form_submit_button("Generate")

if submitted:
    if not prompt.strip():
        st.warning("Prompt cannot be empty. Please enter a prompt.")
    else:
        with st.spinner("Generating..."):
            image_response = generate_image(model, prompt, negative_prompt, image_dimensions)
            st.image(image_response.content, caption=prompt)
            #f"_Generated with [Cloudflare Workers AI](https://developer.cloudflare.com/workers-ai/) using the `{model}_`"

if image_response:
    btn_download_image(image_response.content)