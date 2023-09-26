import openai
import time
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from io import BytesIO
import yaml
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SERVER_ENDPOINT")
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_image(prompt, negative_prompt, reference_image):
    # 顔のリファレンス画像をバイナリ化
    buffered_reference = BytesIO()
    reference_image.save(buffered_reference, format="PNG")
    img_str_reference = base64.b64encode(buffered_reference.getvalue()).decode()

    # ReActor arguments:
    args=[
        img_str_reference, #0
        True, #1 Enable ReActor
        '0', #2 Comma separated face number(s) from swap-source image
        '0', #3 Comma separated face number(s) for target image (result)
        '/workspace/stable-diffusion-webui/models/roop/inswapper_128.onnx', #4 model path
        'CodeFormer', #4 Restore Face: None; CodeFormer; GFPGAN
        1, #5 Restore visibility value
        True, #7 Restore face -> Upscale
        '4x_NMKD-Superscale-SP_178000_G', #8 Upscaler (type 'None' if doesn't need), see full list here: http://127.0.0.1:7860/sdapi/v1/script-info -> reactor -> sec.8
        2, #9 Upscaler scale value
        1, #10 Upscaler visibility (if scale = 1)
        True, #11 Swap in source image なぜかこれTrueにしないと出力も元画像が送られてくる。。。なんでやねん
        True, #12 Swap in generated image
        2, #13 Console Log Level (0 - min, 1 - med or 2 - max)
        0, #14 Gender Detection (Source) (0 - No, 1 - Female Only, 2 - Male Only)
        0, #15 Gender Detection (Target) (0 - No, 1 - Female Only, 2 - Male Only)
        False, #16 Save the original image(s) made before swapping
    ]

    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": 30,
        "cfg_scale": 9,
        "width": 1024,
        "height": 1024,
        "sampler_index": "DPM++ 2M",
        "alwayson_scripts": {
            "reactor": {
                "args": args
                }
            }  
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    r = response.json()

    for i in r['images']: # ここの表現は将来バッチ処理を実装するときよう
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        return image, pnginfo

def transform_image(input_image, reference_image):
    buffered_input = BytesIO()
    input_image.save(buffered_input, format="PNG")
    img_str_input = base64.b64encode(buffered_input.getvalue()).decode()

    buffered_reference = BytesIO()
    reference_image.save(buffered_reference, format="PNG")
    img_str_reference = base64.b64encode(buffered_reference.getvalue()).decode()

    # input_imageのwidthとheightを取得
    width = input_image.width
    height = input_image.height

    # # 長い方の辺がどれだけ250pxより大きいかを確認して、それに基づいてリサイズの倍率を計算
    # if width > height:
    #     ratio = 200.0 / width
    # else:
    #     ratio = 200.0 / height

    # # 新しい縦横のサイズを計算
    # new_width = int(width * ratio)
    # new_height = int(height * ratio)

    # ReActor arguments:
    args=[
        img_str_reference, #0
        True, #1 Enable ReActor
        '0', #2 Comma separated face number(s) from swap-source image
        '0', #3 Comma separated face number(s) for target image (result)
        '/workspace/stable-diffusion-webui/models/roop/inswapper_128.onnx', #4 model path
        'CodeFormer', #4 Restore Face: None; CodeFormer; GFPGAN
        1, #5 Restore visibility value
        True, #7 Restore face -> Upscale
        '4x_NMKD-Superscale-SP_178000_G', #8 Upscaler (type 'None' if doesn't need), see full list here: http://127.0.0.1:7860/sdapi/v1/script-info -> reactor -> sec.8
        2, #9 Upscaler scale value
        1, #10 Upscaler visibility (if scale = 1)
        False, #11 Swap in source image なぜかこれTrueにしないと出力も元画像が送られてくる。。。なんでやねん
        True, #12 Swap in generated image
        2, #13 Console Log Level (0 - min, 1 - med or 2 - max)
        0, #14 Gender Detection (Source) (0 - No, 1 - Female Only, 2 - Male Only)
        0, #15 Gender Detection (Target) (0 - No, 1 - Female Only, 2 - Male Only)
        False, #16 Save the original image(s) made before swapping
    ]

    payload = {
    "init_images": [img_str_input], # 入力画像
    "resize_mode": 0,
    "denoising_strength": 0,
    "prompt": "a man",
    "seed": -1,
    "subseed": -1,
    "subseed_strength": 0,
    "seed_resize_from_h": -1,
    "seed_resize_from_w": -1,
    "sampler_name": "Euler", # ※2
    "batch_size": 1,
    "n_iter": 1,
    "steps": 20, # ※3
    "cfg_scale": 7,
    "width": width,
    "height": height,
    "override_settings": {},
    "override_settings_restore_afterwards": False,
    "script_args": [],
    "sampler_index": "Euler", # ※2
    "include_init_images": False,
    "script_name": "",
    "send_images": True,
    "save_images": True,
    "alwayson_scripts": {
        "reactor": {
            "args": args
        }
    } 
    }

    response = requests.post(url=f'{url}/sdapi/v1/img2img', json=payload)
    r = response.json()

    for i in r['images']: # ここの表現は将来バッチ処理を実装するときよう
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save('./output/generated_image.png', pnginfo=pnginfo)
        return image

def retry_with_backoff(func, max_retries=3, backoff_time=1):
    for i in range(max_retries + 1):
        try:
            return func()
        except openai.error.APIConnectionError as e:
            if i == max_retries:
                raise e
            else:
                print(f"Got rate limited, retrying in {backoff_time} seconds (attempt {i+1}/{max_retries+1})")
                time.sleep(backoff_time)
                backoff_time *= 10

def get_openai_response(prompt, model, max_tokens, temperature):
    def _get_openai_response():
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'assistant', 'content': prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response['choices'][0]['message']['content']

    return retry_with_backoff(_get_openai_response)

def load_setting_file(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as file:
        person_info = yaml.safe_load(file)
    return person_info