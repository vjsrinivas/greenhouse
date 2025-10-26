import os
import sys
from pathlib import Path
from subprocess import Popen
import shutil


if __name__ == "__main__":
    DOCS = [
        "../devices/sensor/sht31d.py",
        "../devices/sensor/camera.py",
        "../devices/sensor/soil.py",
        "../devices/sensor/tsl2591.py",
        "../devices/instrument/fan.py",  
        "../devices/instrument/heater.py",
        "../devices/instrument/light.py",
        "../devices/instrument/water.py",
        "../devices/database.py",  
    ]
    OUTPUT_DIR = "./api/"
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    MAIN_API_DOC = "./template/PROGRAMMING.md"
    OUTPUT_API_DOC = "./PROGRAMMING.md"
    IGNORE_CAPITALIZE = ["sht31d", "tsl2591"]
    processes = []
    for doc in DOCS:
        proc = Popen(["lazydocs", doc, "--output-path", OUTPUT_DIR])
        processes.append(proc)

    [proc.wait() for proc in processes]
    md_files = os.listdir(OUTPUT_DIR)
    md_files.sort()
    new_md_files = []

    for md_file in md_files:
        new_md_file = md_file.replace(".py", "")
        os.rename(
            os.path.join(OUTPUT_DIR, md_file),
            os.path.join(OUTPUT_DIR, new_md_file)
        )
        new_md_files.append(new_md_file)

    for md_file in new_md_files:
        full_md_file = os.path.join(OUTPUT_DIR, md_file)
        with open(full_md_file, "r") as f:
            contents = list(map(str.strip, f.readlines()))
        contents = contents[:-1]
    

    with open(MAIN_API_DOC, "r") as f:
        api_contents = f.readlines()
    api_call_idx = api_contents.index("{{API_DOC_APPLY}}")
    api_list = [Path(py_file).stem for py_file in new_md_files]    
    api_list = [py_file.capitalize() if not py_file in IGNORE_CAPITALIZE else py_file for py_file in api_list]
    api_links = [os.path.join(OUTPUT_DIR, _file) for _file in new_md_files]
    api_list = "\n".join([f"### [{py_file}]({api_links[i]})" for i,py_file in enumerate(api_list)])
    api_contents[api_call_idx] = api_list
    api_str_contents = "".join(api_contents)

    with open(OUTPUT_API_DOC, "w") as f:
        f.write(api_str_contents)