import os
import subprocess

# Directory containing the BOM exports
bom_exports_dir = '/workspace/bom_exports'
kicad_projects_dir = '/workspace/KiCad'

# List all directories in the BOM exports directory
finished_projects = os.listdir(bom_exports_dir)

# Iterate over the projects on the list and export the schematics
for project in finished_projects:
    # Define the path to the project directory
    project_dir = os.path.join(kicad_projects_dir, project)
    # Check if the project directory exists
    if not os.path.exists(project_dir):
        print(f'ERROR: Project directory {project_dir} does not exist.')
        continue
    # Check if the project_dir contains only one directory and if so add it the project_dir
    # (because sometimes the project directory contains an additional directory with the same name)
    project_dir_contents = os.listdir(project_dir)
    if len(project_dir_contents) == 1 and os.path.isdir(os.path.join(project_dir, project_dir_contents[0])):
        project_dir = os.path.join(project_dir, project_dir_contents[0])

    # Define the path to the schematic file
    schematic_file = os.path.join(project_dir, project + '.kicad_sch')
    # Check if the schematic file exists
    if not os.path.exists(schematic_file):
        print(f'ERROR: Schematic file {schematic_file} does not exist.')
        continue

    # Define the path to the output PDF file
    output_pdf = os.path.join(bom_exports_dir, project, project + '.pdf')

    print(f'Exporting schematic for project {project} of schematic file {schematic_file} to PDF file {output_pdf}') 

    # Run the command to export the schematic to a PDF file
    subprocess.run(['kicad-cli', 'sch', 'export', 'pdf', schematic_file, '-o', output_pdf])