from generate_multimodal_post import generate_multimodal_post
from generate_mockup import generate_instagram_mockup
from utils import *
import os

def generate_situation(yaml_path):
    person_info = load_setting_file(yaml_path)

    name = person_info["name"]
    looks = person_info["looks"]
    characteristics = person_info["characteristics"]

    prompt = f"""
    あなたは、{name}さんです。

    あなたの性格:
    {characteristics}

    あなたのその他の情報：
    {looks}

    今回、あなたはInstagramに投稿する過去の出来事を考えます。
    例）
    - 花見で桜を見に行った
    - 美味しいご飯を食べた
    - ビーチに行った
    - 友達とユニバに行った
    - 家の掃除をした
    - 京都でのんびり過ごした

    この人物が投稿しそうな出来事を考えてください。
    投稿する写真を選ぶ必要があるので、その情景がわかりやすいように、表現してください。
    ただし１行で簡潔に。

    あなたの投稿する出来事を現在形で一個だけ回答して：
    """

    model = "gpt-4"
    max_tokens = 2000
    temperature = 1

    response = get_openai_response(prompt, model, max_tokens, temperature)
    cleaned_response = response.replace('<', '').replace('>', '').replace('"', '').replace("'", "").replace("「", "").replace("」", "")
    return cleaned_response

def generate_instagram_post(yaml_path, situation, save_dir=None):
    # 'temp' フォルダとタイムスタンプの名前のサブフォルダが存在しない場合に作成
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    person_info = load_setting_file(yaml_path)

    name = person_info["name"]
    looks = person_info["looks"]
    characteristics = person_info["characteristics"]

    print(f"Name: {name}")
    print(f"Looks: {looks}")
    print(f"Characteristics: {characteristics}")

    # 環境を描写
    print(f"Situation: {situation}")

    # 対象人物の写真を取り込む
    reference_image_path = f"./people/{os.path.basename(yaml_path).replace('.yaml', '.png')}"

    # メインの処理
    image, output_directory, image_path, comment = generate_multimodal_post(name, looks, characteristics, situation, reference_image_path, without_person=False)

    # Instagramの投稿のモックアップにする
    generated_mockup = generate_instagram_mockup(circle_image_path=reference_image_path,
                                                rectangle_image_path=image_path,
                                                name=name,
                                                situation=situation,
                                                comment=comment
                                                )
    # モックアップを保存
    generated_mockup.save(f'{output_directory}/mockup.png')  # 保存
    if save_dir:
        generated_mockup.save(f'{save_dir}/post_{name}_{situation}.png')  # 保存

    return generate_instagram_mockup, comment
    

if __name__=="__main__":
    # peopleディレクトリ内のすべての人物の投稿を5回ずつ生成
    directory_path = "./people"
    for filename in os.listdir(directory_path):
        if filename.endswith(".yaml"):
            yaml_path = os.path.join(directory_path, filename)
            for i in range(5):
                # situation は設定ファイルを元にAIに考えさせる。
                situation = generate_situation(yaml_path)
                # situation = "夜に友達とラーメンを食べに行った"

                # 投稿の生成（ファイルは tempフォルダと、outputフォルダに格納される）
                generate_instagram_mockup, comment = generate_instagram_post(yaml_path, situation, save_dir="./temp")
