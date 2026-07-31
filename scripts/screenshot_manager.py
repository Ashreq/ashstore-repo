import os
import shutil


SCREENSHOT_FOLDER = "screenshots"

MAX_SCREENSHOTS = 8


IGNORE_WORDS = [
    "icon",
    "logo",
    "appstore",
    "launch",
    "launchimage",
    "play",
    "pause",
    "volume",
    "close",
    "delete",
    "add",
    "arrow",
    "button",
    "background",
    "bg",
    "header",
    "footer",
    "slider",
    "cast",
    "hardware",
    "ticket"
]


def is_screenshot(filename):

    lower = filename.lower()


    if not (
        lower.endswith(".png")
        or lower.endswith(".jpg")
        or lower.endswith(".jpeg")
    ):
        return False


    for word in IGNORE_WORDS:

        if word in lower:
            return False


    return True



def save_screenshots(app_path, bundle_id):

    output = os.path.join(
        SCREENSHOT_FOLDER,
        bundle_id
    )


    os.makedirs(
        output,
        exist_ok=True
    )


    found = []


    for root, dirs, files in os.walk(app_path):

        for file in files:

            if len(found) >= MAX_SCREENSHOTS:
                break


            if is_screenshot(file):

                source = os.path.join(
                    root,
                    file
                )


                destination = os.path.join(
                    output,
                    file
                )


                if not os.path.exists(destination):

                    shutil.copy(
                        source,
                        destination
                    )


                found.append(
                    destination
                )


        if len(found) >= MAX_SCREENSHOTS:
            break


    return found



def get_screenshot_urls(files, repo):

    urls = []


    for file in files:

        name = os.path.basename(
            file
        )

        folder = os.path.basename(
            os.path.dirname(file)
        )


        urls.append(
            f"https://raw.githubusercontent.com/{repo}/main/screenshots/{folder}/{name}"
        )


    return urls
