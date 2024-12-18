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
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans

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

def sort_by_closest_distance(points):
    # Copy of points to work on
    points = points.copy()
    num_points = len(points)
    
    # Start with the first point
    sorted_points = [points[0]]
    points = np.delete(points, 0, axis=0)  # Remove the first point
    
    while len(sorted_points) < num_points:
        last_point = sorted_points[-1]
        # Compute distances to all remaining points
        distances = np.linalg.norm(points - last_point, axis=1)
        closest_idx = np.argmin(distances)
        
        # Append the closest point to the sorted list
        sorted_points.append(points[closest_idx])
        # Remove the closest point from the remaining points
        points = np.delete(points, closest_idx, axis=0)
    
    return np.array(sorted_points)

def downsample(points):
    n_clusters = 20  # Number of simplified points
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(points)

    # Simplified points are the cluster centers
    return kmeans.cluster_centers_


    # point_cloud = o3d.geometry.PointCloud()
    # point_cloud.points = o3d.utility.Vector3dVector(points)

    # voxel_size = 1000  # Adjust voxel size for coarser or finer simplification
    # downsampled_pcd = point_cloud.voxel_down_sample(voxel_size=voxel_size)

    #return point_cloud.points

def calculate_spline(points):
    pts = np.asarray(downsample(points))
    sorted_points = sort_by_closest_distance(pts)
    arr_list = sorted_points.tolist()
    arr_list.append(sorted_points[0])
    arr_new = np.array(arr_list)
    #out = np.asarray(np.append(sorted_points, sorted_points[0]))
    x1 = [val[0] for val in points]
    y1 = [val[1] for val in points]
    z1 = [val[2] for val in points]

    x = [val[0] for val in arr_new]
    y = [val[1] for val in arr_new]
    z = [val[2] for val in arr_new]

    tck, u = splprep([x, y, z], s=7000)  # s is the smoothing factor
    u_fine = np.linspace(0, 1, 500)
    x_spline, y_spline, z_spline = splev(u_fine, tck)

    # Plot noisy points and fitted spline
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x1, y1, z1, color='red', label='Noisy Data')
    ax.plot(x_spline, y_spline, z_spline, color='blue', label='Fitted Curve')
    ax.legend()
    plt.show()

def calculate_mean_RMS_to_spline(data):
    # Extract x, y, z
    #x, y, z = points[:, 0], points[:, 1], points[:, 2]
    points = sorted(data, key=lambda v: v[0])
    x, y, z = points.T
    # x = [p[0] for p in points]
    # y = [p[0] for p in points]
    # z = [p[0] for p in points]


    # Parameterize points using arc-length
    tck, u = splprep([x, y, z], s=0)  # s is the smoothing factor

    # Evaluate the spline at the original parameter values
    x_fitted, y_fitted, z_fitted = splev(u, tck)
    fitted_points = np.vstack((x_fitted, y_fitted, z_fitted)).T

    # Compute RMS error
    errors = np.linalg.norm(points - fitted_points, axis=1)  # Euclidean distances
    rms_error = np.sqrt(np.mean(errors**2))

    # Compute average distance (mean error for context)
    mean_error = np.mean(errors)

    return mean_error

def plot_data(original_data, filtered_data, edge_labels, charts_path, val):
    val_map = {
        "5": "n=1 p=5", 
        "20": "n=1 p=20", 
        "50": "n=1 p=50", 
        "5_n2": "n=2 p=5",  
        "20_n2": "n=2 p=20", 
        "50_n2": "n=2 p=50", 
        "5_n3": "n=3 p=5",  
        "20_n3": "n=3 p=20",  
        "50_n3": "n=3 p=50", 
        "5_n5": "n=5 p=5", 
        "20_n5": "n=5 p=20",  
        "50_n5": "n=5 p=50"
    }


    m = edge_labels.keys()
    for k in m:
        head_centroids = [item[k] for item in original_data]
        head_centroids2 = [item[k] for item in filtered_data]

        keys = [i for i in range(len(head_centroids))]

        x_values = [val[0] for val in head_centroids]
        y_values = [val[1] for val in head_centroids]
        z_values = [val[2] for val in head_centroids]

        x_values2 = [val[0] for val in head_centroids2]
        y_values2 = [val[1] for val in head_centroids2]
        z_values2 = [val[2] for val in head_centroids2]

        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        axes[0].plot(keys, x_values, label='Original',color='blue', alpha=0.7)
        axes[0].plot(keys, x_values2, label='Filtered',color='red', alpha=0.7)
        axes[0].set_title("X Axis Values")
        axes[0].set_ylabel("X")
        axes[0].legend()

        axes[1].plot(keys, y_values, label='Original', color='blue', alpha=0.7)
        axes[1].plot(keys, y_values2, label='Filtered',color='red', alpha=0.7)
        axes[1].set_title("Y Axis Values")
        axes[1].set_ylabel("Y")
        axes[1].legend()

        axes[2].plot(keys, z_values,label='Original', color='blue', alpha=0.7)
        axes[2].plot(keys, z_values2,label='Filtered', color='red', alpha=0.7)
        axes[2].set_title("Z Axis Values")
        axes[2].set_xlabel("Frame")
        axes[2].set_ylabel("Z")
        axes[2].legend()
        fig.suptitle(f"RMS: {edge_labels[k]} {val_map[val]}", fontsize=16)  # Set a global title for the figure
        plt.tight_layout()
        plt.savefig(f"{charts_path}/{val}/{edge_labels[k]}.png")
        #plt.show()
        plt.close()
       

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

    


    data = []
    paths = find_ply_files(meshes_path)
    for p in range(20):
        mesh = load_mesh(paths[p])
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
        val = [calculate_spline(points) for points in clusters]
        
        for i, label in enumerate(labels):
            centroid = centroids[label]
            key = find_closest_centroid(centroid, target_centroids)
            new_colors[l_indices[i]] = color_map.get(key)
        new_centroids = {id: np.asarray([0, 0, 0]) for _ in range(len(target_centroids))} 
        temp_rms = {id: np.asarray([0, 0, 0]) for _ in range(len(target_centroids))}      
        for centroid in centroids:
            key = find_closest_centroid(centroid, target_centroids)
            temp_rms[key] = calculate_rms(clusters[key], centroid)
            print(clusters[key])
            mean_rms = calculate_mean_RMS_to_spline(clusters[key])
            print(mean_rms)
            new_centroids[key] = centroid
        #print(centroids)

        mesh.vertex_colors = o3d.utility.Vector3dVector(np.asarray(new_colors))
        #draw_result(mesh)
        target_centroids = new_centroids 
        #data.append(new_centroids)
        data.append(temp_rms)


    

        # o3d.io.write_triangle_mesh(new_path50, source_temp3, write_ascii=True)
        # print("Processed: " + new_path5)
    return data



if __name__ == "__main__":
    edge_labels = {
        0: "Hips", 
        1: "Left Elbow", 
        2: "Left Shoulder", 
        3: "Right Shoulder", 
        4: "Neck", 
        5: "Left Knee", 
        6: "Right Wrist", 
        7: "Right Knee", 
        8: "Right Elbow", 
        9: "Left Ankle", 
        10: "Left Writst", 
        11: "Right Ankle"
    }
    values = ["5", "20", "50","5_n2", "20_n2", "50_n2","5_n3", "20_n3", "50_n3", "5_n5", "20_n5", "50_n5"]

    original_path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\aligned'
    charts_path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\charts_rms'
    filtered_path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\filter_edges'   
    original_data = process(original_path)
    
    # for val in values:
    #     filtered_data = process(f"{filtered_path}/{val}")
    #     plot_data(original_data, filtered_data, edge_labels, charts_path, val)

