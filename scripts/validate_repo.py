import json
import os


APPS_FILE = "apps.json"


def validate_repository():

    print("\nAshStore Repository Validation\n")

    if not os.path.exists(APPS_FILE):
        print("❌ apps.json not found")
        return False


    with open(APPS_FILE, "r") as file:
        repo = json.load(file)


    apps = repo.get(
        "apps",
        []
    )


    errors = 0
    warnings = 0

    seen_apps = set()
    seen_urls = set()


    for app in apps:

        name = app.get(
            "name",
            "Unknown"
        )

        bundle = app.get(
            "bundleIdentifier",
            ""
        )

        variant = app.get(
            "variantID",
            ""
        )

        url = app.get(
            "downloadURL",
            ""
        )


        kkey = f"{bundle}_{variant}_{url}"


        # Duplicate app check
        if key in seen_apps:

            print(
                "❌ Duplicate app:",
                key
            )

            errors += 1

        else:

            seen_apps.add(key)


        # Duplicate download check
        if url in seen_urls:

            print(
                "❌ Duplicate download URL:",
                url
            )

            errors += 1

        else:

            seen_urls.add(url)


        # Required fields

        if not bundle:

            print(
                "❌ Missing bundleIdentifier:",
                name
            )

            errors += 1


        if not variant:

            print(
                "❌ Missing variantID:",
                name
            )

            errors += 1


        if not url:

            print(
                "❌ Missing downloadURL:",
                name
            )

            errors += 1


        if not app.get("sha256"):

            print(
                "❌ Missing SHA256:",
                name
            )

            errors += 1


        if not app.get("iconURL"):

            print(
                "⚠ Missing icon:",
                name
            )

            warnings += 1


        # Old version history check

        if "versions" in app:

            print(
                "⚠ Old versions array found:",
                name
            )

            warnings += 1



    print("\nSummary")
    print("----------------")
    print(
        "Apps checked:",
        len(apps)
    )

    print(
        "Errors:",
        errors
    )

    print(
        "Warnings:",
        warnings
    )


    if errors > 0:

        print(
            "\n❌ Validation failed"
        )

        return False


    print(
        "\n✓ Repository is healthy"
    )

    return True



if __name__ == "__main__":

    if not validate_repository():

        exit(1)
