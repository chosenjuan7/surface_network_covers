import pymeshlab as ml
import glob
import os
import open3d as o3d
import numpy as np
import copy
from scipy.spatial import cKDTree
from collections import Counter
from pprint import pprint

def find_k_nearest_neighbors(mesh, vertex, k):
    vertices = np.asarray(mesh.vertices)
    kdtree = cKDTree(vertices)
    distances, indices = kdtree.query(vertex, k=k+1)  # +1 to include the point itself
    return indices[1:], distances[1:]  # Exclude the point itself

def find_spherical_neighborhood(mesh, vertex, radius):
    vertices = np.asarray(mesh.vertices)
    kdtree = cKDTree(vertices)
    indices = kdtree.query_ball_point(vertex,radius)  # +1 to include the point itself
    return indices[1:]  # Exclude the point itself



def load_mesh(mesh_path):
    """Loads a mesh from a file."""
    return o3d.io.read_triangle_mesh(mesh_path, True)

def find_ply_files(directory):
    obj_files = glob.glob(os.path.join(directory, '*.ply'))
    return obj_files

def draw_result(source):
    o3d.visualization.draw_geometries([source])

def calculate_color(curr_color, neighbour_colors):
    color_tuples = np.array([tuple(color) for color in neighbour_colors])

    unique_colors, counts = np.unique(color_tuples, axis=0, return_counts=True)

    # Identify the most common color
    most_common_index = np.argmax(counts)
    most_common_color = unique_colors[most_common_index]
    count = counts[most_common_index]
    return most_common_color

def adjust_labels(source_mesh, neighbour_meshes,k, path):
    vertices = np.asarray(source_mesh.vertices)
    colors = np.asarray(source_mesh.vertex_colors)
    new_colors = np.asarray(source_mesh.vertex_colors)
    differences = np.asarray(source_mesh.vertex_colors)
    for i, vertex in enumerate(vertices):
        neighbour_colors = []
        for neighbour in neighbour_meshes:
            temp_colors = np.asarray(neighbour.vertex_colors)
            indices, distances = find_k_nearest_neighbors(neighbour, vertex, k)
            #indices = find_spherical_neighborhood(neighbour, vertex, k)
            for index in indices:
                neighbour_colors.append(temp_colors[index])

        color = calculate_color(colors[i], np.array(neighbour_colors))
        if np.all(colors[i]== color):
            differences[i] = np.asarray([0.5,0.5,0.5])
        else:
            differences[i] = np.asarray([1.0,0.0,0.0])

        #new_colors[i] = color

    source_temp = copy.deepcopy(source_mesh)
    source_temp.vertex_colors = o3d.utility.Vector3dVector(differences)
    #draw_result(source_temp)

    o3d.io.write_triangle_mesh(path, source_temp, write_ascii=True)



def generate_output_path(path, k):
    output_dir = f'D:\\studia\\doktorat\\segmentation\data\\Mirek\\Segmentation\\filter_edges\\diff\\{k}_n5'
    directory, filename = os.path.split(path)
    base_name, extension = os.path.splitext(filename)
    new_filename = f"{base_name}_filtered{extension}"
    new_file_path = os.path.join(output_dir, new_filename)
    return new_file_path


def process(meshes_path, n,k):
    paths = find_ply_files(meshes_path)
    #sort paths
    for i, current_path in enumerate(paths):
        curr_mesh = load_mesh(current_path)
        neighbour_meshes = []

        for j in range(1, n + 1):
            if i - j >= 0:
                neighbour_meshes.append(load_mesh(paths[i - j]))
        
        for j in range(1, n + 1):
            if i + j < len(paths):
                neighbour_meshes.append(load_mesh(paths[i + j]))
        new_path = generate_output_path(current_path,k)
        adjust_labels(curr_mesh, neighbour_meshes,k, new_path)
        print("Processed: " + new_path)

    

if __name__ == "__main__":
    path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned' 
    process(path, 5, 5)
