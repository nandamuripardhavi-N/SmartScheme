
import subprocess
import sys
import zipfile
import pandas as pd

from pathlib import Path

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"

DATASETS = {
    "government_schemes":
        "premsargara/indian-government-beneficiary-schemes",

    "education":
        "nagarshivam/india-colleges-and-cities",

    "agriculture":
        "pyatakov/india-agriculture-crop-production"
}


# ==========================================
# 2. EXCEL TO CSV CONVERSION
# ==========================================

def convert_excel_to_csv(folder):

    print("\nChecking Excel files...")

    for excel_file in folder.rglob("*"):

        if excel_file.suffix.lower() not in [".xlsx", ".xls"]:
            continue

        try:
            sheets = pd.read_excel(
                excel_file,
                sheet_name=None
            )

            for sheet_name, df in sheets.items():

                if len(sheets) == 1:
                    output_name = excel_file.stem
                else:
                    output_name = (
                        f"{excel_file.stem}_{sheet_name}"
                    )

                output_file = (
                    excel_file.parent / f"{output_name}.csv"
                )

                df.to_csv(
                    output_file,
                    index=False,
                    encoding="utf-8-sig"
                )

                print(f"Converted: {output_file.name}")

        except Exception as error:
            print(
                f"Conversion failed for {excel_file.name}: {error}"
            )


# ==========================================
# 3. DOWNLOAD AND EXTRACT DATASET
# ==========================================

def download_dataset(name, dataset_id):

    print("\n" + "=" * 55)
    print(f"DOWNLOADING: {name.upper()}")
    print("=" * 55)

    destination = RAW_DIR / name
    destination.mkdir(parents=True, exist_ok=True)

    try:

        command = [
            sys.executable,
            "-m",
            "kaggle",
            "datasets",
            "download",
            "-d",
            dataset_id,
            "-p",
            str(destination),
            "--force"
        ]

        # Download dataset ZIP into its own folder
        subprocess.run(command, check=True)

        zip_file = (
            destination / f"{dataset_id.split('/')[-1]}.zip"
        )

        if not zip_file.exists():
            raise FileNotFoundError(
                f"ZIP file not found: {zip_file.name}"
            )

        print("\nExtracting dataset...")

        # Extract ZIP contents
        with zipfile.ZipFile(zip_file, "r") as archive:

            for member in archive.infolist():

                # Prevent unsafe ZIP paths
                target = (destination / member.filename).resolve()

                if (
                    target != destination.resolve()
                    and destination.resolve() not in target.parents
                ):
                    raise ValueError(
                        "Unsafe file path found in ZIP archive."
                    )

            archive.extractall(destination)

        # Delete ZIP after successful extraction
        zip_file.unlink()

        print("Extraction completed!")

        # Convert Excel files into CSV
        convert_excel_to_csv(destination)

        print(f"\nSUCCESS: {name} downloaded and processed!")

    except subprocess.CalledProcessError as error:

        print(f"\nDOWNLOAD FAILED: {name}")
        print(f"Reason: {error}")

    except Exception as error:

        print(f"\nPROCESSING FAILED: {name}")
        print(f"Reason: {error}")


# ==========================================
# 4. MAIN FUNCTION
# ==========================================

def main():

    print("\nSMARTSCHEME AI")
    print("KAGGLE DATASET DOWNLOAD SYSTEM")
    print("=" * 55)

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    for name, dataset_id in DATASETS.items():

        download_dataset(name, dataset_id)

    print("\n" + "=" * 55)
    print("DATASET DOWNLOAD PROCESS FINISHED!")
    print("=" * 55)

    print("\nDataset folders:")

    for name in DATASETS:

        print(f"- {RAW_DIR / name}")


# ==========================================
# 5. PROGRAM ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
