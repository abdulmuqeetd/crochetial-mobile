# Build the Crochetial Android APK

## Important
Buildozer is easiest on Linux/WSL. Windows desktop preview works with `python main.py`, but APK building should be done with WSL Ubuntu or GitHub Actions.

## Desktop run on Windows
Double click:

```text
run_app_windows.bat
```

Or run manually:

```bat
D:
cd "D:\1 AMD Data -25\Crochetial by Sadaf Muqeet\Crochetial App\Crochetial_App_Final\crochetial_mobile"
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python main.py
```

## APK build with WSL Ubuntu
Install WSL Ubuntu from Microsoft Store, then open Ubuntu and run:

```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
python3 -m pip install --user --upgrade pip buildozer cython==0.29.36
cd /mnt/d/1\ AMD\ Data\ -25/Crochetial\ by\ Sadaf\ Muqeet/Crochetial\ App/Crochetial_App_Final/crochetial_mobile
~/.local/bin/buildozer -v android debug
```

Your APK will be here:

```text
crochetial_mobile/bin/crochetial-0.1.0-arm64-v8a-debug.apk
```

## Install APK on Android phone
1. Copy the APK to your phone.
2. Open it on your phone.
3. Allow installation from unknown sources.
4. Install.

## Release APK / Play Store
For Play Store, build a release AAB/APK and sign it with a keystore. Ask me when you reach this step.
