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


def load_mesh(mesh_path):
    """Loads a mesh from a file."""
    return o3d.io.read_triangle_mesh(mesh_path, True)

def find_ply_files(directory):
    # Use glob to find all .obj files in the directory
    obj_files = glob.glob(os.path.join(directory, '*.ply'))
    return obj_files

def draw_result(source, target):
    o3d.visualization.draw_geometries(source, target)

def calculate_color(curr_color, neighbour_colors):
    color_tuples = np.array([tuple(color) for color in neighbour_colors])

    unique_colors, counts = np.unique(color_tuples, axis=0, return_counts=True)

    # Identify the most common color
    most_common_index = np.argmax(counts)
    most_common_color = unique_colors[most_common_index]
    count = counts[most_common_index]
    return most_common_color

def adjust_labels(source_mesh, neighbour_meshes):
    vertices = np.asarray(source_mesh.vertices)
    colors = np.asarray(source_mesh.vertex_colors)
    new_colors5 = np.asarray(source_mesh.vertex_colors)
    new_colors20 = np.asarray(source_mesh.vertex_colors)
    new_colors50 = np.asarray(source_mesh.vertex_colors)
    for i, vertex in enumerate(vertices):
        neighbour_colors5 = []
        neighbour_colors20 = []
        neighbour_colors50 = []
        for neighbour in neighbour_meshes:
            temp_colors = np.asarray(neighbour.vertex_colors)
            indices5, distances5 = find_k_nearest_neighbors(neighbour, vertex, 5)
            indices20, distances20 = find_k_nearest_neighbors(neighbour, vertex, 20)
            indices50, distances50 = find_k_nearest_neighbors(neighbour, vertex, 50)
            for index in indices5:
                neighbour_colors5.append(temp_colors[index])
            for index in indices20:
                neighbour_colors20.append(temp_colors[index])
            for index in indices50:
                neighbour_colors50.append(temp_colors[index])
        # print(len(neighbour_colors5))
        # print(len(neighbour_colors20))
        # print(len(neighbour_colors50))
        new_color5 = calculate_color(colors[i], np.array(neighbour_colors5))
        new_color20 = calculate_color(colors[i], np.array(neighbour_colors20))
        new_color50 = calculate_color(colors[i], np.array(neighbour_colors50))
        # if not np.array_equal(new_color5,new_color20) or not np.array_equal(new_color5,new_color50) or not np.array_equal(new_color50,new_color20):
        #     print("5points:" + str(new_color5))
        #     print("20points:" + str(new_color20))
        #     print("50points:" + str(new_color50))
        new_colors5[i] = new_color5
        new_colors20[i] = new_color20
        new_colors50[i] = new_color50


    return new_colors5,new_colors20,new_colors50  


def generate_output_path(path):
    output_dir20 = 'D:\\studia\\doktorat\\segmentation\data\\Mirek\\Segmentation\\filter_edges\\20_n2'
    output_dir5 = 'D:\\studia\\doktorat\\segmentation\data\\Mirek\\Segmentation\\filter_edges\\5_n2'
    output_dir50 = 'D:\\studia\\doktorat\\segmentation\data\\Mirek\\Segmentation\\filter_edges\\50_n2'
    directory, filename = os.path.split(path)
    base_name, extension = os.path.splitext(filename)
    new_filename = f"{base_name}_filtered{extension}"
    new_file_path5 = os.path.join(output_dir5, new_filename)
    new_file_path20 = os.path.join(output_dir20, new_filename)
    new_file_path50 = os.path.join(output_dir50, new_filename)

    return new_file_path5, new_file_path20, new_file_path50


def process(meshes_path, n):
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

        #print(len(neighbour_meshes))

        adjusted5, adjusted20, adjusted50 = adjust_labels(curr_mesh, neighbour_meshes)
        new_path5, new_path20, new_path50 = generate_output_path(current_path)

        source_temp = copy.deepcopy(curr_mesh)
        source_temp.vertex_colors = o3d.utility.Vector3dVector(adjusted5)
        o3d.io.write_triangle_mesh(new_path5, source_temp, write_ascii=True)

        source_temp2 = copy.deepcopy(curr_mesh)
        source_temp2.vertex_colors = o3d.utility.Vector3dVector(adjusted20)
        o3d.io.write_triangle_mesh(new_path20, source_temp2, write_ascii=True)

        source_temp3 = copy.deepcopy(curr_mesh)
        source_temp3.vertex_colors = o3d.utility.Vector3dVector(adjusted50)
        o3d.io.write_triangle_mesh(new_path50, source_temp3, write_ascii=True)
        print("Processed: " + new_path5)




if __name__ == "__main__":
    path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned' 
    process(path, 2)
    # source_path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned\\00000003.ply'
    # paths = [
    #     'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned\\00000001.ply',
    #     'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned\\00000002.ply',
    #     'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned\\00000004.ply',
    #     'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned\\00000005.ply'
    # ]
    # curr_mesh = load_mesh(source_path)
    # meshes = [load_mesh(path) for path in paths]
    # adjust_labels(curr_mesh, meshes)