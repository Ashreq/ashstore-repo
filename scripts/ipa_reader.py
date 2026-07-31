import os
import zipfile
import plistlib
import tempfile
import shutil


def extract_ipa(ipa_path):

    temp_dir = tempfile.mkdtemp()

    with zipfile.ZipFile(ipa_path, "r") as archive:
        archive.extractall(temp_dir)

    payload_path = os.path.join(
        temp_dir,
        "Payload"
    )

    app_path = None

    for root, dirs, files in os.walk(payload_path):

        for item in dirs:

            if item.lower().endswith(".app"):

                app_path = os.path.join(
                    root,
                    item
                )

                break

        if app_path:
            break


    if not app_path:

        shutil.rmtree(temp_dir)

        raise Exception(
            "No .app folder found in IPA"
        )


    return temp_dir, app_path



def read_plist(app_path):

    plist_path = os.path.join(
        app_path,
        "Info.plist"
    )


    with open(plist_path, "rb") as file:

        return plistlib.load(file)



def detect_developer_name(plist):

    # Try common developer fields

    developer = (
        plist.get("artistName")
        or plist.get("developerName")
        or plist.get("SellerName")
        or plist.get("TeamName")
    )


    if developer:

        return developer


    # Fallback using bundle identifier

    bundle = plist.get(
        "CFBundleIdentifier",
        ""
    )


    if bundle:

        parts = bundle.split(".")


        if len(parts) >= 2:

            return (
                parts[1]
                .replace("-", " ")
                .title()
            )


    return "Unknown"



def read_ipa_info(ipa_path):

    temp_dir, app_path = extract_ipa(
        ipa_path
    )


    try:

        plist = read_plist(
            app_path
        )


        return {

            "name":
                plist.get(
                    "CFBundleDisplayName",
                    plist.get(
                        "CFBundleName",
                        "Unknown"
                    )
                ),


            "developerName":
                detect_developer_name(
                    plist
                ),


            "bundleIdentifier":
                plist.get(
                    "CFBundleIdentifier",
                    ""
                ),


            "version":
                plist.get(
                    "CFBundleShortVersionString",
                    "0.0.0"
                ),


            "buildVersion":
                plist.get(
                    "CFBundleVersion",
                    ""
                ),


            "minimumOSVersion":
                plist.get(
                    "MinimumOSVersion",
                    ""
                ),


            "appPath":
                app_path,


            "plist":
                plist
        }


    finally:

        # Keep appPath available for icon extraction
        pass
