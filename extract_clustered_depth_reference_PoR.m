
% % % %  
% """
% (*)~---------------------------------------------------------------------------
% author: p.wagner@unsw.edu.au / p.wagner@bhvi.org
% 
% extract depth data with reference to estimated gaze 
%   - matching pointcloud and gaze data 
%   - cluster depth data from point cloud with 3x3 clusters 
% 
% dependencies:
%     - need to be extracted per participant!!! individually 
%     - extract_depth_data(.... )
%     - recoridng_fp == filepath of recording folder 
%     - disp_pointcloud - visualize point cloud (very slow but looks good) 
% ---------------------------------------------------------------------------~(*)
% """
% % %   


function extract_clustered_depth_reference_PoR(pxs)
recordings_fp = 'E:\PupilLabsRecordings'; 
% pxs =3;
identifier = "rec_folder_free";



% get meta data e.g. recording(s) fp and fn, pointcloud ts and fixation
rec_fps = studyII_helpers_lib.get_eyetracking_recording_fps(recordings_fp, pxs, identifier) 
px_rec_fp = split(rec_fps(1), '\');
output_fpn = join([join(px_rec_fp(1:3), '\'), 'clustered_depth_data_with_reference_PoR.csv'], '\');

% set up depth map variable and counter for legit data
depth_data_por = zeros(2 * 171, 2 * 224);
depth_data_por_counter = zeros(2 * 171, 2 * 224); 
world_frame_idx = 0;
disp_pointcloud = false;

% check if extraction has been done before 
% % fp for depth_data_por with fn "clustered_depth_data_with_reference_PoR.csv" 

% if ~isfile(output_fpn)
    % iterate through all recordings belonging to the 1 hours study 
    for rec_idx = 1 : length(rec_fps)
        % get world_ts_data for one recording 
        world_ts_data = studyII_helpers_lib.fixation_annotated_worldTS(rec_fps(rec_idx));
        % find all 'pointcloud*.rrf' for one recording 
        pc_fp_n = dir(fullfile(rec_fps(rec_idx), 'pointcloud*.rrf'));
        % find pointclouds that do not contain depth data and take off the
        % list
        idx_no_pc_data = find([pc_fp_n.bytes] < 200000);
        pc_fp_n(idx_no_pc_data) = [];
        if numel(pc_fp_n) > 1
            rrf_fns = [pc_fp_n(1).name,  natsortfiles({pc_fp_n(2:end).name})]; 
        else 
            rrf_fns = pc_fp_n.name;
        end
        % call extract_clustered_depth_data.m function to get clustered
        % depth data, depth data por and counter need to be passed in since
        % they are continious inbtween point clouds and recordings 
        if ~iscell(rrf_fns)
            rrf_fpn = [pc_fp_n(1).folder, '\', rrf_fns]
            [depth_data_por, depth_data_por_counter, world_frame_idx] = extract_clustered_depth_data(...
                rrf_fpn, world_ts_data, depth_data_por, depth_data_por_counter, disp_pointcloud, world_frame_idx);
        else 
            for idx = 1:length(rrf_fns)
                rrf_fpn = char(join([pc_fp_n(1).folder,rrf_fns(idx)], '\'))
            % check size of pointclould 
                [depth_data_por, depth_data_por_counter, world_frame_idx] = extract_clustered_depth_data(...
                    rrf_fpn, world_ts_data, depth_data_por, depth_data_por_counter, disp_pointcloud, world_frame_idx);
            end 
        end
        
    end
    fprintf("computation completed \n");
    
    % determine mean for depth map 
    depth_data_por = depth_data_por ./ depth_data_por_counter;
    
    % write to output file 
    csvwrite(output_fpn, depth_data_por)
    output_fpn_counter = join([join(px_rec_fp(1:3), '\'), 'clustered_depth_data_PoR_counter.csv'], '\');
    csvwrite(output_fpn_counter, depth_data_por_counter)
    % write report 
    depth_por_report = portcreate_depth_at_por_report(identifier, world_frame_idx, world_ts_data, max(max(depth_data_por_counter)));
    cell2csv(join([join(px_rec_fp(1:3), '\'), 'depth_por_report.csv'], '\'), depth_por_report)
    fprintf('files saved!\n');

% else 
%     fprintf("completed previously \n");
% end
end 
function depth_por_report = portcreate_depth_at_por_report(identifier, world_frame_idx, world_ts_data, pc_counter)
    
    depth_por_report =  strings([5 , 2]);
    
    depth_por_report(1,1) =  'recording identifier:';
    depth_por_report(1,2) =  identifier;
    depth_por_report(2,1) =  'world frame index count:';
    depth_por_report(2,2) =  string(world_frame_idx);
    depth_por_report(3,1) =  'gaze data points count:';
    depth_por_report(3,2) =  string(length(world_ts_data));
    depth_por_report(4,1) =  'gaze data identified as fixations:';
    depth_por_report(4,2) =  string(length(world_ts_data(~isnan(world_ts_data(:,8)))));    
    depth_por_report(5,1) =  'max value of depth_data_por_counter:';
    depth_por_report(5,2) =  string(pc_counter);  
    
end 
