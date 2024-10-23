import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from moviepy.editor import *
from moviepy.video.fx.all import crop
from PIL import Image, ImageFilter
import numpy as np

class YouTubeShortsEditor:
    # Constants
    YT_SHORTS_WIDTH = 1920
    YT_SHORTS_HEIGHT = 1080
    SHORTS_DURATION = 59  # Max video length for YouTube Shorts (in seconds)
    REELS_DURATION = 90   # Max video length for Instagram Reels (in seconds)

    def __init__(self, master):
        self.master = master
        self.master.title("Bulk Video Editor ©workablesolns")
        self.master.geometry("600x700")
        self.master.resizable(False, False)

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.logo_path = tk.StringVar()
        self.logo_position = tk.StringVar(value="lower left")
        self.video_length = tk.StringVar(value="full")
        self.background_option = tk.StringVar(value="blur")
        self.background_path = tk.StringVar()
        self.crop_height_percentage = tk.DoubleVar(value=90)
        self.crop_slider = None  
        self.crop_value_label = None 
        self.progress_var = tk.DoubleVar()

        self.create_widgets()
        self.update_crop_label()

    def create_widgets(self):
        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Bulk Video Editor", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Input folder
        ttk.Label(main_frame, text="Input Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=50).grid(row=1, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.select_input_folder).grid(row=1, column=2, padx=5, pady=5)

        # Output folder
        ttk.Label(main_frame, text="Output Folder:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=50).grid(row=2, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.select_output_folder).grid(row=2, column=2, padx=5, pady=5)

        # Logo selection
        ttk.Label(main_frame, text="Logo:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.logo_path, width=50).grid(row=3, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.select_logo).grid(row=3, column=2, padx=5, pady=5)

        # Logo position
        ttk.Label(main_frame, text="Logo Position:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.logo_position, values=["lower left", "lower right"]).grid(row=4, column=1, columnspan=2, pady=5)

        # Video length
        ttk.Label(main_frame, text="Video Length:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.video_length, values=["full", "shorts", "reels"]).grid(row=5, column=1, columnspan=2, pady=5)

        # Background option
        ttk.Label(main_frame, text="Background:").grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=self.background_option, values=["blur", "custom"]).grid(row=6, column=1, columnspan=2, pady=5)

        # Custom background selection
        ttk.Label(main_frame, text="Custom Background:").grid(row=7, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.background_path, width=50).grid(row=7, column=1, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.select_background).grid(row=7, column=2, padx=5, pady=5)

        # Crop height percentage
        ttk.Label(main_frame, text="Crop Height (%):").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.crop_slider = ttk.Scale(main_frame, from_=10, to=100, orient=tk.HORIZONTAL,
        variable=self.crop_height_percentage, length=200)
        self.crop_slider.grid(row=8, column=1, pady=5)
        
        self.crop_value_label = ttk.Label(main_frame, text="90%")
        self.crop_value_label.grid(row=8, column=2, pady=5)

        # Bind the slider to a function that updates the label
        self.crop_slider.bind("<Motion>", self.update_crop_label)

        # Start button
        ttk.Button(main_frame, text="Start Processing", command=self.start_processing).grid(row=9, column=0, columnspan=3, pady=20)

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=300, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=10, column=0, columnspan=3, pady=10)
    
    def update_crop_label(self, event=None):
        value = int(self.crop_height_percentage.get())
        self.crop_value_label.config(text=f"{value}%")

    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)

    def select_logo(self):
        logo_path = filedialog.askopenfilename(title="Select Logo", filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if logo_path:
            self.logo_path.set(logo_path)

    def select_background(self):
        bg_path = filedialog.askopenfilename(title="Select Background", filetypes=[("Video/Image files", "*.mp4;*.avi;*.mov;*.png;*.jpg;*.jpeg")])
        if bg_path:
            self.background_path.set(bg_path)

    def start_processing(self):
        if not self.input_folder.get() or not self.output_folder.get():
            messagebox.showerror("Folder Selection Error", "Please select both input and output folders.")
            return

        if self.background_option.get() == "custom" and not self.background_path.get():
            messagebox.showerror("Background Selection Error", "Please select a custom background file.")
            return

        self.process_videos(self.input_folder.get(), self.output_folder.get())

    def blur_frame(self, image):
        pil_image = Image.fromarray(image)
        blurred = pil_image.filter(ImageFilter.GaussianBlur(radius=30))
        return np.array(blurred)

    def process_videos(self, input_folder, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        video_files = [f for f in os.listdir(input_folder) if f.endswith((".mp4", ".avi", ".mov"))]

        if not video_files:
            messagebox.showinfo("No Videos", "No video files found in the selected input folder.")
            return

        total_videos = len(video_files)
        for index, video_file in enumerate(video_files, start=1):
            input_path = os.path.join(input_folder, video_file)
            output_path = os.path.join(output_folder, f"edited_{video_file}")

            self.edit_video(input_path, output_path)
            self.progress_var.set((index / total_videos) * 100)
            self.master.update_idletasks()

        messagebox.showinfo("Processing Complete", "All videos have been processed.")

    def edit_video(self, input_path, output_path):
        try:
            clip = VideoFileClip(input_path)
            original_width, original_height = clip.size

            # Calculate crop height
            crop_height = int(original_height * (self.crop_height_percentage.get() / 100))

            # Crop the video to remove watermark from the bottom
            cropped_clip = crop(clip, y1=0, y2=crop_height, x1=0, x2=clip.w)

            # Resize video to fit the target aspect ratio (16:9)
            target_aspect_ratio = self.YT_SHORTS_WIDTH / self.YT_SHORTS_HEIGHT
            current_aspect_ratio = cropped_clip.w / cropped_clip.h

            if current_aspect_ratio > target_aspect_ratio:
                new_width = self.YT_SHORTS_WIDTH
                new_height = int(new_width / current_aspect_ratio)
            else:
                new_height = self.YT_SHORTS_HEIGHT
                new_width = int(new_height * current_aspect_ratio)

            edited_clip = cropped_clip.resize((new_width, new_height))

            # Create background
            if self.background_option.get() == "blur":
                background = edited_clip.resize((self.YT_SHORTS_WIDTH, self.YT_SHORTS_HEIGHT))
                background = background.fl_image(self.blur_frame)
            elif self.background_option.get() == "custom":
                bg_path = self.background_path.get()
                if bg_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    background = ImageClip(bg_path).set_duration(edited_clip.duration)
                else:
                    background = VideoFileClip(bg_path).loop(duration=edited_clip.duration)
                background = background.resize((self.YT_SHORTS_WIDTH, self.YT_SHORTS_HEIGHT))
            else:
                background = ColorClip((self.YT_SHORTS_WIDTH, self.YT_SHORTS_HEIGHT), color=(0, 0, 0))
                background = background.set_duration(edited_clip.duration)

            # Composite the video onto the background
            x_offset = (self.YT_SHORTS_WIDTH - new_width) // 2
            y_offset = (self.YT_SHORTS_HEIGHT - new_height) // 2
            final_clip = CompositeVideoClip([background, edited_clip.set_position((x_offset, y_offset))])

            # Add logo
            if self.logo_path.get():
                logo = ImageClip(self.logo_path.get()).resize(height=80)  # Adjusted size
                logo = logo.set_duration(final_clip.duration)
                if self.logo_position.get() == "lower left":
                    logo = logo.set_position((20, self.YT_SHORTS_HEIGHT - 100))
                else:
                    logo = logo.set_position((self.YT_SHORTS_WIDTH - logo.w - 20, self.YT_SHORTS_HEIGHT - 100))
                final_clip = CompositeVideoClip([final_clip, logo])

            # Adjust video length
            if self.video_length.get() == "shorts":
                final_clip = final_clip.subclip(0, min(final_clip.duration, self.SHORTS_DURATION))
            elif self.video_length.get() == "reels":
                final_clip = final_clip.subclip(0, min(final_clip.duration, self.REELS_DURATION))

            # Save the final video with improved quality
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", bitrate="8000k", verbose=False)

            print(f"Processing complete for: {input_path}")
        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            messagebox.showerror("Video Processing Error", f"An error occurred while processing {input_path}: {e}")
        finally:
            clip.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeShortsEditor(root)
    root.mainloop()