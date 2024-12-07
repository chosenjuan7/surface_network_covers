import pymeshlab as ml
import glob
import os
import open3d as o3d
import numpy as np
import copy
from scipy.spatial import cKDTree
from collections import Counter
from pprint import pprint
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def load_mesh(mesh_path):
    return o3d.io.read_triangle_mesh(mesh_path, True)

def find_ply_files(directory):
    obj_files = glob.glob(os.path.join(directory, '*.ply'))
    return obj_files

def draw_result(source):
    o3d.visualization.draw_geometries([source])

def find_connected_points_with_different_colors(triangles, colors):  
    indices = []

    for tri in triangles:
        if not np.all(colors[tri[0]] == colors[tri[1]]):
            indices.append(tri[0])
            indices.append(tri[1])

        if not np.all(colors[tri[1]] == colors[tri[2]]):
            indices.append(tri[1])
            indices.append(tri[2])

        if not np.all(colors[tri[2]] == colors[tri[0]]):
            indices.append(tri[2])
            indices.append(tri[0])


    return set(indices)

def cluster_points(vertices):

    db = DBSCAN(eps=25, min_samples=5).fit(vertices)
    return db.labels_

def calculate_centroid(points):
    centroid = np.mean(points, axis=0)
    return centroid

def calculate_rms(points, centroid):
    squared_differences = (points - centroid) ** 2
    
    sum_squared_differences = np.sum(squared_differences, axis=1)
    
    rms_distances = np.sqrt(sum_squared_differences)

    return rms_distances

def group_vertices_by_labels(vertices, labels):
    unique_labels = set(labels)
    clusters = [[] for _ in range(len(unique_labels))]
    
    for id, label in enumerate(labels):
        clusters[label].append(vertices[id]) 
    
    return clusters

def find_closest_centroid(point, centroids):
    min_distance = float('inf') 
    for key, centroid in centroids.items():
        distance = np.linalg.norm(point - centroid)
        if distance < min_distance:
            min_distance = distance
            closest_key = key

    return closest_key

def process(meshes_path):
    color_map = {
        0: np.asarray([1.0, 0.0, 0.0]),  # Red
        1: np.asarray([0.0, 1.0, 0.0]),  # Green
        2: np.asarray([0.0, 0.0, 1.0]),  # Blue
        3: np.asarray([1.0, 1.0, 0.0]),  # Yellow
        4: np.asarray([1.0, 0.0, 1.0]),  # Magenta
        5: np.asarray([0.0, 1.0, 1.0]),  # Cyan
        6: np.asarray([0.5, 0.5, 0.5]),  # Gray
        7: np.asarray([1.0, 0.5, 0.0]),  # Orange
        8: np.asarray([0.5, 0.0, 0.5]),  # Purple
        9: np.asarray([0.0, 0.5, 0.5]),  # Teal
        10: np.asarray([0.5, 0.5, 0.0]),  # Olive
        11: np.asarray([0.8, 0.2, 0.2]),  # Crimson
        12: np.asarray([0.2, 0.8, 0.2]),  # Lime
        13: np.asarray([0.2, 0.2, 0.8]),  # Indigo
        14: np.asarray([0.9, 0.7, 0.1]),  # Gold
        15: np.asarray([0.1, 0.9, 0.7]),  # Turquoise
    }

    target_centroids = {
        0: np.asarray([ -8.35179832, 1000.67111352,   19.22533065]), 
        1: np.asarray([-339.02155592, 1355.80026284,  -54.19748538]), 
        2: np.asarray([-2.43567369e+02,  1.56555703e+03, -5.84144029e-01]), 
        3: np.asarray([ 191.0460319 , 1527.71710174,   31.96360247]), 
        4: np.asarray([ -25.29513209, 1741.674077  ,    4.71893587]), 
        5: np.asarray([-114.76136049,  653.81759925,   88.07160387]), 
        6: np.asarray([ 310.25582233, 1090.79390539,  -77.68779006]), 
        7: np.asarray([113.46736418, 666.51401367, -73.60542715]), 
        8: np.asarray([2.75779066e+02, 1.30620442e+03, 9.55226182e-01]), 
        9: np.asarray([-86.05128778, 270.5525032 , 120.02185958]), 
        10: np.asarray([-340.74679997, 1165.8049107 , -207.29018979]), 
        11: np.asarray([ 129.98632118,  282.9945748 , -159.78350696])
    }

    paths = find_ply_files(meshes_path)
    for path in paths:
        mesh = load_mesh(path)
        colors = np.asarray(mesh.vertex_colors)
        triangles = np.asarray(mesh.triangles)
        vertices = np.asarray(mesh.vertices)
        indices = find_connected_points_with_different_colors(triangles, colors)
        e_verts = []
        new_colors = [np.asarray([0.0,0.0,0.0]) for color in colors]

        for i in indices:
            e_verts.append(vertices[i])

        l_indices = list(indices)
        labels = cluster_points(e_verts)

        clusters = group_vertices_by_labels(e_verts, labels)
        centroids = [calculate_centroid(points) for points in clusters]
        
        for i, label in enumerate(labels):
            centroid = centroids[label]
            key = find_closest_centroid(centroid, target_centroids)
            new_colors[l_indices[i]] = color_map.get(key)
        new_centroids = {id: np.asarray([0, 0, 0]) for _ in range(len(target_centroids))}    
        for centroid in centroids:
            key = find_closest_centroid(centroid, target_centroids)
            new_centroids[key] = centroid
        #print(centroids)

        mesh.vertex_colors = o3d.utility.Vector3dVector(np.asarray(new_colors))
        draw_result(mesh)
        target_centroids = new_centroids


        

        # o3d.io.write_triangle_mesh(new_path50, source_temp3, write_ascii=True)
        # print("Processed: " + new_path5)




if __name__ == "__main__":

    path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned' 
    process(path)
