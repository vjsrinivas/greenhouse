from subprocess import Popen

if __name__ == "__main__":
    DOCS = ["../devices/sensor/sht31d.py"]

    processes = []
    for doc in DOCS:
        proc = Popen(["lazydocs", doc, "--output-path", "./temp_doc/"])
        processes.append(proc)

    [proc.wait() for proc in processes]
