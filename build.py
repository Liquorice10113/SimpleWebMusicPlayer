import jinja2
import os, shutil
import hashlib

from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import io
from PIL import Image


def extract_mp3_info(file_path):
    # Load the MP3 file
    audio = MP3(file_path, ID3=ID3)
    tags = ID3(file_path)

    fn = os.path.split(file_path)[-1]
    artist = "Unknown Artist"
    title = fn
    if " - " in fn:
        artist, title, *_ = fn.split(" - ")
    # Extract title and artist
    title = audio.get("TIT2", title)
    artist = audio.get("TPE1", artist)

    # Extract cover image
    cover_image = None
    APIC = tags.getall("APIC")
    if APIC and len(APIC) > 0:
        cover = APIC[0].data
        cover_image = Image.open(io.BytesIO(cover))

    return {"title": str(title), "artist": str(artist), "cover_image": cover_image}


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


shutil.rmtree("build")

if not os.path.exists("build"):
    os.mkdir("build")
if not os.path.exists("build/m"):
    os.mkdir("build/m")

# Copy mp3s
print("Copy music files...")

mp3_list = []
for i in os.listdir("files"):
    if i.lower().endswith("mp3"):
        shutil.copy("files/" + i, "build/m/" + get_md5(i) + ".mp3")
        # Example usage
        info = extract_mp3_info("files/" + i)

        print(f"Title: {info['title']}")
        print(f"Artist: {info['artist']}")

        if info["cover_image"]:
            img_path = "m/" + get_md5(i) + ".jpg"
            info["cover_image"].save("build/" + img_path)
        else:
            img_path = "default.jpg"
            print("No cover image found")

        mp3_list.append(
            ("m/" + get_md5(i) + ".mp3", img_path, info["title"], info["artist"])
        )

if len(mp3_list) == 0:
    print("No music file found!")
    exit(1)

# Render template
print("Render web page...")

with open("res/template.html", "r") as f:
    template_s = f.read()


render_result = jinja2.Template(template_s).render(mp3s=mp3_list)
with open("build/index.html", "w") as f:
    f.write(render_result)


# Copy resource files
print("Copy resource files...")

shutil.copy("res/style.css", "build/style.css")
# shutil.copy("res/jsmediatags.min.js", "build/jsmediatags.min.js")
shutil.copy("res/segoe-ui.ttf", "build/segoe-ui.ttf")
shutil.copy("res/default.jpg", "build/default.jpg")

print("OK")