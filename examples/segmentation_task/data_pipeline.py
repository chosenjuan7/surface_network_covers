import os
import glob
import pymeshlab

def find_obj_files(directory):
    # Use glob to find all .obj files in the directory
    obj_files = glob.glob(os.path.join(directory, '*.obj'))
    return obj_files


def simplify_and_remesh(input_file, output_file, target_vertex_count):
    # Create a new MeshSet
    ms = pymeshlab.MeshSet()
    
    # Load the mesh from the .obj file
    ms.load_new_mesh(input_file)

    ms.apply_filter('generate_simplified_point_cloud', samplenum=target_vertex_count)
    
    
    # Apply the Poisson surface reconstruction filter
    ms.apply_filter('generate_surface_reconstruction_screened_poisson')
    

    ms.apply_filter('meshing_remove_connected_component_by_diameter')
    # Apply the simplification filter on the reconstructed mesh
   
    # Save the simplified mesh to the output file in .off format
    ms.save_current_mesh(output_file, save_vertex_color=False, save_vertex_normal=False, save_face_color=False)

# Main block to specify the directory and print the results
if __name__ == "__main__":
    # Replace 'your_directory_path' with the path to your directory
    #directory = 'D:\\studia\\doktorat\\segmentation\\data\\Agata\\Agata\\00000000\\OBJ'
    #directory = 'D:\\studia\\doktorat\\segmentation\\data\\Agata\\Agata\\00000000\\TEST'
    directory = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Meshes\\OBJ'
    target_directory = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\TEST\\'
    #target_directory = 'D:\\studia\\doktorat\\segmentation\\data\\Agata\\Agata_TEST\\'
    target_vertex_count = 3000  # Replace with your target number of vertices
    obj_files = find_obj_files(directory)
    
    for obj_file in obj_files:
        simplify_and_remesh(obj_file, target_directory + os.path.splitext(os.path.basename(obj_file))[0] + ".off", target_vertex_count)
        #print(f"Simplified mesh saved to {target_directory + os.path.basename(obj_file) + ".off"}")

    #input_file = 'D:\\studia\\doktorat\\segmentation\\data\\Agata\\Agata\\00000000\\OBJ\\00000594_SfM.obj'  # Replace with your input .obj file path
    #output_file = 'D:\\studia\\doktorat\\segmentation\\data\\Agata\\Agata_simplified\\00000594_SfM.off'  # Replace with your desired output .off file path
    
    
    #simplify_and_remesh(input_file, output_file, target_vertex_count)
    #print(f"Simplified mesh saved to {output_file}")