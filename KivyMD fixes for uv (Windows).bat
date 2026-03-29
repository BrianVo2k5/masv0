@echo off

echo Building KivyMD wheel...
pip wheel kivymd==1.2.0 --no-deps

echo Installing KivyMD from binary...
uv pip install kivymd==1.2.0 --only-binary kivymd

echo Installing the rest of the project dependencies...
uv pip install -e .