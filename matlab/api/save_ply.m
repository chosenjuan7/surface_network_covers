function save_ply(filename, V, T, C)
    % Save the mesh with vertices V, faces T, and vertex colors C into a .ply file

    % Open the file for writing
    fid = fopen(filename, 'w');
    if fid == -1
        error('Cannot open the file for writing.');
    end
    
   % Write the PLY header
    fprintf(fid, 'ply\n');
    fprintf(fid, 'format ascii 1.0\n');
    fprintf(fid, 'element vertex %d\n', size(V, 1));
    fprintf(fid, 'property float x\n');
    fprintf(fid, 'property float y\n');
    fprintf(fid, 'property float z\n');
    fprintf(fid, 'element face %d\n', size(T, 1));
    fprintf(fid, 'property list uchar int vertex_indices\n');
    fprintf(fid, 'property uchar red\n');
    fprintf(fid, 'property uchar green\n');
    fprintf(fid, 'property uchar blue\n');
    fprintf(fid, 'end_header\n');

    % Write vertices
    for i = 1:size(V, 1)
        fprintf(fid, '%f %f %f\n', V(i, 1), V(i, 2), V(i, 3));
    end

    % Write faces and associated face colors (scale colors to 0-255 range)
    for i = 1:size(T, 1)
        fprintf(fid, '3 %d %d %d %d %d %d\n', ...
            T(i, 1) - 1, T(i, 3) - 1, T(i, 2) - 1, ...
            round(C(i, 1) * 255), round(C(i, 2) * 255), round(C(i, 3) * 255));
    end

    % Close the file
    fclose(fid);
end