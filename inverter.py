import rawpy
import imageio
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import sys
'''test'''
def max_bits(b):
    return (1 << b) - 1

def get_baseWB(raw, encoding):
    raw_base = raw
    rgb_base_linear = raw_base.postprocess(output_bps=encoding, output_color=rawpy.ColorSpace.raw, gamma=(1, 1),
                                        user_wb=[1.0, 1.0, 1.0, 1.0], no_auto_bright=False,auto_bright_thr=0.1)
    

    rgb_base_linear_cropped = rgb_base_linear[0:200,]

    red_channel_array = rgb_base_linear_cropped[..., 0]
    green_channel_array = rgb_base_linear_cropped[..., 1]
    blue_channel_array = rgb_base_linear_cropped[..., 2]

    avg_r = np.average(red_channel_array)#[red_channel_array!=0])
    avg_g = np.average(green_channel_array)#[green_channel_array!=0])
    avg_b = np.average(blue_channel_array)#[blue_channel_array!=0])

    base_wb = [avg_g/avg_r, 1.0, avg_g/avg_b, 1.0]


    img_sample = rgb_base_linear[750:2000,1000:3000]
    #plt.imshow(img_sample)

    base_brightness = max_bits(encoding)/np.average(img_sample)

    return base_wb, base_brightness

def invertNegative(source_file:str, encoding = 8, bright_weight = 1):
    raw = rawpy.imread(source_file)
    base_wb, base_brightness = get_baseWB(raw, encoding)

    rgb_neg_corrected = raw.postprocess(output_bps=encoding, output_color=rawpy.ColorSpace.raw, gamma=(1, 1),
                                        user_wb=base_wb, no_auto_bright=False,auto_bright_thr=0.1)

    rgb_neg_corrected_cropped = rgb_neg_corrected#[200:2000,1000:2000]
    #plt.imshow(rgb_neg_corrected_cropped)

    max_r = np.max(rgb_neg_corrected_cropped[..., 0])
    max_g = np.max(rgb_neg_corrected_cropped[..., 1])
    max_b = np.max(rgb_neg_corrected_cropped[..., 2])

    rgb_pos = rgb_neg_corrected_cropped.copy()
    rgb_pos[..., 0] = max_r - rgb_pos[..., 0]
    rgb_pos[..., 1] = max_g - rgb_pos[..., 1]
    rgb_pos[..., 2] = max_b - rgb_pos[..., 2]

    #plt.imshow(rgb_pos)

    return rgb_pos

def save_to_DNG(RGB_array, output_path):
    red_channel_array = RGB_array[..., 0]
    green_channel_array = RGB_array[..., 1]
    blue_channel_array = RGB_array[..., 2]

    # Create a random noise image with random colors
    random_noise_rgb = np.stack((red_channel_array, green_channel_array, blue_channel_array), axis=-1)

    # Save the random noise image as a DNG file
    imageio.imwrite(output_path, random_noise_rgb)

def import_files():
    file_paths = filedialog.askopenfilenames()  # Open the file dialog to select multiple files

    for file_path in file_paths:
        file_list.append(file_path)  # Add selected file paths to the list
        file_listbox.insert(tk.END, file_path)  # Display the file paths in the listbox

def set_output_folder():
    global output_folder
    output_folder = filedialog.askdirectory()  # Open folder selection dialog
    output_folder_label.config(text="Output Folder: " + output_folder)

def show_completion_popup():
    messagebox.showinfo("Inversion Completed", "Inversion process completed successfully.")

def show_completion_popup():
    def close_window():
        root.destroy()

    messagebox.showinfo("Inversion Completed", "Inversion process completed successfully.")
    root.after(100, close_window)  # Close the Tkinter window after a short delay

def run_Inversion():
    progress_bar["value"] = 0
    root.update()

    progress_step = 100 / len(file_list)

    for idx, file in enumerate(file_list, start=1):
        file_name = file.split("/")[-1]
        file_name = file_name.split(".")[0]
        new_filename = file_name + ".dng"

        inverted_image = invertNegative(source_file=file, encoding=16)
        save_to_DNG(inverted_image, output_folder + "//" + new_filename)

        progress_bar["value"] = idx * progress_step
        root.update()

    show_completion_popup()

print("app started...")

# Create the main application window
root = tk.Tk()

root.title("Raw color inversion")

file_list = []  # List to store file paths
output_folder = ""  # Variable to store the output folder path

# Create a listbox to display selected file paths
file_listbox = tk.Listbox(root, width=50)
file_listbox.pack()

# Create a button to import files
import_button = tk.Button(root, text="Import Files", command=import_files)
import_button.pack(pady=10)

# Create a button to set the output folder
output_folder_button = tk.Button(root, text="Set Output Folder", command=set_output_folder)
output_folder_button.pack(pady=10)

# Label to display the selected output folder
output_folder_label = tk.Label(root, text="Output Folder: " + output_folder)
output_folder_label.pack()

# Button to run the inversion process
output_folder_button = tk.Button(root, text="Run", command=run_Inversion)
output_folder_button.pack(pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='determinate')
progress_bar.pack(pady=10)

#root.protocol("WM_DELETE_WINDOW", sys.exit)  # Close the script on window close
root.protocol("WM_DELETE_WINDOW", root.destroy)

root.mainloop()