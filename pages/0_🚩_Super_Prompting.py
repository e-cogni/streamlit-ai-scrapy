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
    'square-1600': (1600, 16000),
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
        account_id = st.secrets["CLOUDFLARE_ACCOUNT_ID"]
        api_token = st.secrets["CLOUDFLARE_API_TOKEN"]
        headers = {
            "Authorization": f"Bearer {api_token}",
        }
        with st.spinner("Generating..."):
            # url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"
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
            st.image(response.content, caption=prompt)
            image_response = response

            f"_Generated with [Cloudflare Workers AI](https://developer.cloudflare.com/workers-ai/) using the `{model}_`"
        # with st.spinner("Creating additional prompt suggestions..."):
        #     prompt_model = "@hf/thebloke/mistral-7b-instruct-v0.1-awq"
        #     prompt_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{prompt_model}"
        #     system_message = """
        #     You are a Stable Diffusion prompt engineer. 
            
        #     The user is going to give you a prompt, and you will provide three detailed suggestions. 
            
        #     Use various photo stylistic terms.
        #     """
        #     prompt_suggestion_response = requests.post(
        #         prompt_url,
        #         headers=headers,
        #         json={
        #             "messages": [
        #                 {"role": "system", "content": system_message},
        #                 {"role": "user", "content": prompt},
        #             ]
        #         },
        #     )
        #     json = prompt_suggestion_response.json()
        #     result = json["result"]
        #     if "response" in result:
        #         st.write(result["response"])
        #         f"_Generated with [Cloudflare Workers AI](https://developer.cloudflare.com/workers-ai/) using the `{prompt_model}` model_"
        #     else:
        #         st.write(result)

    # add a button
 #   if response: 
 #       image_bytes = response.content
 #       st.download_button("Download Image", data=image_bytes, file_name="generated_image.png", mime="image/png")

if image_response:
    btn_download_image(image_response.content)