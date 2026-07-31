import os
import shutil


SCREENSHOT_FOLDER = "screenshots"


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

            if (
                lower.endswith(".png")
                or lower.endswith(".jpg")
                or lower.endswith(".jpeg")
            ):

                if (
                    "screenshot" in lower
                    or "screen" in lower
                ):

                    source = os.path.join(
                        root,
                        file
                    )

                    destination = os.path.join(
                        output,
                        file
                    )

                    shutil.copy(
                        source,
                        destination
                    )

                    found.append(
                        destination
                    )


    return found
