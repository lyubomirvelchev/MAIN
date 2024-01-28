import os
import subprocess

# Directory containing your DWG files
dwg_dir = r'C:\Users\user\PycharmProjects\OpenCVInterview\dwgs'

# Directory to save the converted PNG files
png_dir = r'C:\Users\user\PycharmProjects\OpenCVInterview\pngs'

# Iterate over all DWG files in the directory
for filename in os.listdir(dwg_dir):
    if filename.endswith('.dwg'):
        # Construct the full file paths
        dwg_file = os.path.join(dwg_dir, filename)
        png_file = os.path.join(png_dir, filename[:-4] + '.png')

        # Call dwg2img to convert the DWG file to PNG
        subprocess.run(['dwg2img', '--format', 'png', dwg_file, png_file])
