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
image_folder = 'D:\\studia\\doktorat\\segmentation\\data\\Agata\\Segmentation\\animation\\back'  # Folder containing your images
output_video = 'D:\\studia\\doktorat\\segmentation\\data\\Agata\\Segmentation\\animation\\back\\back.mp4'  # Name of the output video file
create_video_from_images(image_folder, output_video, frame_rate=24)