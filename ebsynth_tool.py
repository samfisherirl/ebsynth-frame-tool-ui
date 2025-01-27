import tkinter
from tkinter import ttk
from tkinter import filedialog
import sv_ttk
import os
from PIL import Image
import shutil
import numpy as np
import json


class EBSynthHelper:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        # Setting up the GUI components
        self.root.title("EBSynth Helper")
        self.root.geometry("500x450")
        self.data = None
        # Creating menu for file operations
        menu_bar = tkinter.Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = tkinter.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load JSON", command=self.load_json)
        self.mapping_file = os.getcwd() + "\\mapping.json"
        # Configure style
        style = ttk.Style()
        style.configure('.', font=('Helvetica', 12))

        # Labels and Entry fields for folder paths
        ttk.Label(self.root, text="Folder 1:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.folder1_path = tkinter.StringVar()
        self.folder1_entry = ttk.Entry(self.root, textvariable=self.folder1_path, width=40)
        self.folder1_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.browse1_btn = ttk.Button(self.root, text="Browse", command=lambda: self.browse_folder(self.folder1_path))
        self.browse1_btn.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(self.root, text="Folder 2:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.folder2_path = tkinter.StringVar()
        self.folder2_entry = ttk.Entry(self.root, textvariable=self.folder2_path, width=40)
        self.folder2_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.browse2_btn = ttk.Button(self.root, text="Browse", command=lambda: self.browse_folder(self.folder2_path))
        self.browse2_btn.grid(row=1, column=2, padx=5, pady=5)
        self.browse5_btn = ttk.Button(self.root, text="generate_frames", command=self.generate_missing_frames)
        self.browse5_btn.grid(row=7, column=2, padx=5, pady=5)

        # Divider option
        ttk.Label(self.root, text="Divider:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.divide = tkinter.StringVar()
        self.divide_entry = ttk.Entry(self.root, textvariable=self.divide, width=40)
        self.divide_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        # Buttons for processing and generating keys
        self.process_btn = ttk.Button(self.root, text="Process", command=self.process_images)
        self.process_btn.grid(row=3, column=1, padx=5, pady=8, sticky='w')
        self.generate_keys_btn = ttk.Button(self.root, text="Generate Keys", command=self.generate_keys)
        self.generate_keys_btn.grid(row=3, column=1, padx=5, pady=8, sticky='e')
        self.rename_files_in_folder2_btn = ttk.Button(self.root, text="Rename Keys", command=self.rename_files_in_folder2)
        self.rename_files_in_folder2_btn.grid(row=5, column=1, padx=5, pady=8, sticky='e')

        # Radio buttons for extra options (example placeholders)
        self.option = tkinter.StringVar(value="crop")
        ttk.Radiobutton(self.root, text="Crop", variable=self.option, value="crop").grid(row=4, column=1, padx=5, pady=8, sticky='w')
        ttk.Radiobutton(self.root, text="Stretch", variable=self.option, value="stretch").grid(row=4, column=1, padx=5, pady=8, sticky='e')

    def browse_folder(self, path_variable):
        folder_path = tkinter.filedialog.askdirectory()
        if folder_path:
            path_variable.set(folder_path)  # Update the path in the Entry widget

    def load_json(self):
        file_path = tkinter.filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                self.data = json.load(file)

    def load_mapping(self):
        # Load the mapping from the JSON file
        with open(self.mapping_file, 'r') as f:
            mapping = json.load(f)
        return mapping

    def rename_files_in_folder2(self):
        # Get the mapping from the JSON file
        # Rename files in folder2 based on the loaded mapping
        folery = self.folder2_entry.get()
        counter = 0
        # Walk through all the files in the directory
        for root, dirs, files in os.walk(folery):
            for ind, fil in self.data.items():
                # Ensure counter is within the range of files list to avoid IndexError
                if counter < len(files):
                    source = files[counter]
                    # Check if the current file is a png before renaming
                    if "png" in source:
                        current_path = os.path.join(root, source)
                        new_name = os.path.basename(fil)  # Assumes 'fil' has the new name for the file
                        new_path = os.path.join(root, new_name)
                        # Use the ind file name to rename file[counter]
                        shutil.move(source, new_path)
                        print(f"Renamed {source} to {new_name}")
                    counter += 1

    def rename_files_in_folder2_to_match_folder1(self, folder1, folder2):
        """
        Enumerate all the files in folder1 and folder2,
        and rename the files in folder2 to have the same names as those in folder1.
        It assumes that the count of files in both folders is the same and 
        the order of files is not significant.

        Args:
        folder1 (str): Path to the first folder (source of file names).
        folder2 (str): Path to the second folder (where files will be renamed).
        """
        
        # Getting a list of filenames in both folders
        folder1_files = sorted(os.listdir(folder1))
        folder2_files = sorted(os.listdir(folder2))
        
        # Check if both folders have the same amount of files
        if len(folder1_files) != len(folder2_files):
            raise ValueError("The number of files in both folders must be the same")

        # Loop through each file in folder2 and rename it to match the corresponding file in folder1
        for file1, file2 in zip(folder1_files, folder2_files):
            file1_path = os.path.join(folder1, file1)  # Full path for file in folder1
            file2_path = os.path.join(folder2, file2)  # Full path for file in folder2
            new_file2_path = os.path.join(folder2, file1)  # New path for the file in folder2
            
            # Rename the file in folder2
            os.rename(file2_path, new_file2_path)

            print(f'Renamed "{file2_path}" to "{new_file2_path}"')

    def process_images(self):
        folder1 = self.folder1_path.get()
        folder2 = self.folder2_path.get()
        option = self.option.get()

        if not folder1 or not folder2 or not option:
            print("All fields are required")
            return

        first_image_path = next(os.path.join(folder1, f) for f in os.listdir(folder1) if os.path.isfile(os.path.join(folder1, f)))
        first_image = Image.open(first_image_path)
        target_size = first_image.size

        for file in os.listdir(folder2):
            file_path = os.path.join(folder2, file)
            if os.path.isfile(file_path):
                img = Image.open(file_path)
                if option == "crop":
                    img = self.crop_image(img, target_size)
                elif option == "stretch":
                    img = img.resize(target_size)
                img.save(file_path)
        print('done!')
        self.rename_files_in_folder2_to_match_folder1(folder1, folder2)
    def crop_image(self, img, target_size):
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        if img_ratio > target_ratio:
            # Crop the image horizontally
            new_height = img.height
            new_width = int(target_ratio * new_height)
        else:
            # Crop the image vertically
            new_width = img.width
            new_height = int(new_width / target_ratio)
        left = (img.width - new_width) / 2
        top = (img.height - new_height) / 2
        right = (img.width + new_width) / 2
        bottom = (img.height + new_height) / 2
        img = img.crop((left, top, right, bottom))
        return img

    def generate_keys(self):
        folder1 = self.folder1_path.get()
        folder2 = self.folder2_path.get()
        division_factor = self.divide.get()

        if not folder1 or not division_factor.isdigit():
            print("Folder 1 path and division factor are required and division factor must be numeric.")
            return

        division_factor = int(division_factor)  # Convert division factor to integer
        try:
            images = [img for img in os.listdir(folder1) if os.path.isfile(os.path.join(folder1, img))]
        except Exception as e:
            print(f"Error reading directory {folder1}: {e}")
            return

        total_images = len(images)
        indices_to_copy = np.round(np.linspace(0, total_images - 1, min(division_factor, total_images))).astype(int)

        if not os.path.isdir(folder2):
            os.makedirs(folder2, exist_ok=True)

        mapping = {}  # Initialize mapping before the loop
        for idx in indices_to_copy:
            src_path = os.path.join(folder1.replace('\\\\', '/'), images[idx])
            dest_path = os.path.join(folder2.replace('\\\\', '/'), images[idx])  # Use the same filename as in the source
            shutil.copy(src_path, dest_path)
            # Update mapping with relative paths
            mapping[src_path] = dest_path

        # Save the mapping to a JSON file
        with open(self.mapping_file, 'w') as f:
            json.dump(mapping, f)
        print("Mapping saved to", self.mapping_file)

    def blend_images(self, img1_path, img2_path, output_path):
        """
        Blends two images together and saves the result.
        """
        img1 = Image.open(img1_path).convert("RGBA")
        img2 = Image.open(img2_path).convert("RGBA")

        # Linear blend the images
        blended = Image.blend(img1, img2, 0.5)
        blended.save(output_path)

    def generate_missing_frames(self):
        """
        Identifies missing frames in a sequence and generates them by blending
        adjacent frames.
        """
        import re
        # Updated to accept any value before the integer at the end
        file_pattern = re.compile(r"(.+)_(\d{5})\.(png|jpg)$")

        # Prepare a dictionary to store filenames indexed by their sequence number
        frames = {}
        directory = self.folder1_path.get()
        # List all files and populate the frames dictionary
        for file in os.listdir(directory):
            match = file_pattern.match(file)
            if match:
                sequence_number = int(match.group(2))
                frames[sequence_number] = file

        # Sort the sequence numbers to identify missing frames
        sorted_sequence_numbers = sorted(frames.keys())
        max_sequence_number = sorted_sequence_numbers[-1]
        min_sequence_number = sorted_sequence_numbers[0]

        # Loop through expected sequence numbers to find missing ones
        for sequence_number in range(min_sequence_number, max_sequence_number):
            if sequence_number not in frames:
                # Find available adjacent frames
                prev_frame_number = sequence_number - 1
                next_frame_number = sequence_number + 1

                while prev_frame_number not in frames and prev_frame_number > min_sequence_number:
                    prev_frame_number -= 1

                while next_frame_number not in frames and next_frame_number < max_sequence_number:
                    next_frame_number += 1

                # Ensure both adjacent frames are found
                if prev_frame_number in frames and next_frame_number in frames:
                    prev_frame_path = os.path.join(directory, frames[prev_frame_number])
                    next_frame_path = os.path.join(directory, frames[next_frame_number])

                    # Generate name for the new blended frame
                    base_name, _ = os.path.splitext(frames[prev_frame_number])  # Remove extension
                    base_name = '_'.join(base_name.split('_')[:-1])
                    new_frame_name = f"{base_name}_{str(sequence_number).zfill(5)}.png"
                    new_frame_path = os.path.join(directory, new_frame_name)

                    # Blend and save the new frame
                    self.blend_images(prev_frame_path, next_frame_path, new_frame_path)
                    print(f"Generated missing frame: {new_frame_name}")


if __name__ == "__main__":
    root = tkinter.Tk()
    app = EBSynthHelper(root)
    root.mainloop()
