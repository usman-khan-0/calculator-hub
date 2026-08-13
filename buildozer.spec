[app]

presplash.filename = %(source.dir)s/assets/images/presplash.png
icon.filename = %(source.dir)s/assets/icons/icon.png

# (str) Title of your application
title = Calculator Hub

# (str) Package name
package.name = calculatorhub

# (str) Package domain (needed for android/ios packaging)
package.domain = org.calculatorhub

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json

# (list) List of directories to exclude from the build
source.exclude_dirs = tests, .git, .pytest_cache, bin, .buildozer, __pycache__

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# fetch python-for-android recipes for these
# Python 3.11 is used for compatibility with Python-for-Android and pip
requirements = python3.11,kivy==2.3.1,pillow

# (str) Presplash / icon (place real assets under assets/icons and assets/images,
# then point these paths at them)
# presplash.filename = %(source.dir)s/assets/images/presplash.png
# icon.filename = %(source.dir)s/assets/icons/icon.png

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# ---------------------------------------------------------------------------
# ANDROID SPECIFIC
# ---------------------------------------------------------------------------

# (list) Permissions
# Calculator Hub works fully offline and stores all data locally, so no
# network, storage, or other sensitive permissions are requested.
android.permissions =

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 28

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) The Android arch to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (int) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Automatically accept SDK license agreements.
android.accept_sdk_license = True

# (str) The format used to package the app for release mode (aab or apk).
android.release_artifact = aab

# (str) The format used to package the app for debug mode (apk or aab).
android.debug_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

# (str) Path to build artifact storage
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin
