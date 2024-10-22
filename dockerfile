FROM kicad/kicad:8.0.6

WORKDIR /workspace

# Copy the KiCad project files into the container
COPY . /workspace

# Install any additional dependencies (if needed)
RUN sudo apt-get update && sudo apt-get install -y \
    python3 \
    python3-pip

# run export schematic script
CMD ["python3", "/workspace/scripts/export_schematics.py"]