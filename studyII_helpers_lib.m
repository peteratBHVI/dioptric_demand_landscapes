classdef studyII_helpers_lib
    %UNTITLED Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        Property1
    end
    
    methods (Static)
        %%% retrieves the filepath of the eye-tracking recording for participants
        %%% Arguments (pupil labs recording file path, participant index, kind of
        %%% recording as stated in the experiment_execution_logV.3.xlsx

        function [fp_data] = get_eyetracking_recording_fps(rec_fp, pxs, identifier)
            %Import the data from experiment_execution_logV.3.xlsx
            log_file_name = 'C:\Users\p.wagner\Documents\phd\study_II\participants\studyII_execution_log.xlsx';
            [~, ~, px_data] = xlsread(log_file_name , 'master', 'A1:AC28');

            px_data = string(px_data);
            px_data(ismissing(px_data)) = '';
            fp_data = string([]);
            for idx = 1 : length(pxs)
                row = find(px_data(:, 1) == identifier);
                col = find(px_data(3, :) == string(pxs(idx)));
                recordings = split(px_data(row, col), ', ');
                for idx2 = 1:length(recordings) 
                    fp_data_new = join([rec_fp, px_data(6, col), erase(recordings(idx2), '\')], '\');
                    fp_data = [fp_data; fp_data_new ];
                end 
            end
        end
        
        function world_TSs = fixation_annotated_worldTS(rec_fp)
            %METHOD1 Summary of this method goes here
            %   Detailed explanation goes here
            fprintf('aquire world timestamp and gaze data \n');
            tic
            % import world_timestamps and gaze data 
            world_TSs = readNPY(join([rec_fp, '\world_timestamps.npy'], ''));
            export_folder = dir(join([rec_fp, '\**\gaze_pos*.csv'], ''));
            [g_data, fileerror] = GetPupilLabCSVData.Gaze([export_folder.folder '\gaze_positions.csv']);
            if fileerror == 1
                fprintf('pupil labs export data e.g. gaze_positions.csv not found \n');
                
            end
            % sort gaze positions to world_frame timestamps 
            world_TSs(:,2:8) = nan;
            fprintf('%.2f seconds\n', toc)
            fprintf('calculating gaze coordintes for world timestamps \n');
            tic 
            for idx = 1:length(world_TSs(:,1))
                world_ts = world_TSs(idx,1);
                % get nearest gaze timestamp to world timestamp 
                [delta_t, gaze_idx] = min(abs(g_data(:,1) - world_ts));
                world_TSs(idx, 2) = delta_t;
                world_TSs(idx, 3) = gaze_idx;
                world_TSs(idx, 4) = g_data(gaze_idx, 1);

                world_TSs(idx, 5) = g_data(gaze_idx, 3);
                world_TSs(idx, 6) = g_data(gaze_idx, 4) * 224;
                world_TSs(idx, 7) = g_data(gaze_idx, 5) * 171;   
            end
            fprintf('%.2f seconds\n', toc)
            fprintf('annotate fixational eye movements \n');
            tic
            % import fixations file and world_timestamps with fixations 
            [f_data, ~] = GetPupilLabCSVData.FixationPL([export_folder.folder '\fixations.csv']);
            % for all times of fixations flag world_ts(:, 8)  == 1 
            for idx = 1 : length(f_data)
                f_start = f_data(idx, 2);
                f_end   = f_data(idx, 2) + f_data(idx, 3)/1000;
                % find all index of world_ts within range f_start to f_end 
                [fix_row_index] = find((world_TSs(:, 1) >= f_start) & (world_TSs(:, 1 ) <= f_end));
                world_TSs(fix_row_index, 8) = 1;
            end
            fprintf('%.2f seconds\n', toc)
        end
    end
end

