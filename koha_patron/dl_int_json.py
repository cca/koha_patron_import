# shell out to `gsutil` to download JSON files from GSB
import subprocess

GS_BUCKET = "integration-success"


def main() -> None:
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
    main()
