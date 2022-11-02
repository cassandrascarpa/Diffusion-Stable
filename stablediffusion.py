import base64
import os
import random
import requests
import string
import tkinter
import threading
import time

from io import BytesIO
from PIL import Image, ImageTk

# ---------- SETTINGS  ----------

host = 'http://gpu1.local:9000'
path = '/api/predict/'

save_generated_images = True
output_dir = "out/"
# Load existing images
saved_dir = "saved/"
saved_filename_pattern = "generated_{}.png"

base_image = "horse.jpeg"
mask_image = "mask.png"

# TODO make these the same without taking forever to generate
height = 512
width = 512
screenwidth = 1920
screenheight = 1800

prompt = "medium-size short robotic (((((horse))))) standing on four legs facing towards the camera, futuristic, steampunk, (((cyberpunk))), sci-fi, lights"
negative_prompt = "off-center, long, (((tall))), huge, hiding, obscured, off-screen, outdoors, window, tree, city, background, human, person, rider, toy, abstract, platform, jumping, fence, gate"

mode_inpaint = 1
method = "Heun"
sampling_steps = 30
cfg_scale = 23
denoising_strength = 0.9
mask_blur = 30
inpaint_full_res = False
padding = 32
mask_type = "Draw mask"
masked_content = "fill"
resize = "Just resize"
inpaint = "Inpaint masked"
batch_count = 1
batch_size = 1
style1 = "None"
style2 = "None"
seed = -1

# ---------- VARS  ----------

fn_index_init = 59
fn_index_generate = 75

false = False
true = True
null = None

saved_count = len(os.listdir(saved_dir))

session_hash = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(11))

with open(base_image, "rb") as f:
    base_image_b64 = base64.b64encode(f.read()).decode('utf-8')

with open(mask_image, "rb") as f:
    mask_image_b64 = base64.b64encode(f.read()).decode('utf-8')

image_data = {
    "image":"data:image/jpeg;base64," + base_image_b64,
    "mask":"data:image/png;base64," + mask_image_b64
    }

req_init = {"fn_index":fn_index_init,"data":[],"session_hash":session_hash}
req_generate = {
    "fn_index":fn_index_generate,
    "data":[
        mode_inpaint,
        prompt,
        negative_prompt,
        style1, style2,
        null,
        image_data,
        null,null,
        mask_type,
        sampling_steps,
        method,
        mask_blur,
        masked_content,
        false, false,
        1,
        1,
        cfg_scale,
        denoising_strength,
        seed,
        -1,
        0,0,0,
        false,
        width,
        height,
        resize,
        inpaint_full_res,
        padding,
        inpaint,
        # Abandon all hope, ye who enter here
        "",
        "",
        "None",
        0.9,
        5,
        "0.0001",
        false,
        "None",
        "",
        0.1,
        false,false,
        "<p style=\"margin-bottom:0.75em\">Render these video formats:</p>","<p style=\"margin-bottom:0.75em\">Animation Parameters</p>",
        "<p style=\"margin-bottom:0.75em\">Prompt Template, applied to each keyframe below</p>",
        "<p style=\"margin-bottom:0.75em\">Keyframe Format: <br>Time (s) | Desnoise | Zoom (/s) | X Shift (pix/s) | Y shift (pix/s) | Positive Prompts | Negative Prompts | Seed</p>",
        "10.0",
        "15",
        false,false,true,
        "1.0",
        "","","",
        0.4,
        "0","0",
        false,false,
        0.1,
        0.5,
        "\n            <h3><strong>Variations</strong></h3>\n            Choose exactly one term from the list\n            <code>{summer|autumn|winter|spring}</code>\n            <br/><br/>\n\n            <h3><strong>Combinations</strong></h3>\n            Choose a number of terms from a list, in this case we choose two artists\n            <code>[2$$artist1|artist2|artist3]</code>\n            <br/><br/>\n\n            <h3><strong>Wildcards</strong></h3>\n            <p>Available wildcards</p>\n            <ul>\n        </ul>\n            <br/>\n            <code>WILDCARD_DIR: scripts/wildcards</code><br/>\n            <small>You can add more wildcards by creating a text file with one term per line and name is mywildcards.txt. Place it in scripts/wildcards. <code>__mywildcards__</code> will then become available.</small>\n        ",
        "<ul>\n<li><code>CFG Scale</code> should be 2 or lower.</li>\n</ul>\n",
        true,true,
        "","",
        true,
        50,
        true,
        1,0,
        false,
        4,
        1,
        4,
        0.09,
        true,
        1,0,7,
        false,false,
        "<p style=\"margin-bottom:0.75em\">Recommended settings: Sampling Steps: 80-100, Sampler: Euler a, Denoising strength: 0.8</p>",
        128,
        8,
        ["left","right","up","down"],
        1,
        0.05,
        128,4,
        "fill",
        ["left","right","up","down"],
        false,false,null,
        "",
        "<p style=\"margin-bottom:0.75em\">Will upscale the image to twice the dimensions; use width and height sliders to set tile size</p>",
        64,
        "None",
        false,
        4,
        "",
        10,
        false,false,true,
        30,
        true,false,
        10,
        true,
        30,
        true,
        "svg",
        true,true,false,
        0.5,
        "","",
        24,
        "24",
        "hh:mm:ss","hh:mm:ss",
        false,
        "",
        24,24,3,15,
        "00:00:00","00:00:00",
        false,
        "",
        1,
        10,
        true,
        1,
        false,
        1,0,0,
        "Seed","",
        "Nothing","",true,false,false,null,
        "{\"prompt\": \"medium-size short robotic (((((horse))))) standing on four legs facing towards the camera, futuristic, steampunk, (((cyberpunk))), sci-fi, lights\", \"all_prompts\": [\"medium-size short robotic (((((horse))))) standing on four legs facing towards the camera, futuristic, steampunk, (((cyberpunk))), sci-fi, lights\"], \"negative_prompt\": \"off-center, long, (((tall))), huge, hiding, obscured, off-screen, outdoors, window, tree, city, background, human, person, rider, toy, abstract, platform, jumping, fence, gate\", \"seed\": 2634139638, \"all_seeds\": [2634139638], \"subseed\": 2660122970, \"all_subseeds\": [2660122970], \"subseed_strength\": 0, \"width\": 512, \"height\": 512, \"sampler_index\": 3, \"sampler\": \"Heun\", \"cfg_scale\": 23, \"steps\": 30, \"batch_size\": 1, \"restore_faces\": false, \"face_restoration_model\": null, \"sd_model_hash\": \"7460a6fa\", \"seed_resize_from_w\": 0, \"seed_resize_from_h\": 0, \"denoising_strength\": 0.9, \"extra_generation_params\": {\"Mask blur\": 30}, \"index_of_first_image\": 0, \"infotexts\": [\"medium-size short robotic (((((horse))))) standing on four legs facing towards the camera, futuristic, steampunk, (((cyberpunk))), sci-fi, lights\\nNegative prompt: off-center, long, (((tall))), huge, hiding, obscured, off-screen, outdoors, window, tree, city, background, human, person, rider, toy, abstract, platform, jumping, fence, gate\\nSteps: 30, Sampler: Heun, CFG scale: 23, Seed: 2634139638, Size: 512x512, Model hash: 7460a6fa, Denoising strength: 0.9, Clip skip: 2, Mask blur: 30\"], \"styles\": [\"None\", \"None\"], \"job_timestamp\": \"20221028203853\", \"clip_skip\": 2}","<p>medium-size short robotic (((((horse))))) standing on four legs facing towards the camera, futuristic, steampunk, (((cyberpunk))), sci-fi, lights<br>\nNegative prompt: off-center, long, (((tall))), huge, hiding, obscured, off-screen, outdoors, window, tree, city, background, human, person, rider, toy, abstract, platform, jumping, fence, gate<br>\nSteps: 30, Sampler: Heun, CFG scale: 23, Seed: 2634139638, Size: 512x512, Model hash: 7460a6fa, Denoising strength: 0.9, Clip skip: 2, Mask blur: 30</p><div class='performance'><p class='time'>Time taken: <wbr>5.16s</p><p class='vram'>Torch active/reserved: 3354/3714 MiB, <wbr>Sys VRAM: 4972/24220 MiB (20.53%)</p></div>"],
        "session_hash":session_hash
}

# ---------- GUI ----------

def showFullScreen(img):
    win = tkinter.Tk()
    win.geometry("%dx%d+0+0" % (screenwidth, screenheight))   
    win.wm_attributes('-fullscreen', 'True')
    win.bind("<Escape>", lambda event:win.destroy())
    canvas = tkinter.Canvas(win,width=screenwidth,height=screenheight)
    canvas.pack()
    canvas.configure(background='black')
    canvas.create_image(screenwidth/2,screenheight/2,image=ImageTk.PhotoImage(img))
    win.mainloop()

# ---------- HORSE CODE  ----------

def json_to_string(j):
    vals = list(j.values())
    return "={},".join(j.keys()).format(*vals) + "={}".format(vals[-1])

def display_saved_horse():
    horse_num = random.randint(1,saved_count)
    horse_file = saved_dir + saved_filename_pattern.format(horse_num)
    if not(os.path.isfile(horse_file)):
        print("Couldn't find horse "+horse_file)
        return
    im = Image.open(horse_file)
    showFullScreen(im)

def diffuse_horse(s, stability):
    if stability == 1:
        display_saved_horse()
        return

    s.post(host+path, json = req_init)
    resp_generate = s.post(host+path, json = req_generate)
    resp_json = resp_generate.json()
    generated_file_path = resp_json['data'][0][0]['name']

    resp_img = s.get(host+"/file="+generated_file_path)
    im = Image.open(BytesIO(resp_img.content))
    showFullScreen(im)

    with open("out/"+generated_file_path.split("/")[-1], 'wb') as f:
        f.write(resp_img.content)

sess = requests.Session()
while True:
    user_input = input("Choose stability level (1-10): ")
    if user_input == "quit":
        break
    if not(user_input.isdigit()):
         print("Invalid stability level")
         continue
    stability = int(user_input)
    if stability < 1 or stability > 10:
        print("Invalid stability level")
        continue
    print("Diffusing horse at stability level {}".format(stability))
    try:
        diffuse_horse(sess, stability)
    except:
        print("An error occurred, retrying...")

# stability ideas!!!!!!!!!!!

# level 0 = live generate horse with random partial mask
# level 1 = pre-generated horse with random partial mask
# level 2 = live generate horse with horse mask
# level 3 - pre-generated horse with horse mask
# level 4 = live generate horse with full mask
# level 5 - pre-generated horse with full mask

# level 0,1 - very high probability of weird wordlist in positive/negative prompts
# level 2,3 - medium probabiliby of weird wordlsit in positive/negative prompts
# level 4,5 - very low probabiliby of weird wordlist in positive/negative prompts

# Animator? Other scripts?