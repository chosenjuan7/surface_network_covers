import open3d as o3d
import os
import glob

def display_and_save_pointclouds(directory,var, image_prefix="frame", width=600, height=1080):
    
    # Get all .ply files in the directory
    pointcloud_files = glob.glob(os.path.join(directory, "*.ply"))
    
    # Initialize visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=width, height=height)

    output_image_directory_b = f"D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\diff\\filtered_{var}\\back"
    output_image_directory_f= f"D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\diff\\filtered_{var}\\front"
    output_image_directory_s = f"D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\diff\\filtered_{var}\\side"
    output_image_directory_p = f"D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\animation\\diff\\filtered_{var}\\perspective"

    # Loop through each point cloud file
    for idx, file in enumerate(pointcloud_files):
        # Load the point cloud
        pcd = o3d.io.read_triangle_mesh(file, True)

        # Clear geometry and add new point cloud
        vis.clear_geometries()
        vis.add_geometry(pcd)

        view_ctl = vis.get_view_control()


        #back
        vis.poll_events()
        vis.update_renderer()
        vis.capture_screen_image(f"{output_image_directory_b}/{image_prefix}_{idx:04d}.png")

        #front
        view_ctl.rotate(-1000.0, 0.0)  # Rotate the camera
        vis.poll_events()
        vis.update_renderer()
        vis.capture_screen_image(f"{output_image_directory_f}/{image_prefix}_{idx:04d}.png")

        # #side
        view_ctl.rotate(-500.0, 0.0)  # Rotate the camera
        vis.poll_events()
        vis.update_renderer()
        vis.capture_screen_image(f"{output_image_directory_s}/{image_prefix}_{idx:04d}.png")

        # #perspective
        view_ctl.rotate(750.0, 75.0)  # Rotate the camera
        view_ctl.translate(0, 50.0)  # Translate the camera slightly (X and Y)
        vis.poll_events()
        vis.update_renderer()
        vis.capture_screen_image(f"{output_image_directory_p}/{image_prefix}_{idx:04d}.png")
        
        # Modify camera parameters (adjust these for your preferred angle)
        #view_ctl.rotate(-250.0, 75.0)  # Rotate the camera
        #view_ctl.translate(0, 50.0)  # Translate the camera slightly (X and Y)

        #view_ctl.rotate(-500.0, 0.0)  # Rotate the camera
        #view_ctl.translate(0, 0.0)  # Translate the camera slightly (X and Y)

        # Update the visualizer and capture the frame
        # vis.poll_events()
        # vis.update_renderer()

        # # Save the frame as an image
        # vis.capture_screen_image(f"{output_image_directory_b}/{image_prefix}_{idx:04d}.png")
    
    vis.destroy_window()

    print(f"Saved {len(pointcloud_files)} frames to {output_image_directory_b}.")
    
# Example usage:
if __name__ == "__main__":
    # Directory containing point clouds

    values = ["5", "20", "50","5_n2", "20_n2", "50_n2","5_n3", "20_n3", "50_n3"]


    directory =  "D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\filter_edges\\diff"
    # for val in values:
    #     display_and_save_pointclouds(f"{directory}/5_n3", "5_n3")

    display_and_save_pointclouds(f"{directory}/5_n3", "5_n3")