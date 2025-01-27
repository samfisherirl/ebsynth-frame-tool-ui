import tkinter
from tkinter import ttk, filedialog
import os
from PIL import Image
import numpy as np
import json
import shutil
import re
import cv2  # New import for video processing


class EBSynthHelper:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.json_file = "temp_values.json"  # JSON file for storing temp values

    def setup_ui(self):
        self.root.title("EBSynth Helper")
        self.root.geometry("620x480")  # Adjusted to accommodate new buttons
        self.data = None
        menu_bar = tkinter.Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = tkinter.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load JSON", command=self.load_json)
        self.mapping_file = os.path.join(os.getcwd(), "mapping.json")

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        style = ttk.Style()
        style.configure(".", font=("Helvetica", 12))

        ttk.Label(main_frame, text="Folder 1:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.folder1_path = tkinter.StringVar()
        self.folder1_entry = ttk.Entry(
            main_frame, textvariable=self.folder1_path, width=40
        )
        self.folder1_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.browse1_btn = ttk.Button(
            main_frame,
            text="Browse",
            command=lambda: self.browse_folder(self.folder1_path),
        )
        self.browse1_btn.grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(main_frame, text="Folder 2:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.folder2_path = tkinter.StringVar()
        self.folder2_entry = ttk.Entry(
            main_frame, textvariable=self.folder2_path, width=40
        )
        self.folder2_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.browse2_btn = ttk.Button(
            main_frame,
            text="Browse",
            command=lambda: self.browse_folder(self.folder2_path),
        )
        self.browse2_btn.grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(main_frame, text="Divider:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.divide = tkinter.StringVar()
        self.divide_entry = ttk.Entry(main_frame, textvariable=self.divide, width=40)
        self.divide_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=3, pady=10)
        self.process_btn = ttk.Button(
            action_frame, text="Process", command=self.process_images
        )
        self.process_btn.grid(row=0, column=0, padx=5)
        self.generate_keys_btn = ttk.Button(
            action_frame, text="Generate Keys", command=self.generate_keys
        )
        self.generate_keys_btn.grid(row=0, column=1, padx=5)
        self.rename_files_in_folder2_btn = ttk.Button(
            action_frame, text="Rename Keys", command=self.rename_files_in_folder2
        )
        self.rename_files_in_folder2_btn.grid(row=0, column=2, padx=5)
        ttk.Label(main_frame, text="Options:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        self.option = tkinter.StringVar(value="crop")
        radio_frame = ttk.Frame(main_frame)
        radio_frame.grid(row=4, column=1, columnspan=2, pady=5, sticky="w")
        ttk.Radiobutton(
            radio_frame, text="Crop", variable=self.option, value="crop"
        ).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(
            radio_frame, text="Stretch", variable=self.option, value="stretch"
        ).grid(row=0, column=1, padx=5)
        self.browse5_btn = ttk.Button(
            main_frame, text="Generate Frames", command=self.generate_missing_frames
        )
        self.browse5_btn.grid(row=5, column=1, columnspan=2, pady=10)

        # New buttons for video processing
        self.extract_frames_btn = ttk.Button(
            main_frame, text="Extract Frames", command=self.extract_frames_from_video
        )
        self.extract_frames_btn.grid(row=6, column=1, columnspan=2, pady=10)

        self.create_video_btn = ttk.Button(
            main_frame, text="Create Video", command=self.create_video_from_frames
        )
        self.create_video_btn.grid(row=7, column=1, columnspan=2, pady=10)

    def browse_folder(self, path_variable):
        folder_path = filedialog.askdirectory()
        if folder_path:
            path_variable.set(folder_path)

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as file:
                self.data = json.load(file)

    def load_mapping(self):
        with open(self.mapping_file, "r") as f:
            mapping = json.load(f)
        return mapping

    def rename_files_in_folder2(self):
        folery = self.folder2_entry.get()
        counter = 0
        for root, _, files in os.walk(folery):
            for ind, fil in self.data.items():
                if counter < len(files):
                    source = files[counter]
                    if "png" in source:
                        current_path = os.path.join(root, source)
                        new_name = os.path.basename(fil)
                        new_path = os.path.join(root, new_name)
                        shutil.move(current_path, new_path)
                        print(f"Renamed {source} to {new_name}")
                    counter += 1

    def rename_files_in_folder2_to_match_folder1(self, folder1, folder2):
        folder1_files = sorted(os.listdir(folder1))
        folder2_files = sorted(os.listdir(folder2))
        if len(folder1_files) != len(folder2_files):
            raise ValueError("The number of files in both folders must be the same")
        for file1, file2 in zip(folder1_files, folder2_files):
            file1_path = os.path.join(folder1, file1)
            file2_path = os.path.join(folder2, file2)
            new_file2_path = os.path.join(folder2, file1)
            os.rename(file2_path, new_file2_path)
            print(f'Renamed "{file2_path}" to "{new_file2_path}"')

    def process_images(self):
        folder1 = self.folder1_path.get()
        folder2 = self.folder2_path.get()
        option = self.option.get()
        if not folder1 or not folder2 or not option:
            print("All fields are required")
            return
        first_image_path = next(
            (
                os.path.join(folder1, f)
                for f in os.listdir(folder1)
                if os.path.isfile(os.path.join(folder1, f))
            ),
            None,
        )
        first_image = Image.open(first_image_path)
        target_size = first_image.size
        for file in os.listdir(folder2):
            file_path = os.path.join(folder2, file)
            if os.path.isfile(file_path):
                img = Image.open(file_path)
                if option == "crop":
                    img = self.crop_image(img, target_size)
                elif option == "stretch":
                    img = img.resize(target_size, Image.ANTIALIAS)
                img.save(file_path)
        print("done!")
        self.rename_files_in_folder2_to_match_folder1(folder1, folder2)

    def crop_image(self, img, target_size):
        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]
        if img_ratio > target_ratio:
            new_height = img.height
            new_width = int(target_ratio * new_height)
        else:
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
            print(
                "Folder 1 path and division factor are required and division factor must be numeric."
            )
            return
        division_factor = int(division_factor)
        try:
            images = [
                img
                for img in os.listdir(folder1)
                if os.path.isfile(os.path.join(folder1, img))
            ]
        except Exception as e:
            print(f"Error reading directory {folder1}: {e}")
            return
        total_images = len(images)
        indices_to_copy = np.round(
            np.linspace(0, total_images - 1, min(division_factor, total_images))
        ).astype(int)
        if not os.path.isdir(folder2):
            os.makedirs(folder2, exist_ok=True)
        mapping = {}
        for idx in indices_to_copy:
            src_path = os.path.join(folder1.replace("\\\\", "/"), images[idx])
            dest_path = os.path.join(folder2.replace("\\\\", "/"), images[idx])
            shutil.copy(src_path, dest_path)
            mapping[src_path] = dest_path
        with open(self.mapping_file, "w") as f:
            json.dump(mapping, f)
        print("Mapping saved to", self.mapping_file)

    def blend_images(self, img1_path, img2_path, output_path):
        img1 = Image.open(img1_path).convert("RGBA")
        img2 = Image.open(img2_path).convert("RGBA")
        blended = Image.blend(img1, img2, 0.5)
        blended.save(output_path)

    def generate_missing_frames(self):
        file_pattern = re.compile(r"(.+)_(\d{5})\.(png|jpg)$")
        frames = {}
        directory = self.folder1_path.get()
        for file in os.listdir(directory):
            match = file_pattern.match(file)
            if match:
                sequence_number = int(match.group(2))
                frames[sequence_number] = file
        sorted_sequence_numbers = sorted(frames.keys())
        max_sequence_number = sorted_sequence_numbers[-1]
        min_sequence_number = sorted_sequence_numbers[0]
        for sequence_number in range(min_sequence_number, max_sequence_number):
            if sequence_number not in frames:
                prev_frame_number = sequence_number - 1
                next_frame_number = sequence_number + 1
                while (
                    prev_frame_number not in frames
                    and prev_frame_number > min_sequence_number
                ):
                    prev_frame_number -= 1
                while (
                    next_frame_number not in frames
                    and next_frame_number < max_sequence_number
                ):
                    next_frame_number += 1
                if prev_frame_number in frames and next_frame_number in frames:
                    prev_frame_path = os.path.join(directory, frames[prev_frame_number])
                    next_frame_path = os.path.join(directory, frames[next_frame_number])
                    base_name, _ = os.path.splitext(frames[prev_frame_number])
                    base_name = "_".join(base_name.split("_")[:-1])
                    new_frame_name = f"{base_name}_{str(sequence_number).zfill(5)}.png"
                    new_frame_path = os.path.join(directory, new_frame_name)
                    self.blend_images(prev_frame_path, next_frame_path, new_frame_path)
                    print(f"Generated missing frame: {new_frame_name}")

    # New method to extract frames from a video
    def extract_frames_from_video(self):
        video_file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        if not video_file:
            return
        output_folder = filedialog.askdirectory()
        if not output_folder:
            return

        cap = cv2.VideoCapture(video_file)
        success, frame = cap.read()
        count = 0
        while success:
            frame_path = os.path.join(output_folder, f"frame_{str(count).zfill(5)}.png")
            cv2.imwrite(frame_path, frame)
            success, frame = cap.read()
            count += 1

        cap.release()

        with open(self.json_file, "w") as f:
            json.dump(
                {
                    "fps": cap.get(cv2.CAP_PROP_FPS),
                    "resolution": (
                        int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    ),
                },
                f,
            )
        print(f"Frames extracted to {output_folder}")

    # New method to create a video from frames
    def create_video_from_frames(self):
        input_folder = filedialog.askdirectory()
        if not input_folder:
            return
        output_file = filedialog.asksaveasfilename(
            defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")]
        )
        if not output_file:
            return

        with open(self.json_file, "r") as f:
            temp_values = json.load(f)

        frame_files = sorted(
            [
                os.path.join(input_folder, f)
                for f in os.listdir(input_folder)
                if f.endswith(".png")
            ]
        )

        if not frame_files:
            print("No frames found in the folder.")
            return

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(
            output_file, fourcc, temp_values["fps"], temp_values["resolution"]
        )

        for frame_file in frame_files:
            frame = cv2.imread(frame_file)
            video_writer.write(frame)

        video_writer.release()
        print(f"Video saved to {output_file}")


if __name__ == "__main__":
    root = tkinter.Tk()
    app = EBSynthHelper(root)
    root.mainloop()
