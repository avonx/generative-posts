from datetime import datetime
import os
from utils import *

def generate_prompt_for_sd(looks, situation, without_person=False):
    # inspired by https://gist.github.com/bluelovers/92dac6fe7dcbafd7b5ae0557e638e6ef
    if not without_person: # 人が映る場合
        prompt = f"""
        Stable Diffusion is an AI art generation model similar to DALLE-2.

        You need to generate a picture posted on the following person's instagram account.

        looks:
        {looks}

        Below is a list of prompts that can be used to generate images with Stable Diffusion:

        - full body, jumping, white T shirts and denim skirts,a japanese beauty girl
        - Teenage girl with her high school friends at Universal Studios, cheerful, sunlight, amusement park backdrop, asian, long brown hair, 17 years old.

        Make it simple.
        
        I want you to write me a prompt exactly about the idea written after IDEA. Follow the structure of the example prompts. This means a very short description of the scene, followed by modifiers divided by commas to alter the mood, style, lighting, and more.
        output only 1 prompt you think it's great
        
        IDEA: 「{situation}」
        """
    else: # 人が映らない場合
        prompt = f"""
        Stable Diffusion is an AI art generation model similar to DALLE-2.

        You need to generate a picture posted on the following person's instagram account.

        - a tall red pagoda surrounded by trees with fall foliages on it's sides and a blue sky, japan, Ai-Mitsu, cloisonnism, photo
        - a beach with a chair and umbrella on it and the sun shining through the palm tree leaves on the beach, dau-al-set, photo, sun

        Make it simple.
        
        I want you to write me a prompt exactly about the idea written after IDEA. Follow the structure of the example prompts. This means a very short description of the scene, followed by modifiers divided by commas to alter the mood, style, lighting, and more.
        output only 1 prompt you think it's great

        Please do not feature any people.
        
        IDEA: 「{situation}」
        """

    model = "gpt-4"
    max_tokens = 2000
    temperature = 1

    response = get_openai_response(prompt, model, max_tokens, temperature)
    return response

def generate_prompt_for_comment(name, looks, characteristics, situation):
    prompt = f"""
    あなたは、{name}さんです。

    あなたの性格:
    {characteristics}

    あなたのその他の情報：
    {looks}

    状況:
    {situation}

    Instagramに投稿する写真に書くコメントを考えてください。
    ハッシュタグをつけても大丈夫です。
    あなたのコメント（鉤括弧などは不要）：
    """

    model = "gpt-4"
    max_tokens = 2000
    temperature = 1

    response = get_openai_response(prompt, model, max_tokens, temperature)
    cleaned_response = response.replace('<', '').replace('>', '').replace('"', '').replace("'", "").replace("「", "").replace("」", "")
    return cleaned_response

# すべてのテキスト情報を保存するための関数を定義
def append_to_log(file_path, title, content):
    with open(file_path, 'a') as f:
        f.write(f"{title}\n{'='*len(title)}\n")
        f.write(content)
        f.write("\n\n")

# 画像付き投稿を生成、本人が画像中に登場する前提だが、風景の写真のこともありそうなので「with_face」とした
def generate_multimodal_post(name, looks, characteristics, situation, reference_image_path, without_person=False):
    print(f"{name}のこのシーンの投稿の生成を開始しました。「{situation}」")

    # タイムスタンプでフォルダ名を生成
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_directory = f'./output/{timestamp_str}'

    # タイムスタンプの名前でフォルダを作成
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 'output' フォルダとタイムスタンプの名前のサブフォルダが存在しない場合に作成
    if not os.path.exists('./output'):
        os.mkdir('./output')
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    # ログファイルのパスを指定
    log_file_path = f'{output_directory}/log.txt'

    # 対象人物の写真を取り込む
    reference_image = Image.open(reference_image_path)
    reference_image.save(f'{output_directory}/reference.png')  # 保存

    # 状況をLLMで描写して、StableDiffusion用のプロンプトを生成
    prompt_for_sd = generate_prompt_for_sd(looks=looks, situation=situation, without_person=without_person)

    # 外見、内面、状況などの情報をログに保存
    append_to_log(log_file_path, "Looks", "\n".join([f"- {item}" for item in looks]))
    append_to_log(log_file_path, "Characteristics", "\n".join([f"- {item}" for item in characteristics]))
    append_to_log(log_file_path, "Situation", situation)
    append_to_log(log_file_path, "Prompt for SD", prompt_for_sd)

    # StableDiffusion用のプロンプトを整形する。
    prompt =  "xxmixgirl, " + prompt_for_sd # 今回使っているSDのモデルのトリガーワード。
    negative_prompt = " (worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch), tooth, open mouth, bad hand, bad fingers" # 推奨ネガティブプロンプト
    
    # StableDiffusionサーバーにリクエストを送り、画像生成
    generated_image, pnginfo = generate_image(prompt, negative_prompt, reference_image)
    generated_image.save(f'{output_directory}/output.png', pnginfo=pnginfo)  # 保存

    # コメントを生成してみる。写真を選んだ後コメントに悩む感じをイメージしてデザイン。
    # comment = """お寺で疲れを癒してきました！座禅ってあんなにスッキルするんだね〜お勧めしてくれた方に感謝！ #座禅"""
    situation_with_layout = situation + f"次のような構図の画像を撮ってみた。「{prompt_for_sd}」" # situationは、引き継ぐが、撮った写真の構図を新たに加えておく。
    comment = generate_prompt_for_comment(name, looks, characteristics, situation_with_layout)
    append_to_log(log_file_path, "Comment", comment)

    print(f"{name}のこのシーンの投稿の生成が完了しました。保存フォルダは「{output_directory}」")

    return generate_image, output_directory, f'{output_directory}/output.png', comment

    # 以下は、Reactor単体で使う時。
    # input_image_path = "./input/target.png"
    # reference_image_path = "./input/reference.jpeg"
    # input_image = Image.open(input_image_path)
    # reference_image = Image.open(reference_image_path)
    # output_image = transform_image(input_image, reference_image)


if __name__=="__main__":
    from generate_mockup import generate_instagram_mockup

    # 人物の名前（テキトーでOK）
    name = "橋本環奈"

    # 人物の外見を描写
    looks = """
    - 165cm
    - girl
    - 17 years old
    - black hair
    - long hair
    - Japanse
    """

    # 人物の内面を描写
    characteristics = """
    - 芸能人
    - ちょっと天然
    - 可愛い
    - 仕事熱心
    """

    # 環境を描写
    situation = "着物を着て神社で写真を撮った。"

    # 対象人物の写真を取り込む
    reference_image_path = "./input/reference_2.png"

    image, output_directory, image_path, comment = generate_multimodal_post(name, looks, characteristics, situation, reference_image_path, without_person=False)

    # Instagramの形式にしてみる
    generated_mockup = generate_instagram_mockup(circle_image_path=reference_image_path,
                                                rectangle_image_path=image_path,
                                                name=name,
                                                situation=situation,
                                                comment=comment
                                                )
    # モックアップを保存
    generated_mockup.save(f'{output_directory}/mockup.png')  # 保存