FROM kicad/kicad:8.0.6

WORKDIR /workspace

# Copy the KiCad project files, the scripts and the bom_exports into the container
COPY scripts /workspace/scripts
COPY bom_exports /workspace/bom_exports
COPY KiCad /workspace/KiCad

# Install any additional dependencies (if needed)
RUN sudo apt-get update && sudo apt-get install -y \
    python3
    
# run export schematic script
CMD ["python3", "/workspace/scripts/export_schematics.py"]