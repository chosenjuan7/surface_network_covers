import open3d as o3d
import os
import glob

def display_and_save_pointclouds(directory, output_dir, image_prefix="frame", width=1000, height=1080):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all .ply files in the directory
    pointcloud_files = glob.glob(os.path.join(directory, "*.ply"))
    
    # Initialize visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=width, height=height)

    # Loop through each point cloud file
    for idx, file in enumerate(pointcloud_files):
        # Load the point cloud
        pcd = o3d.io.read_triangle_mesh(file, True)

        # Clear geometry and add new point cloud
        vis.clear_geometries()
        vis.add_geometry(pcd)

        view_ctl = vis.get_view_control()
        
        # Modify camera parameters (adjust these for your preferred angle)
        view_ctl.rotate(-250.0, 75.0)  # Rotate the camera
        view_ctl.translate(0, 50.0)  # Translate the camera slightly (X and Y)

        #view_ctl.rotate(-500.0, 0.0)  # Rotate the camera
        #view_ctl.translate(0, 0.0)  # Translate the camera slightly (X and Y)

        # Update the visualizer and capture the frame
        vis.poll_events()
        vis.update_renderer()

        # Save the frame as an image
        vis.capture_screen_image(f"{output_dir}/{image_prefix}_{idx:04d}.png")
    
    vis.destroy_window()

    print(f"Saved {len(pointcloud_files)} frames to {output_dir}.")
    
# Example usage:
if __name__ == "__main__":
    # Directory containing point clouds
    pointcloud_directory = "D:\\studia\\doktorat\\segmentation\\data\\Agata\\Segmentation\\aligned"
    
    # Directory to save the images (frames)
    output_image_directory = "D:\\studia\\doktorat\\segmentation\\data\\Agata\\Segmentation\\animation\\perspective"
    
    # Call the function to display and save point clouds
    display_and_save_pointclouds(pointcloud_directory, output_image_directory)