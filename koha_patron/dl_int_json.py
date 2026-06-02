# shell out to `gsutil` to download JSON files from GSB
import subprocess
from shutil import which

GS_BUCKET = "integration-success"


def main() -> None:
    gcloud: str | None = which("gcloud")
    if not gcloud:
        raise OSError("gcloud CLI is not installed or not found in PATH.")

    subprocess.run(  # noqa: S603
        [
            gcloud,
            "storage",
            "cp",
            f"gs://{GS_BUCKET}/student_data.json",
            ".",
        ],
    )

    subprocess.run(  # noqa: S603
        [
            gcloud,
            "storage",
            "cp",
            f"gs://{GS_BUCKET}/employee_data.json",
            ".",
        ],
    )


if __name__ == "__main__":
    main()
