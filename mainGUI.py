import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import webbrowser
import sys

FRAME_RATE = 100  # SET TO 100 IF YOUR PC SUCKS :)
CANCEL_FLAG = False

def average_color(image):
    # Convert image to RGB
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Calculate average color
    average_color = np.mean(np.mean(img_rgb, axis=0), axis=0)

    return average_color.astype(int)

def draw_preview(canvas, colors):
    canvas.delete("all")
    rect_width = canvas.winfo_width() / len(colors)
    for i, color in enumerate(colors):
        x0 = i * rect_width
        x1 = (i + 1) * rect_width
        canvas.create_rectangle(x0, 0, x1, canvas.winfo_height(), fill=f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}')


def generate_svg(colors, svg_path):
    num_colors = len(colors)
    svg_width = 24 * 100 
    svg_height = 6 * 100

    with open(svg_path, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">\n')

        rect_width = svg_width / num_colors
        for i, color in enumerate(colors):
            x = i * rect_width
            f.write(f'<rect x="{x}" y="0" width="{rect_width}" height="{svg_height}" fill="rgb({color[0]}, {color[1]}, {color[2]})"/>\n')
        f.write('</svg>')

def process_video(video_path, progress_bar, progress_label, btn_open_svg, btn_open, btn_cancel, btn_done, btn_new_video, canvas):
    global CANCEL_FLAG
    CANCEL_FLAG = False

    # Open video file
    cap = cv2.VideoCapture(video_path)

    # List to store average colors
    avg_colors = []

    # Read frames from the video
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for i in range(0, num_frames, FRAME_RATE):
        if CANCEL_FLAG:
            break

        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break
        
        # Get the average color of the frame
        avg_color_frame = average_color(frame)
        avg_colors.append(avg_color_frame)

        # Update progress bar and label
        progress = int((i+1) * 100 / num_frames)
        progress_bar["value"] = progress
        progress_label.config(text=f"Processing: {progress}%")
        progress_bar.update()

        draw_preview(canvas, avg_colors)

    # Release video capture object
    cap.release()

    if not CANCEL_FLAG:
        # Generate SVG
        generate_svg(avg_colors, "average_colors.svg")

        progress_label.config(text="Finished Processing")
        print("SVG file generated: average_colors.svg")
        btn_done.pack(side="bottom", pady=10)
        btn_open_svg.pack(pady=5)
        btn_done.pack(pady=5)
        btn_new_video.pack(pady=5)
        btn_open_svg.config(state="normal")
        btn_done.config(state="normal")
        btn_new_video.config(state="normal")
        btn_open.pack_forget()
        btn_cancel.pack_forget()
    else:
        progress_label.config(text="Processing canceled")
        progress_bar["value"] = 0

def open_file_dialog(progress_bar, progress_label, btn_cancel, btn_open_svg, btn_open, btn_done, btn_new_video, canvas):
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi")])
    if file_path:
        progress_label.config(text="Processing...")
        btn_cancel.config(state="normal")
        btn_cancel.pack(pady=5)
        btn_open.pack_forget()
        btn_open_svg.pack_forget()
        btn_done.pack_forget()
        threading.Thread(target=process_video, args=(file_path, progress_bar, progress_label, btn_open_svg, btn_open, btn_cancel, btn_done, btn_new_video, canvas)).start()

def cancel_processing(btn_cancel, progress_bar, btn_open_svg, btn_open, btn_done, btn_new_video, canvas):
    global CANCEL_FLAG
    CANCEL_FLAG = True
    btn_cancel.config(state="disabled")
    progress_bar["value"] = 0
    btn_open.pack(pady=10)
    btn_open_svg.pack(pady=5)
    btn_open.config(state="normal")
    btn_done.pack_forget()
    btn_new_video.pack_forget()
    canvas.delete("all")

def open_svg():
    webbrowser.open("average_colors.svg")

def close_program():
    sys.exit()

def main():
    root = tk.Tk()
    root.title("Video Color Analysis")

    # lbl_progress = tk.Label(root, text="Progress:")
    # lbl_progress.pack(pady=10)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    lbl_status = tk.Label(root, text="Waiting for video...")
    lbl_status.pack(pady=5)

    btn_open = tk.Button(root, text="Open Video", command=lambda: open_file_dialog(progress_bar, lbl_status, btn_cancel, btn_open_svg, btn_open, btn_done, btn_new_video, canvas))
    btn_open.pack(pady=10)

    btn_cancel = tk.Button(root, text="Cancel", command=lambda: cancel_processing(btn_cancel, progress_bar, btn_open_svg, btn_open, btn_done, btn_new_video, canvas), state="disabled")
    btn_cancel.pack(pady=5)

    btn_open_svg = tk.Button(root, text="Open SVG", command=open_svg, state="disabled")

    btn_new_video = tk.Button(root, text="Process New Video", command=lambda: [btn_open_svg.pack_forget(), btn_new_video.pack_forget(), btn_done.pack_forget(), canvas.delete("all"), open_file_dialog(progress_bar, lbl_status, btn_cancel, btn_open_svg, btn_open, btn_done, btn_new_video, canvas)],  state="disabled")
    
    btn_done = tk.Button(root, text="Exit", command=close_program, state="disabled")

    # Canvas to display evolving image preview
    canvas = tk.Canvas(root, width=300, height=150)
    canvas.pack()


    root.mainloop()

if __name__ == "__main__":
    main()
