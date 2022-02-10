function [por_depth_data, por_depth_data_counter, world_frame_idx] = extract_clustered_depth_data(...
    FileName, world_data, por_depth_data, por_depth_data_counter, disp_pointcloud, world_frame_idx)
%ROYALE_LEVEL1_SAMPLE3 - royale example #3:
% 

% % % %  
% """
% (*)~---------------------------------------------------------------------------
% amendments to ROYALE_LEVEL1_SAMPLE3 - royale example #3:
% author: p.wagner@unsw.edu.au / p.wagner@bhvi.org
% 
% find all target positions in point cloud of accuray recording  
%     data output: data talbe with all x y positions of all targets sorted 
% 
% dependencies:
%     - FileName == point cloud in accuracy recording folder 
%     - disp_pointcloud - visualize point cloud (very slow but looks good) 
% ---------------------------------------------------------------------------~(*)
% """
% % %   

% retrieve royale version information
royaleVersion = royale.getVersion();
fprintf('* royale version: %s\n',royaleVersion);

% open recorded file
manager = royale.CameraManager();
FileName
cameraDevice = manager.createCamera(FileName);
delete(manager);

cameraDevice.initialize();

% display some information about the connected camera
fprintf('====================================\n');
fprintf('        Camera information\n');
fprintf('====================================\n');
fprintf('Id:              %s\n',cameraDevice.getId());
fprintf('Type:            %s\n',cameraDevice.getCameraName());
fprintf('Width:           %u\n',cameraDevice.getMaxSensorWidth());
fprintf('Height:          %u\n',cameraDevice.getMaxSensorHeight());

% retrieve valid use cases
UseCases=cameraDevice.getUseCases();
fprintf('Use cases: %d\n',numel(UseCases));
fprintf('    %s\n',UseCases{:});
fprintf('====================================\n');

if (numel(UseCases) == 0)
    error('No use case available');
end

% configure playback
cameraDevice.loop(false);
cameraDevice.useTimestamps(false);

N_Frames= cameraDevice.frameCount();
fprintf('Retrieving %d frames...\n',N_Frames);

% start capture mode
cameraDevice.startCapture();

% initialize preview figure
hFig=figure('Name',...
    ['Preview: ',cameraDevice.getId(),' @ MODE_PLAYBACK'],...
    'IntegerHandle','off','NumberTitle','off');
colormap(jet(256));
TID = tic();
last_toc = toc(TID);
iFrame = 0;

while (ishandle(hFig)) && (iFrame < N_Frames) && ... 
        (world_frame_idx < length(world_data(:,1))) 
    % retrieve data from camera
    data = cameraDevice.getData();
    iFrame = iFrame + 1;
    world_frame_idx = world_frame_idx +1;
    if (mod(iFrame,100) == 0)
        this_toc=toc(TID);
        fprintf('FPS = %.2f\n',100/(this_toc-last_toc));
        fprintf('world_frame_idx = %.0f\n',(world_frame_idx));
        last_toc=this_toc;
    end
    
    % check for fixational eye movements 
    if world_data(world_frame_idx, 8) == 1

        % prepare data, calculate distance for all data points and 
        data_depth_map = sqrt(data.x.^2 + data.y.^2 + data.z.^2);
        [data_depth_map_filtered] = validation_filter(data_depth_map, data.grayValue, data.depthConfidence);     


        % mapping depth map with reference to gaze coordintaes
        [por_depth_data, por_depth_data_counter] = mapping_depth_data_to_por(...
            por_depth_data, por_depth_data_counter, world_data, world_frame_idx, data_depth_map_filtered);
    
    end 
  
        
        if disp_pointcloud
            set(0,'CurrentFigure',hFig);       
            my_image(por_depth_data,'depth data with found targets');
            drawnow;
        end     
 
end

% stop capture mode
fprintf('* Stopping capture mode...\n');
cameraDevice.stopCapture();
fprintf('* ...done!\n');
close all

end

function my_image(CData,Name)
% convenience function for faster display refresh:
%  only update 'CData' on successive image calls
%  (does not update title or change resolution!)
if ~isappdata(gca,'my_imagehandle')
    my_imagehandle = imagesc(CData);
    axis image
    title(Name);
    setappdata(gca,'my_imagehandle',my_imagehandle);
else
    my_imagehandle = getappdata(gca,'my_imagehandle');
    set(my_imagehandle,'CData',CData);
end
end


% % % find each target in each q and sort to target id
function [data_depth_map_mean] = validation_filter(dd_map, gray, confi)
    % set over exposed area to arbitrary 0.25 m
    [dd_map, confi] = set_overexposure_to_nearest_depth(dd_map, gray, confi);
    
    data_depth_map_mean = zeros(171,224);
    data_depth_map_mean(:) = 10;

    
    for row_idx = 3:169
        for col_idx = 3:222
            % within the area row_idx - 2 : row_idx + 2, col_idx - 2 : col_idx + 2 
            % percentage of missing data         
            valid_data_idx = find(dd_map(row_idx - 2 : row_idx + 2, col_idx - 2 : col_idx + 2) > 0.14 & ... 
                 confi(row_idx - 2 : row_idx + 2, col_idx - 2 : col_idx + 2) >= 25);
            % within the cluster min of 8 valid depth data is required to 
             if length(valid_data_idx) < 8
                data_depth_map_mean(row_idx, col_idx) = 5;
            else 
                mean_data = dd_map(row_idx - 2 : row_idx + 2, col_idx - 2 : col_idx + 2);
                data_depth_map_mean(row_idx, col_idx) = mean(mean_data(valid_data_idx));
            end
        end
    end
    data_depth_map_mean = 1./data_depth_map_mean;
end 


function [por_depth_data, por_depth_data_counter] = mapping_depth_data_to_por(...
        por_depth_data, por_depth_data_counter, world_data, world_frame_idx, data_depth)

    % adjust for gaze position and map at gaze centre 
    col_pos = int16(world_data(world_frame_idx, 6));
    row_pos = int16(world_data(world_frame_idx, 7));

    if col_pos >= 1 && col_pos <= 224 && row_pos >= 1 && row_pos <= 171
        x = 225 - col_pos;
        y = row_pos; % 86 - row_pos + 86, but row pos is in bottom left and need to be transfered to image space   
        por_depth_data(y : y + 170, x : x + 223) = por_depth_data(y : y + 170, x : x + 223) + data_depth;
        por_depth_data_counter(y : y + 170, x : x + 223) = por_depth_data_counter(y : y + 170, x : x + 223) +1;
    end
   
end 

function [data_depth_map, confi] = set_overexposure_to_nearest_depth(data_depth_map, gray, confi)
    % identify everexposed areas 
    arr = zeros(171, 224);
    over_exp_idx =  find(data_depth_map < 0.01 & gray > 500);
    arr(over_exp_idx) = 1;
    confi(over_exp_idx) = 25;
    % imshow(arr)

    % black and white (binary) connected component -> group true (1) values
    CC = bwconncomp(arr);
    for idx = 1 :length(CC.PixelIdxList)
        % estimate gravity point of overexposed area
        center_px = int32(median(CC.PixelIdxList{1,idx}));
        [row_idx, col_idx] = ind2sub(size(data_depth_map), center_px);
        % create mask to select data around overexposed data only
        [x, y] = meshgrid(linspace(1,224,224), linspace(1,171,171));
        for r = linspace(5, 55, 11)
            mask_area = (x - col_idx) .^2 + (y - row_idx).^2 <= r^2;
            % if % of valid data exceeds 20% or 50 data points 
            % set overexposed area to mean depth of valid data 
            ddm_mask = data_depth_map .* mask_area;
            valid_point_idx = find(ddm_mask > 0.14 );
            valid_point_perc = length(valid_point_idx) / sum(sum(mask_area));
            if (valid_point_perc > 0.05) 
                break
            elseif (length(valid_point_idx) > 50)
                break
            end
    %         imshow(mask_area)
        end

        mean_valid_points = mean(data_depth_map(valid_point_idx));
        data_depth_map(CC.PixelIdxList{1,idx}) = mean_valid_points;
        data_depth_map(valid_point_idx) = 0.8;
    %     imshow(data_depth_map)
    end
end

