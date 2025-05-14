# Project Setup Guide

## 🔧 Setting Up the Python Environment

This guide walks you through setting up a virtual environment and installing required packages from `requirements.txt`.

### 1. Create a Virtual Environment

#### Windows
```bash
python -m venv env
.\env\Scripts\activate
```

#### Linux/macOS
```bash
python3 -m venv env
source env/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### This is how to collect virtual environment packages to requirement.txt
### 3. Freeze Installed Packages
```bash
pip freeze > requirements.txt
```
