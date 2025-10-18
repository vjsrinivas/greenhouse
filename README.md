# Greenhouse Application
**Description:** This implementation is an official Python-only codebase for automating greenhouse mechanisms

## Quick Start (Python Program) 🚀
This repository has only been tested on the Raspberry Pi 5, which contains a UNIX-style operating system. 

Create and activate a Python virtual environment with `venv`:
```bash
# Assuming you are in $HOME
python3 -m venv greenhouse_env # Generate virtual environment at current path
source greenhouse_env/bin/activate # Activate environment
```

Install all prerequisite Python packages from this repo's `requirements.txt`:
```bash
# Assuming you changed directories to the root folder of this repository
pip install -r requirements.txt
```

Start the greenhouse service (production):
```bash
cd services
bash setup.sh
```

Start the main program by simply running `main.py` (debugging):
```bash
python main.py # or python3 main.py based on Python installation type
```

## Documentation 📚
To construct, program, and run the greenhouse, it is highly recommended you to read the [DOCS](DOCS.md).