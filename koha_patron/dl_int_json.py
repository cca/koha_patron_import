# shell out to `gsutil` to download JSON files from GSB
# download pre-college if pc or precollege is passed to script
import argparse
import subprocess

GS_BUCKET = "integration-success"


def main(args) -> None:
    # Download pre-college JSON files
    if args.pc:
        subprocess.run(
            [
                "gsutil",
                "cp",
                f"gs://{GS_BUCKET}/student_pre_college_data.json",
                ".",
            ]
        )

    # always download student and employee data
    subprocess.run(
        [
            "gsutil",
            "cp",
            f"gs://{GS_BUCKET}/student_data.json",
            ".",
        ]
    )

    subprocess.run(
        [
            "gsutil",
            "cp",
            f"gs://{GS_BUCKET}/employee_data.json",
            ".",
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download JSON files from GSB")
    parser.add_argument(
        "-p",
        "--pc",
        "--precollege",
        help="download precollege student data (only needed before summer)",
        action="store_true",
    )
    args: argparse.Namespace = parser.parse_args()
    main(args)
