import os
from moviepy.editor import ImageSequenceClip

def create_video_from_images(image_folder, output_video, frame_rate=60):
    # Get all image file paths
    image_files = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".png")]
    
    # Create video clip from images
    clip = ImageSequenceClip(image_files, fps=frame_rate)
    
    # Write the video file
    clip.write_videofile(output_video, codec="libx264")

# Example usage
image_folder = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\diff'
#output_video = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\combined\\perspective\\perspective.mp4' 

var = ["combined", "combined_5", "combined_20", "combined_50", "combined_n2", "combined_n3"]


for x in var:
    create_video_from_images(f"{image_folder}/{x}/side",f"{image_folder}/{x}/side/side.mp4", frame_rate=24)
    create_video_from_images(f"{image_folder}/{x}/front",f"{image_folder}/{x}/front/front.mp4", frame_rate=24)
    create_video_from_images(f"{image_folder}/{x}/back",f"{image_folder}/{x}/back/back.mp4", frame_rate=24)
    create_video_from_images(f"{image_folder}/{x}/perspective",f"{image_folder}/{x}/perspective/perspective.mp4", frame_rate=24)