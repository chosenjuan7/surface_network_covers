import pymeshlab as ml
import glob
import os
import open3d as o3d
import numpy as np
import copy

def preprocess_point_cloud(pcd, voxel_size):
    print(":: Downsample with a voxel size %.3f." % voxel_size)
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius %.3f." % radius_normal)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius %.3f." % radius_feature)
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh

def execute_global_registration(source_down, target_down, source_fpfh,
                                target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is %.3f," % voxel_size)
    print("   we use a liberal distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(True),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ], o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    return result

def refine_registration(source, target, source_fpfh, target_fpfh, voxel_size, result_ransac):
    distance_threshold = voxel_size * 0.4
    print(":: Point-to-plane ICP registration is applied on original point")
    print("   clouds to refine the alignment. This time we use a strict")
    print("   distance threshold %.3f." % distance_threshold)
    result = o3d.pipelines.registration.registration_icp(
        source, target, distance_threshold, result_ransac.transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    return result

def load_mesh(mesh_path):
    """Loads a mesh from a file."""
    return o3d.io.read_triangle_mesh(mesh_path, True)

def find_ply_files(directory):
    # Use glob to find all .obj files in the directory
    obj_files = glob.glob(os.path.join(directory, '*.ply'))
    return obj_files

def draw_registration_result(source, target, transformation):
    source.paint_uniform_color([1,0,0])
    target.paint_uniform_color([0,1,0])
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([0,0,1])
    target_temp.paint_uniform_color([0,0,1])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source, target, source_temp])


def normalize(pcd1, pcd2):
    # Compute the bounding boxes for both point clouds
    bbox1 = pcd1.get_axis_aligned_bounding_box()
    bbox2 = pcd2.get_axis_aligned_bounding_box()

    # Calculate the extent (size) of each bounding box
    extent1 = bbox1.get_extent()
    extent2 = bbox2.get_extent()

    # Find the maximum extent for both point clouds (max dimension across all axes)
    max_extent1 = np.max(extent1)
    max_extent2 = np.max(extent2)

    # Normalize both point clouds to have the same bounding box size (scale to 1)
    
    #pcd2.scale(max_extent1, center=pcd2.get_center())

    return max_extent2 / max_extent1

def normalize_to_same_size(pcd1, pcd2):
    # Compute the bounding boxes for both point clouds
    bbox1 = pcd1.get_axis_aligned_bounding_box()
    bbox2 = pcd2.get_axis_aligned_bounding_box()

    # Calculate the extent (size) of each bounding box
    extent1 = bbox1.get_extent()
    extent2 = bbox2.get_extent()

    # Find the maximum extent for both point clouds (max dimension across all axes)
    max_extent1 = np.max(extent1)
    max_extent2 = np.max(extent2)

    # Normalize both point clouds to have the same bounding box size (scale to 1)
    pcd1.scale(1.0 / max_extent1, center=pcd1.get_center())
    pcd2.scale(1.0 / max_extent2, center=pcd2.get_center())

    return pcd1, pcd2



def align_meshes(source_mesh_path, target_mesh_path, output_path):

    voxel_size = 10
    """Aligns two meshes using the ICP algorithm and saves the aligned result."""
    # Load the source and target meshes
    source_mesh = load_mesh(source_mesh_path)
    target_mesh = load_mesh(target_mesh_path)

    
    # Convert meshes to point clouds (ICP works with point clouds)
    source_pcd = source_mesh.sample_points_uniformly(number_of_points=100000)
    target_pcd = target_mesh.sample_points_uniformly(number_of_points=100000)

    flip = np.array([[1,  0,  0, 0],   # x-axis remains the same
        [0, -1,  0, 0],   # y-axis is flipped
        [0,  0,  1, 0],   # z-axis remains the same
        [0,  0,  0, 1]])  # Homogeneous coordinate


    source_pcd.estimate_normals()
    target_pcd.estimate_normals()

    factor = normalize(source_pcd, target_pcd)
    source1 = source_pcd.scale(factor, center=source_pcd.get_center())
    source = source1.transform(flip)
    target = target_pcd#.scale(factor, center=target_pcd.get_center())
    #o3d.visualization.draw_geometries([source, target])
    
    source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    result_ransac = execute_global_registration(source_down, target_down,
                                            source_fpfh, target_fpfh,
                                            voxel_size)
    #print(result_ransac.transformation)
    #draw_registration_result(source, target, result_ransac.transformation)
    
    result_icp = refine_registration(source, target, source_fpfh, target_fpfh, voxel_size, result_ransac)
    #print(result_icp.transformation)
    #draw_registration_result(source, target, result_icp.transformation)


    source_n = source.transform(result_icp.transformation)
    factor2 = normalize(source_n, target_pcd)
    source_n_1 = source_n.scale(factor2, center=source_n.get_center())
    #o3d.visualization.draw_geometries([source_n_1, target])



    source_down, source_fpfh = preprocess_point_cloud(source_n_1, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

    result_ransac2 = execute_global_registration(source_down, target_down,
                                            source_fpfh, target_fpfh,
                                            voxel_size)
    #print(result_ransac.transformation)
    #draw_registration_result(source_n_1, target, result_ransac2.transformation)
    
    result_icp2 = refine_registration(source_n_1, target, source_fpfh, target_fpfh, voxel_size, result_ransac2)
    #print(result_icp.transformation)
    #draw_registration_result(source_n_1, target, result_icp2.transformation)

    res = source_mesh.scale(factor, center=source_mesh.get_center())
    res1 = res.transform(flip)
    res2 = res1.transform(result_icp.transformation)
    res3 = res2.scale(factor2, center=res2.get_center())
    res3 = res2.transform(result_icp2.transformation)
    o3d.io.write_triangle_mesh(output_path, res3, write_ascii=True)

    print(f"Mesh aligned and saved to {output_path}")


def generate_target_path(path):
    target_dir = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Meshes_simpliefied'
    directory, filename = os.path.split(path)
    base_name, extension = os.path.splitext(filename)
    new_filename = f"{base_name}.off"
    new_file_path = os.path.join(target_dir, new_filename)

    return new_file_path

def generate_output_path(path):
    output_dir = 'D:\\studia\\doktorat\\segmentation\data\\Mirek\\Segmentation\\aligned'
    directory, filename = os.path.split(path)
    base_name, extension = os.path.splitext(filename)
    new_filename = f"{base_name}_alligned{extension}"
    new_file_path = os.path.join(output_dir, new_filename)

    return new_file_path




def process(meshes_path):
    paths = find_ply_files(meshes_path)
    for path in paths:
        source_file = path
        target_file = generate_target_path(path)
        output_file = generate_output_path(path)
        align_meshes(source_file,target_file, output_file)




# Example usage
if __name__ == "__main__":
    #mesh1_path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\results_per_vertex\\00000003.ply'  # Replace with your path to the first mesh
    #mesh2_path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Meshes_simpliefied\\00000003.off'  # Replace with your path to the rotated and scaled mesh
    #output_path = 'D:\\studia\\doktorat\\segmentation\data\\Mirek\\Segmentation\\aligned\\00000003_alligned.ply'  # Replace with the path to save the aligned mesh


    path = 'D:\\studia\\doktorat\\segmentation\\data\\Mirek\\Segmentation\\results_per_vertex'  # Replace with your path to the first mesh

    #align_meshes(mesh1_path, mesh2_path , output_path)
    process(path)