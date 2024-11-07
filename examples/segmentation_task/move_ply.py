from pathlib import Path
import shutil

def find_and_move_ply_files(source_dir, target_dir):
    # Convert to Path objects
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Check if the target directory exists, if not, create it
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Recursively find all .ply files in the source directory
    for ply_file in source_path.rglob('*.ply'):
        # Define the target file path
        target_file_path = target_path / ply_file.name
        
        # Move the file to the target directory
        shutil.move(str(ply_file), str(target_file_path))
        print(f"Moved: {ply_file} to {target_file_path}")

# Example usage
if __name__ == "__main__":
    source_directory = 'D:\\studia\\doktorat\\segmentation\\surface_networks_covers\\examples\\segmentation_task\\data\\results'  # Replace with your source directory path
    target_directory = 'D:\\studia\\doktorat\\segmentation\\data\\Agata\\Segmentation\\aligned'  # Replace with your target directory path
    
    find_and_move_ply_files(source_directory, target_directory)