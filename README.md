<a name="top"></a><center>
<div align="center">
  <img src="https://i.postimg.cc/23Ryh4TH/re.png" alt="Researchr Logo" width="200">
  <h1>Researchr — MASv0</h1>
</div>

[![language](https://img.shields.io/badge/language-Python-239120)](https://learn.microsoft.com/ru-ru/dotnet/csharp/tour-of-csharp/overview)
[![OS](https://img.shields.io/badge/OS-linux%2C%20windows%2C%20macOS-0078D4)](https://docs.abblix.com/docs/technical-requirements)
[![CPU](https://img.shields.io/badge/CPU-x86%2C%20x64%2C%20ARM%2C%20ARM64-FF8C00)](https://docs.abblix.com/docs/technical-requirements)
[![Free](https://img.shields.io/badge/free_for_non_commercial_use-brightgreen)](#-license)
</center>

## Table of Contents
- [About](#-about)
- [What's New](#-whats-new)
- [How to use?](#-how-to-use)
- [Documentation](#-documentation)
- [Contacts](#%EF%B8%8F-contacts)

## 🚀 About

**Researchr** is a summarizer bot written in Python that is capable of summarizing texts from news/scientific papers. It adheres to high standards of flexibility, reusability, and reliability, utilizing well-known software design patterns, these patterns ensure the following benefits:

- **Modularity**: Different parts of the library can function independently, enhancing the library's modularity and allowing for easier maintenance and updates.
- **Maintainability**: Clear structure and separation facilitate better management of the codebase.

## ✨ What's New

### Version 0.0.2 (Latest)

🚀 **Features**
- Debugging phase.

✏️ **Improvements**
- "Feedback" added.

## 📝 How to use?


To use the bot, follow these steps:

**Open a terminal (Command Prompt or PowerShell for Windows, Terminal for macOS or Linux)**

**Ensure Git is installed**

**Visit https://git-scm.com to download and install console Git if not already installed**


**Clone the repository from GitHub**

```git clone https://github.com/mitternachtslaeufer/bot.news.git```


**Navigate to the project directory**

```cd bot.news```


**Setup a Virtual Environment, this keeps the project dependencies isolated from your main computer settings**

**Create the environment**

```python -m venv venv```


**Activate it (Windows)**

```.\venv\Scripts\activate```

**Activate it (macOS/Linux)**

```source venv/bin/activate```


**Once the environment is active, install the libraries required for the bot to work:**

**Use pip to install everything listed in requirements.txt**

```pip install -r requirements.txt```

**Execute the main script**

```python main.py```
Gemini đã nói

It looks like you're setting up a Python-based news bot! Based on your question "how to end a line in git," there are usually two things people mean: how to handle Line Endings (the invisible characters at the end of every line) or how to exit/save a commit message in the terminal.

Here is a quick breakdown of both:
1. Managing Line Endings (LF vs. CRLF)

Windows and Linux/macOS handle the "end" of a line differently. Windows uses Carriage Return + Line Feed (CRLF), while Unix-based systems use just Line Feed (LF). This often causes annoying "modified file" warnings in Git.

To fix this so Git handles it automatically for you, run this command in your terminal:

    On Windows:
    git config --global core.autocrlf true

    On macOS/Linux:
    git config --global core.autocrlf input

2. How to "End" or Exit a Git Commit

If you accidentally found yourself stuck in a text editor after typing git commit, here is how to get out:
Editor	How to Save and Exit
Vim (The default)	Press Esc, type :wq, and hit Enter.
Nano	Press Ctrl + O, then Enter (to save), then Ctrl + X (to exit).
VS Code	Simply close the tab or window where you wrote the message.
3. A Quick Note on your Setup

I noticed in your instructions you're using python main.py. Since you are using a virtual environment, always make sure your terminal prompt shows (venv) at the beginning of the line before running that command. If it doesn't, the pip install won't "stick" to the project.

Would you like me to help you create a .gitignore file for this project so you don't accidentally upload your venv folder to GitHub?
Bạn đã nói

in github I am writing a readme.md
Gemini đã nói

Since you are writing a README.md, "ending a line" usually refers to how you create line breaks so your text doesn't all run together in a single block when you view it on GitHub.

Markdown can be a bit picky—simply pressing Enter once often isn't enough to start a new line. Here are the three ways to handle it:
1. The Double Space (Soft Break)

If you want the text to start on a new line but stay in the same paragraph:

    Type two spaces at the end of the line.

    Then press Enter.

    Example:
    This is line one.[space][space]
    This is line two.

2. The Double Enter (Hard Break)

If you want to start a new paragraph with a visible gap between the lines:

    Press Enter twice.

    Example:
    This is paragraph one.

    This is paragraph two.

3. The <br> Tag (Manual Break)

If you need multiple line breaks in a row or want more control over the layout, you can use the HTML break tag:

    Type <br> at the end of your line.

    Example:
    I want a big gap here.


    Now I am further down.

Pro-Tip: Visualizing your README.md

Since you are working on the bot.news project, you can preview your changes locally if you use VS Code.

    Press Ctrl + Shift + V (Windows) or Cmd + Shift + V (Mac).

    This opens a split-screen preview so you can see if your line endings look right before you git push them.

Would you like me to generate a professionally formatted README template specifically for your Python news bot?
Bạn đã nói

┌──(venv)─(catmilk㉿catmilk)-[/mnt/storage/masv0]

└─$ pip install -r requirements.txt 

Collecting kivymd (from -r requirements.txt (line 2))

  Downloading kivymd-1.2.0.tar.gz (2.2 MB)

     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.2/2.2 MB 3.5 MB/s  0:00:00

  Installing build dependencies ... done

  Getting requirements to build wheel ... done

  Preparing metadata (pyproject.toml) ... done

Collecting kaki (from -r requirements.txt (line 3))

  Downloading kaki-0.1.9-py2.py3-none-any.whl.metadata (4.0 kB)

Collecting watchdog (from -r requirements.txt (line 4))

  Downloading watchdog-6.0.0-py3-none-manylinux2014_x86_64.whl.metadata (44 kB)

Collecting gspread (from -r requirements.txt (line 5))

  Downloading gspread-6.2.1-py3-none-any.whl.metadata (11 kB)

Collecting google-auth (from -r requirements.txt (line 6))

  Downloading google_auth-2.49.1-py3-none-any.whl.metadata (6.2 kB)

ERROR: Ignored the following versions that require a different python version: 0.10.6 Requires-Python <3.6,>=2.7; 0.10.7 Requires-Python <3.6,>=2.7

ERROR: Could not find a version that satisfies the requirement kivy_deps.sdl2 (from versions: none)

ERROR: No matching distribution found for kivy_deps.sdl2

                                                                                               

┌──(venv)─(catmilk㉿catmilk)-[/mnt/storage/masv0]

└─$ ls

app_fonts  app_textures  credentials.json  README.md         venv

app.kv     contents      main.py           requirements.txt

                                                                                               

┌──(venv)─(catmilk㉿catmilk)-[/mnt/storage/masv0]

└─$ python main.py                 

Traceback (most recent call last):

  File "/mnt/storage/masv0/main.py", line 2, in <module>

    from kivymd.app import MDApp

ModuleNotFoundError: No module named 'kivymd'

                                                                                               

┌──(venv)─(catmilk㉿catmilk)-[/mnt/storage/masv0]

└─$ 
Gemini đã nói

It looks like your installation hit a snag, catmilk. The error No module named 'kivymd' is happening because the pip install failed halfway through, so the libraries never actually got tucked into your venv.

The specific culprit is kivy_deps.sdl2. Here is the deal: those kivy_deps packages are Windows-only. Since your terminal shows you are on a Linux environment (likely WSL or a Linux distro based on the /mnt/storage/ path), you don't need them and they won't install.
🛠️ How to fix this

You need to clean up your requirements.txt and install the Linux-native dependencies.

1. Edit your requirements.txt
Open the file and remove any lines that look like these:

    kivy_deps.sdl2...

    kivy_deps.glew...

    kivy_deps.gstreamer...

2. Install Linux System Dependencies
Kivy/KivyMD on Linux needs some system-level libraries before pip can finish the job. Run this command:
Bash

sudo apt update && sudo apt install -y python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

3. Try the install again
Now that the system is ready, run the pip command again:
Bash

pip install -r requirements.txt

💡 Why did it fail?

When you see ERROR: No matching distribution found for kivy_deps.sdl2, it's basically Git/Pip saying, "I'm looking for a Windows tool, but I'm standing in a Linux room." Once you remove those Windows-specific lines, kivymd and kivy should install just fine on your current setup.

Would you like me to take a look at the full content of your requirements.txt to see if there's anything else that might cause a crash?
Bạn đã nói

I want my environment to use python 3.10

    2 yêu cầu thành công

Gemini đã nói

Since your terminal prompt shows you are in a Kali Linux environment (the (catmilk㉿catmilk) style), you likely already have multiple Python versions installed, but your virtual environment (venv) was probably created using the system default (which is usually 3.11 or 3.12 in newer Kali releases).

To force your environment to use Python 3.10, you need to recreate it while pointing specifically to that version.
1. Check if Python 3.10 is installed

First, see if it's already on your system:
Bash

python3.10 --version

    If it says "command not found": Install it using:
    sudo apt update && sudo apt install python3.10 python3.10-venv

2. Rebuild the Environment

You cannot "upgrade" an existing venv's Python version easily; it is cleaner to delete the old one and start fresh.

Step A: Deactivate and remove the old venv
Bash

deactivate
rm -rf venv

Step B: Create the new venv using Python 3.10
Bash

python3.10 -m venv venv

Step C: Activate it
Bash

source venv/bin/activate

3. Verify and Re-install

Once activated, verify the version:
Bash

python --version
# Should output: Python 3.10.x

Now, try running your install again (remembering to remove those Windows-specific kivy_deps lines from requirements.txt first as we discussed):
Bash

pip install -r requirements.txt

Why do this?

Using a specific version like 3.10 is a smart move for KivyMD projects, as some older libraries (like kaki or older versions of kivymd) sometimes struggle with the "strictness" of Python 3.11+.

Would you like me to help you double-check if there are any other version-sensitive libraries in your requirements.txt?
Bạn đã nói

┌──(catmilk㉿catmilk)-[/mnt/storage/masv0]

└─$ sudo apt install python3.10                 

Error: Unable to locate package python3.10

Error: Couldn't find any package by glob 'python3.10'
Gemini đã nói

It looks like Python 3.10 isn't in the default repositories for your current version of Kali Linux. Since Kali is a rolling release based on Debian Testing, it usually only keeps the very latest version (like 3.11 or 3.12) and drops the older ones.

To get 3.10 on Kali, you have two main options:
Option 1: The "DeadSnakes" PPA (Easiest)

While technically built for Ubuntu, the DeadSnakes PPA usually works on Debian-based systems like Kali.

    Install the software properties tool:
    sudo apt update && sudo apt install software-properties-common

    Add the repository:
    sudo add-apt-repository ppa:deadsnakes/ppa

    Update and Install:
    sudo apt update && sudo apt install python3.10 python3.10-venv

Option 2: Use pyenv (The Professional Choice)

If you're doing a lot of computer science or cybersecurity work, pyenv is a lifesaver. It lets you install any version of Python side-by-side without touching the system's "sacred" Python version.

    Install dependencies:
    sudo apt update && sudo apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git

    Install pyenv:
    curl https://pyenv.run | bash

    Install and set 3.10:
    pyenv install 3.10.13
    pyenv shell 3.10.13

⚠️ A Note for catmilk

Before you go through the trouble of installing 3.10, try running python3 --version.

If you have 3.11 or 3.12, KivyMD should still work perfectly fine as long as you fix that requirements.txt file (removing the kivy_deps Windows lines). Most people only "downgrade" to 3.10 if they hit a very specific bug with a library that hasn't been updated in years.

Would you like me to show you how to check if your current Python version can handle your requirements.txt without the 3.10 install?
Bạn đã nói

how to know that kivy_deps only for windoq
Gemini đã nói

You can tell kivy_deps is only for Windows by looking at the official Kivy documentation and the file names on the Python Package Index (PyPI).

Since you are a CS/Cybersecurity student at VGU/Saarland, checking these "under the hood" details is a great habit. Here is how you can verify it yourself:
1. Check the File Names (The "Wheel" Tags)

If you go to the PyPI page for kivy-deps.sdl2, look at the list of downloadable files. You will notice that every single file ends in -win_amd64.whl or -win32.whl.

    win = Windows

    amd64 = 64-bit architecture

    There are no files listed for manylinux (Linux) or macosx.

2. Official Kivy Documentation

The Kivy Installation Guide explicitly states:

    "kivy_deps.sdl2 is for window/images/audio and optionally OpenGL. It is only available on Windows and is included in the main Kivy wheel for other platforms."

3. Why Linux doesn't need it

On Kali Linux, instead of downloading a pre-packaged "dependency wheel" like kivy_deps, Kivy uses your system's native libraries. This is why I recommended running sudo apt install libsdl2-dev earlier. On Linux, the "glue" between Python and the hardware is handled by the OS package manager (apt), not by pip.
🛠️ Summary for your README.md

If you want to make your bot's README.md professional and cross-platform, you should split your installation instructions like this:

For Windows:
Bash

pip install kivy_deps.sdl2 kivy_deps.glew
pip install -r requirements.txt

For Linux (Kali):
Bash

sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
pip install -r requirements.txt

(And make sure your requirements.txt only contains the core libraries like kivy, kivymd, and gspread.)

Would you like me to help you rewrite your requirements.txt so it works on both Windows and Linux automatically?

    Yêu cầu thành công

Gemini đã nói

That table is the perfect evidence! It shows exactly how Kivy handles different environments.

Since you are on Kali Linux (the Penguin row 🐧), you should be looking at the "pip" and "PPA" installation methods. Notice that it does not mention kivy_deps because, as we found, those are "wheels" built specifically for the Windows row (the first row with the Windows logo 🪟).

To make your project cross-platform (so it works for you on Kali and for others on Windows), you can use environment markers in your requirements.txt. This is a pro-level way to handle dependencies.
🛠️ The "Universal" requirements.txt

Instead of having different files, you can tell pip to only install certain things if the user is on Windows:
Plaintext

kivymd==1.2.0
kaki
watchdog
gspread
google-auth
# These will ONLY install if the user is on Windows
kivy_deps.sdl2; sys_platform == 'win32'
kivy_deps.glew; sys_platform == 'win32'
kivy_deps.gstreamer; sys_platform == 'win32'

🚀 Next Steps for you on Kali:

Since you've already seen that python3.10 isn't in your current Kali repo, here is the fastest way to get your bot running right now:

    Modify your requirements.txt to remove (or comment out with #) the kivy_deps lines.

    Run the system-level install to give Kali the tools it needs to "build" Kivy:
    Bash

sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

Try the pip install again in your current venv:
Bash

    pip install -r requirements.txt

Would you like me to help you check which version of Python your current venv is actually using so we can be 100% sure it's compatible?
Bạn đã nói

<a name="top"></a><center>

<div align="center">

  <img src="https://i.postimg.cc/23Ryh4TH/re.png" alt="Researchr Logo" width="200">

  <h1>Researchr — MASv0</h1>

</div>


[![language](https://img.shields.io/badge/language-Python-239120)](https://learn.microsoft.com/ru-ru/dotnet/csharp/tour-of-csharp/overview)

[![OS](https://img.shields.io/badge/OS-linux%2C%20windows%2C%20macOS-0078D4)](https://docs.abblix.com/docs/technical-requirements)

[![CPU](https://img.shields.io/badge/CPU-x86%2C%20x64%2C%20ARM%2C%20ARM64-FF8C00)](https://docs.abblix.com/docs/technical-requirements)

[![Free](https://img.shields.io/badge/free_for_non_commercial_use-brightgreen)](#-license)

</center>


## Table of Contents

- [About](#-about)

- [What's New](#-whats-new)

- [How to use?](#-how-to-use)

- [Documentation](#-documentation)

- [Contacts](#%EF%B8%8F-contacts)


## 🚀 About


**Researchr** is a summarizer bot written in Python that is capable of summarizing texts from news/scientific papers. It adheres to high standards of flexibility, reusability, and reliability, utilizing well-known software design patterns, these patterns ensure the following benefits:


- **Modularity**: Different parts of the library can function independently, enhancing the library's modularity and allowing for easier maintenance and updates.

- **Maintainability**: Clear structure and separation facilitate better management of the codebase.


## ✨ What's New


### Version 0.0.2 (Latest)


🚀 **Features**

- Debugging phase.


✏️ **Improvements**

- "Feedback" added.


## 📝 How to use?


**To use the bot, follow these steps:**    

**Open a terminal (Command Prompt or PowerShell for Windows, Terminal for macOS or Linux)**  

**Ensure Git is installed**  

**Visit https://git-scm.com to download and install console Git if not already installed**  


**Clone the repository from GitHub**  

```git clone https://github.com/mitternachtslaeufer/bot.news.git```  


**Navigate to the project directory**  

```cd bot.news```  


**Setup a Virtual Environment, this keeps the project dependencies isolated from your main computer settings**  

**Create the environment**  

```python -m venv venv```  


**Activate it (Windows)**  

```.\venv\Scripts\activate```  

**Activate it (macOS/Linux)**  

```source venv/bin/activate```  


**Once the environment is active, install the libraries required for the bot to work:**  

**Use pip to install everything listed in requirements.txt**  

```pip install -r requirements.txt```  

**Execute the main script**  

```python main.py```  


## 📚 Documentation


### Getting Started

Explore the [Getting Started Guide]().


## 🗨️ Contacts


For more details about our products, services, or any general information, feel free to reach out to us. We are here to provide support and answer any questions you may have. Below are the best ways to contact our team:


- **Email**: Send us your inquiries or support requests at [104240034@student.vgu.edu.vn](mailto:104240034@student.vgu.edu.vn).


We look forward to assisting you and ensuring your experience with our products is successful and enjoyable!


[Back to top](#top)


write this again for linux and windows here is my requirements.txt

<a name="top"></a><center>

<div align="center">

  <img src="https://i.postimg.cc/23Ryh4TH/re.png" alt="Researchr Logo" width="200">

  <h1>Researchr — MASv0</h1>

</div>


[![language](https://img.shields.io/badge/language-Python-239120)](https://learn.microsoft.com/ru-ru/dotnet/csharp/tour-of-csharp/overview)

[![OS](https://img.shields.io/badge/OS-linux%2C%20windows%2C%20macOS-0078D4)](https://docs.abblix.com/docs/technical-requirements)

[![CPU](https://img.shields.io/badge/CPU-x86%2C%20x64%2C%20ARM%2C%20ARM64-FF8C00)](https://docs.abblix.com/docs/technical-requirements)

[![Free](https://img.shields.io/badge/free_for_non_commercial_use-brightgreen)](#-license)

</center>


## Table of Contents

- [About](#-about)

- [What's New](#-whats-new)

- [How to use?](#-how-to-use)

- [Documentation](#-documentation)

- [Contacts](#%EF%B8%8F-contacts)


## 🚀 About


**Researchr** is a summarizer bot written in Python that is capable of summarizing texts from news/scientific papers. It adheres to high standards of flexibility, reusability, and reliability, utilizing well-known software design patterns, these patterns ensure the following benefits:


- **Modularity**: Different parts of the library can function independently, enhancing the library's modularity and allowing for easier maintenance and updates.

- **Maintainability**: Clear structure and separation facilitate better management of the codebase.


## ✨ What's New


### Version 0.0.2 (Latest)


🚀 **Features**

- Debugging phase.


✏️ **Improvements**

- "Feedback" added.


## 📝 How to use?


**To use the bot, follow these steps:**    

**Open a terminal (Command Prompt or PowerShell for Windows, Terminal for macOS or Linux)**  

**Ensure Git is installed**  

**Visit https://git-scm.com to download and install console Git if not already installed**  


**Clone the repository from GitHub**  

```git clone https://github.com/mitternachtslaeufer/bot.news.git```  


**Navigate to the project directory**  

```cd bot.news```  


**Setup a Virtual Environment, this keeps the project dependencies isolated from your main computer settings**  

**Create the environment**  

```python -m venv venv```  


**Activate it (Windows)**  

```.\venv\Scripts\activate```  

**Activate it (macOS/Linux)**  

```source venv/bin/activate```  


**Once the environment is active, install the libraries required for the bot to work:**  

**Use pip to install everything listed in requirements.txt**  

```pip install -r requirements.txt```  

**Execute the main script**  

```python main.py```  


## 📚 Documentation


### Getting Started

Explore the [Getting Started Guide]().


## 🗨️ Contacts


For more details about our products, services, or any general information, feel free to reach out to us. We are here to provide support and answer any questions you may have. Below are the best ways to contact our team:


- **Email**: Send us your inquiries or support requests at [104240034@student.vgu.edu.vn](mailto:104240034@student.vgu.edu.vn).


We look forward to assisting you and ensuring your experience with our products is successful and enjoyable!


[Back to top](#top)
Gemini đã nói

Since you are building this for both Windows and Linux users (and currently working on it from Kali), we need to address those OS-specific dependencies directly in the guide to prevent others from hitting the same errors you did.

I have updated the "How to use?" section to include a clear split for system dependencies.

<a name="top"></a><center>

<div align="center">
<img src="https://i.postimg.cc/23Ryh4TH/re.png" alt="Researchr Logo" width="200">
<h1>Researchr — MASv0</h1>
</div>

</center>
Table of Contents

    About

    What's New

    How to use?

    Documentation

    Contacts

🚀 About

Researchr is a summarizer bot written in Python that is capable of summarizing texts from news/scientific papers. It adheres to high standards of flexibility, reusability, and reliability, utilizing well-known software design patterns, these patterns ensure the following benefits:

    Modularity: Different parts of the library can function independently, enhancing the library's modularity and allowing for easier maintenance and updates.

    Maintainability: Clear structure and separation facilitate better management of the codebase.

✨ What's New
Version 0.0.2 (Latest)

🚀 Features

    Debugging phase.
    ✏️ Improvements

    "Feedback" system implemented.

📝 How to use?
1. Prerequisites

    Install Git: Download from git-scm.com.

    Python 3.10+: Ensure Python is installed on your system.

2. Installation

Open your terminal and run the following:

Clone the repository
Bash

git clone https://github.com/mitternachtslaeufer/bot.news.git
cd bot.news

Setup a Virtual Environment
Bash

# Create the environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate

3. Install Dependencies

Before running the bot, you must install the specific system requirements for your OS to support the Kivy framework.
🐧 Linux (Ubuntu/Debian/Kali)
Bash

sudo apt update
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev
pip install -r requirements.txt

🪟 Windows
Bash

pip install kivy_deps.sdl2 kivy_deps.glew
pip install -r requirements.txt

4. Run the Bot
Bash

python main.py

📚 Documentation

Explore the Getting Started Guide.
🗨️ Contacts

    Email: 104240034@student.vgu.edu.vn

Back to top
💡 Pro-tip for your requirements.txt:

To make the file work for both OS types without crashing, edit your requirements.txt to look like this:
Plaintext

kivymd==1.2.0
kaki
watchdog
gspread
google-auth
# Windows-only dependencies
kivy_deps.sdl2; sys_platform == 'win32'
kivy_deps.glew; sys_platform == 'win32'

Would you like me to help you create a setup.sh script for Linux that automates all of this for your users?
Bạn đã nói

write in md format
Gemini đã nói

Here is the complete README.md file in Markdown format. I’ve incorporated the OS-specific fixes we discussed to ensure other users (or you, when switching between Windows and Kali) don't run into the same installation errors.
Markdown

<a name="top"></a><center>
<div align="center">
  <img src="https://i.postimg.cc/23Ryh4TH/re.png" alt="Researchr Logo" width="200">
  <h1>Researchr — MASv0</h1>
</div>

[![language](https://img.shields.io/badge/language-Python-239120)](https://www.python.org/)
[![OS](https://img.shields.io/badge/OS-linux%2C%20windows%2C%20macOS-0078D4)](https://docs.abblix.com/docs/technical-requirements)
[![CPU](https://img.shields.io/badge/CPU-x86%2C%20x64%2C%20ARM%2C%20ARM64-FF8C00)](https://docs.abblix.com/docs/technical-requirements)
[![Free](https://img.shields.io/badge/free_for_non_commercial_use-brightgreen)](#-license)
</center>

## Table of Contents
- [About](#-about)
- [What's New](#-whats-new)
- [How to use?](#-how-to-use)
- [Documentation](#-documentation)
- [Contacts](#%EF%B8%8F-contacts)

---

## 🚀 About

**Researchr** is a summarizer bot written in Python that is capable of summarizing texts from news/scientific papers. It adheres to high standards of flexibility, reusability, and reliability, utilizing well-known software design patterns. These patterns ensure the following benefits:

- **Modularity**: Different parts of the library can function independently, enhancing the library's modularity and allowing for easier maintenance and updates.
- **Maintainability**: Clear structure and separation facilitate better management of the codebase.

---

## ✨ What's New

### Version 0.0.2 (Latest)

🚀 **Features**
- Debugging phase.

✏️ **Improvements**
- "Feedback" system added for user interaction.

---

## 📝 How to use?

To get the bot running on your local machine, follow these steps:

### 1. Prerequisites
* **Git**: Install from [git-scm.com](https://git-scm.com/).
* **Python 3.10+**: Ensure Python is installed and added to your PATH.

### 2. Clone and Setup
Open your terminal (Command Prompt/PowerShell for Windows, Terminal for macOS/Linux) and run:

```bash
# Clone the repository
git clone [https://github.com/mitternachtslaeufer/bot.news.git](https://github.com/mitternachtslaeufer/bot.news.git)
cd bot.news

# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate
```
### 3. Install Requirements
Dependencies vary slightly depending on your Operating System.
🐧 Linux (Ubuntu/Debian/Kali)

You must install system-level SDL2 libraries before installing Python packages:
```bash
sudo apt update
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev
pip install -r requirements.txt
```
🪟 Windows
```bash
pip install kivy_deps.sdl2 kivy_deps.glew
pip install -r requirements.txt
```
### 4. Execute

Once the environment is active and libraries are installed, launch the bot:
```bash
python main.py
```
## 📚 Documentation

### Getting Started
Explore the [Getting Started Guide]().

## 🗨️ Contacts

For more details about our products, services, or any general information, feel free to reach out to us. We are here to provide support and answer any questions you may have. Below are the best ways to contact our team:

- **Email**: Send us your inquiries or support requests at [104240034@student.vgu.edu.vn](mailto:104240034@student.vgu.edu.vn).

We look forward to assisting you and ensuring your experience with our products is successful and enjoyable!

[Back to top](#top)
