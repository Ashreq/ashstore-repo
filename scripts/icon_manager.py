import os
import shutil


ICON_FOLDER = "icons"


def find_icon(app_path, plist):

    if not os.path.exists(app_path):
        return None


    icon_names = []


    bundle_icons = plist.get(
        "CFBundleIcons",
        {}
    )


    primary_icon = bundle_icons.get(
        "CFBundlePrimaryIcon",
        {}
    )


    icon_names.extend(
        primary_icon.get(
            "CFBundleIconFiles",
            []
        )
    )


    icon_names.extend(
        plist.get(
            "CFBundleIconFiles",
            []
        )
    )


    icon_names.extend([
        "AppIcon60x60@3x.png",
        "AppIcon60x60@2x.png",
        "AppIcon.png",
        "Icon.png"
    ])


    files = os.listdir(
        app_path
    )


    for icon in icon_names:

        clean_name = icon.replace(
            ".png",
            ""
        )


        for file in files:

            if file.startswith(
                clean_name
            ):

                return os.path.join(
                    app_path,
                    file
                )


    # fallback: search any png icon

    for file in files:

        if file.lower().endswith(".png"):

            return os.path.join(
                app_path,
                file
            )


    return None



def save_icon(icon_path, bundle_id):

    if not icon_path:
        return None


    os.makedirs(
        ICON_FOLDER,
        exist_ok=True
    )


    filename = (
        bundle_id.replace(
            ".",
            "_"
        )
        +
        ".png"
    )


    destination = os.path.join(
        ICON_FOLDER,
        filename
    )


    shutil.copy(
        icon_path,
        destination
    )


    return filename



def get_icon_url(filename, repository):

    if not filename:
        return None


    return (
        "https://raw.githubusercontent.com/"
        f"{repository}/main/icons/{filename}"
    )
