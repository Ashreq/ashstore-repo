import json
import os


APPS_FILE = "apps.json"


def validate_repository():

    if not os.path.exists(APPS_FILE):
        print("❌ apps.json not found")
        return False


    with open(APPS_FILE, "r") as file:
        repo = json.load(file)


    apps = repo.get(
        "apps",
        []
    )


    print("\nAshStore Validation\n")

    errors = 0

    seen = set()


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


        key = f"{bundle}_{variant}"


        if key in seen:

            print(
                "❌ Duplicate:",
                key
            )

            errors += 1

        else:

            seen.add(key)


        if not app.get("iconURL"):

            print(
                "⚠ Missing icon:",
                name
            )


        if not app.get("developerName"):

            print(
                "⚠ Missing developer:",
                name
            )


        if not app.get("downloadURL"):

            print(
                "❌ Missing download URL:",
                name
            )

            errors += 1


    print("\nSummary")
    print("----------------")
    print(
        "Apps scanned:",
        len(apps)
    )


    if errors:

        print(
            "❌ Validation failed:",
            errors,
            "issues"
        )

        return False


    print(
        "✓ Repository is healthy"
    )

    return True



if __name__ == "__main__":

    validate_repository()
