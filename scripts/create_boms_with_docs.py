import os
import shutil
import sys
import pandas as pd
from collections import defaultdict
import re

# Please mind: The script is designed to be run from the root directory of the repository!

# Constants
KICAD_LIBRARY_DOCS_DIR = "KiCad_Library/documents"
KICAD_PROJECTS_DIR = "KiCad"
BOM_EXPORTS_DIR = "bom_exports"
PATH_TO_DOCS_COLUMN_NAME = "path_to_docs"

def sort_and_merge_designators(designators):
    def extract_number(designator):
        match = re.match(r"([A-Za-z]+)(\d+)", designator)
        if match:
            return match.group(1), int(match.group(2))
        return designator, 0

    def merge_ranges(ranges):
        merged = []
        for r in ranges:
            if not merged or merged[-1][-1] + 1 < r[0]:
                merged.append(r)
            else:
                merged[-1][-1] = r[-1]
        return merged

    # Flatten the list and sort by the numeric part
    flattened = [d for sublist in designators for d in sublist.split(',')]
    sorted_designators = sorted(flattened, key=extract_number)

    # Group by prefix and merge ranges
    grouped = {}
    for d in sorted_designators:
        prefix, number = extract_number(d)
        if prefix not in grouped:
            grouped[prefix] = []
        grouped[prefix].append(number)

    merged_designators = []
    for prefix, numbers in grouped.items():
        ranges = [[n, n] for n in numbers]
        merged_ranges = merge_ranges(ranges)
        for r in merged_ranges:
            if r[0] == r[1]:
                merged_designators.append(f"{prefix}{r[0]}")
            else:
                merged_designators.append(f"{prefix}{r[0]}-{prefix}{r[1]}")

    return merged_designators


def main():
    # Step 1: Loop through all available projects
    available_projects = sorted([name for name in os.listdir(KICAD_PROJECTS_DIR) if os.path.isdir(os.path.join(KICAD_PROJECTS_DIR, name))])

    for project_name in available_projects:
        print(f"Processing project: {project_name}")

        # Step 2: Validate the Project Name
        project_path = os.path.join(KICAD_PROJECTS_DIR, project_name)
        if not os.path.isdir(project_path):
            print(f"Error! Project {project_name} does not exist in {KICAD_PROJECTS_DIR}.")
            continue

        # Step 3: Locate the BOM File
        bom_file = project_name + "_BOM.csv"
        bom_path = os.path.join(project_path, project_name, "manufacturing", "PCB Assembly", bom_file)
        if not os.path.isfile(bom_path):
            print(f"    Warning! BOM file not found at path:")
            print(f"        {bom_path}")
            print(f"    Skipping project.")
            continue

        # Step 4: Read the BOM File
        try:
            bom_df = pd.read_csv(bom_path)
        except Exception as e:
            print(f"    Error reading BOM file: {e}")
            continue

        if PATH_TO_DOCS_COLUMN_NAME not in bom_df.columns:
            print(f"    Error! BOM file does not contain '{PATH_TO_DOCS_COLUMN_NAME}' column.")
            continue

        # Step 5: Copy Files
        export_dir = os.path.join(BOM_EXPORTS_DIR, project_name)
        docs_export_dir = os.path.join(export_dir, "docs")
        os.makedirs(docs_export_dir, exist_ok=True)

        # Group designators by path_to_docs
        docs_to_designators = defaultdict(list)
        for index, row in bom_df.iterrows():
            # Skip rows with empty path_to_docs
            if pd.isna(row[PATH_TO_DOCS_COLUMN_NAME]):
                print(f"    Warning: Empty path_to_docs in row {index} for designator {row['Designator']} with value {row['Comment']}. Skipping.")
                continue
            path_to_docs = os.path.join(KICAD_LIBRARY_DOCS_DIR, row[PATH_TO_DOCS_COLUMN_NAME])
            designator = row.get("Designator", f"entry_{index}")
            docs_to_designators[path_to_docs].append(designator)

        # Copy files for each unique path_to_docs
        for path_to_docs, designators in docs_to_designators.items():
            if not os.path.isdir(path_to_docs):
                print(f"    Error: Directory {path_to_docs} does not exist.")
                continue

            dest_dir = os.path.join(docs_export_dir, ",".join(sort_and_merge_designators(designators)))
            os.makedirs(dest_dir, exist_ok=True)

            try:
                for item in os.listdir(path_to_docs):
                    s = os.path.join(path_to_docs, item)
                    d = os.path.join(dest_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
                print(f"    Copied all files from {path_to_docs} to {dest_dir}")
            except Exception as e:
                print(f"    Error copying files from {path_to_docs} to {dest_dir}: {e}")

        # Remove the specified column and create a new DataFrame
        bom_df_modified = bom_df.drop(columns=[PATH_TO_DOCS_COLUMN_NAME])

        # Export the modified DataFrame to a CSV file
        output_bom_path = os.path.join(export_dir, bom_file)
        bom_df_modified.to_csv(output_bom_path, index=False)
        print(f"    Exported modified BOM to {output_bom_path}")


if __name__ == "__main__":
    main()