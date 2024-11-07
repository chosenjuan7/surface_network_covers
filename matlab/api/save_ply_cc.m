function save_ply_cc(filename, V, T, C)
    % Save the mesh with vertices V, faces T, and face colors C by averaging the
    % colors for each vertex from the adjacent faces.

    % V: Vertex coordinates Nx3
    % T: Face indices Mx3
    % C: Face colors Mx3 (one color per face)
    
    % Number of vertices
    num_vertices = size(V, 1);
    
    % Initialize vertex color matrix
    vertex_colors = zeros(num_vertices, 3);
    vertex_color_count = zeros(num_vertices, 1);  % To track how many faces contributed to each vertex
    
    % Iterate through faces and assign face colors to vertices
    for i = 1:size(T, 1)
        face_color = C(i, :);  % Color of the current face
        face_vertices = T(i, :);  % Indices of the vertices of the current face
        
        % Add the face color to each vertex of the face
        for j = 1:3
            vertex_idx = face_vertices(j);
            vertex_colors(vertex_idx, :) = face_color; %vertex_colors(vertex_idx, :); % + 
            % vertex_color_count(vertex_idx) = vertex_color_count(vertex_idx) + 1;
        end
    end
    
    % Average the colors for each vertex by dividing by the number of contributing faces
    %for i = 1:num_vertices
    %    if vertex_color_count(i) > 0
    %        vertex_colors(i, :) = vertex_colors(i, :) / vertex_color_count(i);
    %    end
    % end

    % Convert vertex colors to 0-255 scale for saving
    vertex_colors = round(vertex_colors * 255);

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
    fprintf(fid, 'property uchar red\n');
    fprintf(fid, 'property uchar green\n');
    fprintf(fid, 'property uchar blue\n');
    fprintf(fid, 'element face %d\n', size(T, 1));
    fprintf(fid, 'property list uchar int vertex_indices\n');
    fprintf(fid, 'end_header\n');

    % Write vertices along with their averaged vertex colors
    for i = 1:size(V, 1)
        fprintf(fid, '%f %f %f %d %d %d\n', ...
            V(i, 1), V(i, 2), V(i, 3), ...
            vertex_colors(i, 1), vertex_colors(i, 2), vertex_colors(i, 3));
    end

    % Write faces (PLY uses zero-based indexing)
    for i = 1:size(T, 1)
        fprintf(fid, '3 %d %d %d\n', T(i, 1) - 1, T(i, 2) - 1, T(i, 3) - 1);
    end

    % Close the file
    fclose(fid);
end