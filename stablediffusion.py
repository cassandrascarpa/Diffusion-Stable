import base64
import glob
import json
import math
import os
import random
import requests
import string
import threading
import time
import tkinter

from io import BytesIO
from PIL import Image, ImageTk

# ---------- SETTINGS  ----------

host_primary = 'http://gpu1.local:7860'
host_alt = 'http://192.168.1.166:7860'
host = host_primary

path = '/sdapi/v1/img2img'

live_generation = True
interactive = True
fullscreen = False
tth = 3 # time to horse

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
screenwidth = width #1920
screenheight = height #1088

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

# ---------- HORSE CODE  ----------
img = None
canvas = None
label = None
horse_container = None
horse_info = None
stability = 10
generation_time = tth

with open(base_image, "rb") as f:
    base_image_b64 = base64.b64encode(f.read()).decode('utf-8')

with open(stable_wordlist) as sw:
    stable_words = [line.rstrip() for line in sw]

with open(unstable_wordlist) as uw:
    unstable_words = [line.rstrip() for line in uw]

def json_to_string(j):
    vals = list(j.values())
    return "={},".join(j.keys()).format(*vals) + "={}".format(vals[-1])

def update_image(newhorse):
   global img
   im_large = newhorse.resize((screenwidth, screenheight), resample=Image.BOX)
   img = ImageTk.PhotoImage(im_large)
   canvas.itemconfig(horse_container,image=img)

def update_info():
    global stability
    global generation_time
    canvas.itemconfig(horse_info,text="Generation time: {}s\nStability: {}/10".format(generation_time, stability))

def display_saved_horses():
    global stability
    while True:
        stability_dir = "/level_{}/".format(stability)
        dir_contents = glob.glob(saved_dir + stability_dir + "*.png")
        horse_file = random.choice(dir_contents)
        if not(os.path.isfile(horse_file)):
            print("Couldn't find horse "+horse_file)
            continue
        im = Image.open(horse_file)
        update_image(im)
        time.sleep(tth)
        break

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
    num_stable_words = math.ceil(stability/2) + 1
    num_unstable_words = math.ceil((10-stability)/2)
    if stability < 4:
        num_unstable_words += 1
    for _ in range(num_stable_words):
        prompt.append(random.choice(stable_words))
    for _ in range(num_unstable_words):
        prompt.append(random.choice(unstable_words))
    return ",".join(prompt)

def denoising_strength(stability):
    if stability == 10:
        return 0
    elif stability == 9:
        return 0.2
    elif stability == 8:
        return 0.3
    elif stability > 5:
        return 0.38
    elif stability > 2:
        return 0.42
    elif stability > 0:
        return 0.45
    else:
        return 0.48

def diffuse_horse(s, stability):
    req = generate_request(stability)
    resp_generate = s.post(host+path, json.dumps(req))
    resp_json = resp_generate.json()
    resp_img = resp_json['images'][0]
    resp_img_content = base64.b64decode(resp_img)

    im = Image.open(BytesIO(resp_img_content))
    update_image(im)

    if save_generated_images:
        generated_file_path = "level_{}/".format(stability) + ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8)) + ".png"
        with open("out/"+generated_file_path, 'wb') as f:
            f.write(resp_img_content)

def diffuser():
    global generation_time
    sess = requests.Session()
    last_horse_time = time.time()
    while True:
        try:
            diffuse_horse(sess, stability)
            now = time.time()
            generation_time = math.ceil(now - last_horse_time)
            last_horse_time = now
            update_info()
        except:
            print("An error occurred, retrying...")
        time.sleep(tth)

def destabilizer():
    global generation_time
    global stability
    while True:
        stability = random.randint(0,10)
        update_info()
        time.sleep(generation_time + 2*tth)

def repl():
    global stability
    while True:
        user_input = input("Choose stability level (0-10): ")
        if not(user_input.isdigit()):
            print("Invalid stability level")
            continue
        stability = int(user_input)
        if stability < 0 or stability > 10:
            print("Invalid stability level")
            continue
        update_info()

def main():
    global img
    global canvas
    global horse_container
    global horse_info
    win = tkinter.Tk()
    win.geometry("%dx%d+0+0" % (screenwidth, screenheight))
    if fullscreen:   
        win.wm_attributes('-fullscreen', 'True')
    win.bind("<Escape>", lambda event:win.destroy())
    canvas = tkinter.Canvas(win,width=screenwidth,height=screenheight)
    canvas.pack()
    canvas.configure(background='black')
    initial = Image.open(BytesIO(base64.b64decode(base_image_b64)))
    im_large = initial.resize((screenwidth, screenheight), resample=Image.BOX)
    img = ImageTk.PhotoImage(im_large)
    horse_container = canvas.create_image(screenwidth/2,screenheight/2,image=img)
    horse_info = canvas.create_text(10,30, text="", fill="white", font=('Helvetica 15 bold'), anchor = 'w')
    update_info()

    if interactive:
        t1 = threading.Thread(target=repl)
        
    else:
        t1 = threading.Thread(target=destabilizer)

    if live_generation:
        t2 = threading.Thread(target=diffuser)
    else:
        t2 = threading.Thread(display_saved_horses)

    t1.setDaemon(True)
    t1.start()
    t2.setDaemon(True)
    t2.start()
    
    win.mainloop()

if __name__ == "__main__":
    main()

# ---------- TODOS are back and they're better than ever -------------
# Set stability level with hardware
# Make sure everything works on the pi
# Backups: have another sd instance to fall back on, sets of saved images, etc
