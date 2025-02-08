import os
import modules.path
import json

from PIL import Image
from PIL.PngImagePlugin import PngInfo
from modules.util import generate_temp_filename
from shutil import copy


def log(img, dic, single_line_number=3, metadata=None, save_metadata_json=False, save_metadata_image=False, keep_input_names=False, input_image_filename=None, output_format='png'):
    date_string, local_temp_filename, only_name = generate_temp_filename(folder=modules.path.temp_outputs_path, extension=output_format, base=input_image_filename if keep_input_names else None)
    os.makedirs(os.path.dirname(local_temp_filename), exist_ok=True)

    if metadata != None:
        with open(modules.path.last_prompt_path, 'w', encoding='utf-8') as json_file:
            json_file.write(metadata)
            json_file.close()

        if save_metadata_json:
            json_path = local_temp_filename.replace(f'.{output_format}', '.json')
            copy(modules.path.last_prompt_path, json_path)

    if output_format == 'png':
        if save_metadata_image:
            pnginfo = PngInfo()
            pnginfo.add_text("Comment", metadata)
        else:
            pnginfo = None
        Image.fromarray(img).save(local_temp_filename, pnginfo=pnginfo)
    elif output_format == 'jpg':
        Image.fromarray(img).save(local_temp_filename, quality=95, optimize=True, progressive=True, comment=metadata if save_metadata_image else None)
    else:
        Image.fromarray(img).save(local_temp_filename)

    html_name = os.path.join(os.path.dirname(local_temp_filename), 'log.html')

    if not os.path.exists(html_name):
        with open(html_name, 'a+', encoding='utf-8') as f:
            f.write(f"<p>Fooocus Log {date_string} (private)</p>\n")
            f.write(f"<p>All images do not contain any hidden data.</p>")

    with open(html_name, 'a+', encoding='utf-8') as f:
        div_name = only_name.replace('.', '_')
        f.write(f'<div id="{div_name}"><hr>\n')
        f.write(f"<p>{only_name}</p>\n")
        i = 0
        for k, v in dic:
            if i < single_line_number:
                f.write(f"<p>{k}: <b>{v}</b> </p>\n")
            else:
                if (i - single_line_number) % 2 == 0:
                    f.write(f"<p>{k}: <b>{v}</b>, ")
                else:
                    f.write(f"{k}: <b>{v}</b></p>\n")
            i += 1
        f.write(f"<p><img src=\"{only_name}\" width=512 onerror=\"document.getElementById('{div_name}').style.display = 'none';\"></img></p></div>\n")

        all_json_name = os.path.join(os.path.dirname(local_temp_filename), 'all.json')

        if not os.path.exists(all_json_name):
            with open(all_json_name, 'w', encoding='utf-8') as f:
                f.write('{"data": []}')

        with open(all_json_name, 'r', encoding='utf-8') as f:
            all_json = json.load(f)

        new_data = {
            "src": only_name,
        }
        new_data.update(dic)
        all_json["data"].append(new_data)
        with open(all_json_name, 'w', encoding='utf-8') as f:
            json.dump(all_json, f)
    
    print(f'Image generated with private log at: {html_name}')

    return
