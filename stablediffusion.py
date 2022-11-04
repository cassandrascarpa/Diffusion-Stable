import base64
import json
import math
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

host = 'http://gpu1.local:7860'
path = '/sdapi/v1/img2img'

save_generated_images = True
output_dir = "out/"
# Load existing images
saved_dir = "saved/"
saved_filename_pattern = "generated_{}.png"

base_image = "horse.jpeg"
stable_wordlist = "stable_wordlist.txt"
unstable_wordlist = "unstable_wordlist.txt"
height = 896
width = 960
screenwidth = 1920
screenheight = 1792

prompt = "medium-size short robotic (((((horse))))) standing on four legs facing towards the camera, futuristic, steampunk, (((cyberpunk))), sci-fi, lights"
negative_prompt = "off-center, long, (((tall))), huge, hiding, obscured, off-screen, outdoors, window, tree, city, background, human, person, rider, toy, abstract, platform, jumping, fence, gate"

mode_inpaint = 1
method = "Heun"
sampling_steps = 30
cfg_scale = 23
#denoising_strength = 0.9
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

with open(base_image, "rb") as f:
    base_image_b64 = base64.b64encode(f.read()).decode('utf-8')

with open(stable_wordlist) as sw:
    stable_words = [line.rstrip() for line in sw]

with open(unstable_wordlist) as uw:
    unstable_words = [line.rstrip() for line in uw]

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
    im.show()
    #showFullScreen(im)

def generate_request(stability):
    req = {
        "init_images": ["data:image/jpeg;base64," + base_image_b64],
        "prompt":generate_prompt(stability),
        "sampler_index": method,
        "steps": sampling_steps,
        "denoising_strength": denoising_strength(stability),
        "cfg_scale": cfg_scale,
        "height":height,
        "width":width,
        "inpaint_full_res":inpaint_full_res,
        "resize_method":resize,
    }
    return req

def generate_prompt(stability):
    prompt = []
    num_stable_words = math.ceil(stability/2)
    num_unstable_words = math.ceil((10-stability)/2)
    for _ in range(num_stable_words):
        prompt.append(random.choice(stable_words))
    for _ in range(num_unstable_words):
        prompt.append(random.choice(unstable_words))
    return ",".join(prompt)

def denoising_strength(stability):
    if stability == 10:
        return 0
    elif stability == 9:
        return 0.1
    elif stability == 8:
        return 0.2
    elif stability == 7:
        return 0.3
    elif stability > 5:
        return 0.35
    elif stability > 2:
        return 0.38
    elif stability < 3 and stability > 0:
        return 0.4
    else:
        return 0.45

def diffuse_horse(s, stability):
    req = generate_request(stability)
    resp_generate = s.post(host+path, json.dumps(req))
    resp_json = resp_generate.json()
    resp_img = resp_json['images'][0]
    resp_img_content = base64.b64decode(resp_img)

    im = Image.open(BytesIO(resp_img_content))
    im.show()
    #im_large = im.resize((screenwidth, screenheight), resample=Image.BOX)
    #im_large.show()
    #showFullScreen(im)

    generated_file_path = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(11)) + ".png"
    with open("out/"+generated_file_path.split("/")[-1], 'wb') as f:
        f.write(resp_img_content)

sess = requests.Session()
saved_count = len(os.listdir(saved_dir))
while True:
    user_input = input("Choose stability level (1-10): ")
    if user_input == "quit":
        break
    if user_input == "saved":
        display_saved_horse()
        continue
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