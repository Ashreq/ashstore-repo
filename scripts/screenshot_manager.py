import os
import shutil


SCREENSHOT_FOLDER = "screenshots"


IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg"
)


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

            lower = file.lower()

            if lower.endswith(IMAGE_EXTENSIONS):

                source = os.path.join(
                    root,
                    file
                )


                destination = os.path.join(
                    output,
                    file
                )


                # avoid duplicate names
                if not os.path.exists(destination):

                    shutil.copy2(
                        source,
                        destination
                    )


                found.append(
                    destination
                )


    return found



def get_screenshot_urls(files, repo):

    urls = []


    for file in files:

        filename = os.path.basename(file)


        bundle = os.path.basename(
            os.path.dirname(file)
        )


        urls.append(
            f"https://raw.githubusercontent.com/{repo}/main/screenshots/{bundle}/{filename}"
        )


    return urls
