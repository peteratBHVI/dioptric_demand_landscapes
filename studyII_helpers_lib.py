"""
Author: p.wagner@bhvi.org / p.wagner@unsw.edu.au

Purpose:
- easy data access
- easy data visualization

"""
import pandas as pd
import numpy as np

import os, sys, json

from datetime import datetime

import plotly.express as px
# import glob
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg
# import plotly.graph_objects as go


class DataAccess:

    def __init__(self, fp_fn_logbook, px_ids, rec_types, path_recordings):
        self.fp_fn_logbook = fp_fn_logbook
        self.px_ids = px_ids
        self.rec_types = rec_types
        self.path_recordings = path_recordings

        self.log_master = pd.read_excel(self.fp_fn_logbook, sheet_name='master', index_col=0, engine='xlrd')
        self.subject_ids = self.get_subject_ids(self.log_master, self.px_ids)
        self.px_rec_fp = self.get_px_rec_fp(self.log_master, self.px_ids, self.path_recordings)
        self.rec_fp = self.get_rec_fp(self.log_master, self.px_ids, self.path_recordings, self.rec_types)

    @staticmethod
    def get_scan_time(df, scan_number):
        data_no_col_idx = df.loc[0, :].index[df.loc[0, :].values == 'Data No.'][0]
        idx = df.iloc[:, data_no_col_idx][df.iloc[:, data_no_col_idx].values == str(scan_number)].index[0]
        capture_date_col_idx = df.loc[0, :].index[df.loc[0, :].values == 'Capture Date'][0]
        capture_time_col_idx = df.loc[0, :].index[df.loc[0, :].values == 'Capture Time'][0]

        date_time = df.iloc[idx, capture_date_col_idx].replace(" ", "") + '/' + df.iloc[idx, capture_time_col_idx]
        return date_time

    def get_subject_ids(self, log_master, px_ids):
        subject_ids_col_names = []
        for px_id in px_ids:
            for col_name in self.log_master.columns:
                if self.log_master.loc['px_id', col_name] == px_id:
                    subject_ids_col_names.append(col_name)

        subject_ids = log_master.loc['subject', subject_ids_col_names].reset_index(drop=True)
        return subject_ids

    def get_px_rec_fp(self, log_master, px_ids, recording_path):
        rec_fp = list()
        fp = []
        # find all in folders for participants
        for px_id in px_ids:
            for col_name in log_master.columns:
                if log_master.loc['px_id', col_name] == px_id:
                    rec_date = log_master.loc['date', col_name]
                    fp = os.path.join(recording_path, rec_date)

                    if os.path.isdir(fp):
                        rec_fp.append(fp)
                    else:
                        print(fp, ' not recoreded')
        return rec_fp

    def get_rec_fp(self, log_master, px_ids, recording_path, rec_types):
        rec_fp = list()
        fp = []
        # find all in folders for participants
        for px_id in px_ids:
            for rec_type in rec_types:
                for col_name in log_master.columns:
                    if log_master.loc['px_id', col_name] == px_id:
                        rec_date = log_master.loc['date', col_name]
                        for folder in log_master.loc[rec_type, col_name].split(', '):
                            fp = os.path.join(recording_path, rec_date, folder.strip('\\'))

                            if os.path.isdir(fp):
                                rec_fp.append(fp)
                            else:
                                print(fp, ' not recorded')
        return rec_fp


class VisualizeData:

    @staticmethod
    def display_dioptric_map(display_data, save_file=False, output_fpn=None):
        # creating a accumulative map of dioptric landscape
        fig = px.imshow(display_data,
                        title='Accumulated dioptric landscape from participant vantage point over a period of one hour',
                        labels=dict(x='Horizontal decentration from fovea in degrees [°]',
                                    y='Vertical decentration from fovea in degrees [°]',
                                    color="Dioptres [D]",
                                    ),
                        x=np.array([float(x) * 0.278 for x in range(0, 448)]) - 62,
                        y=-1 * np.array([float(x) * 0.2647 for x in range(0, 342)]) + 45,

                        )
        fig.update_xaxes(side="bottom")
        fig.update_yaxes(autorange=True)

        fig.update_coloraxes(cmin=0, cmax=5, colorbar_title_side='right',
                             colorscale=[[0.0, "rgb(  0, 75,  0)"],
                                         [0.1, "rgb( 50,125,  0)"],
                                         [0.2, "rgb(175,175,  0)"],
                                         [0.3, "rgb(225,200,  0)"],
                                         [0.4, "rgb(250,150, 75)"],
                                         [0.5, "rgb(250, 75, 75)"],
                                         [0.6, "rgb(200, 25, 50)"],
                                         [0.7, "rgb(150,  0, 25)"],
                                         [0.8, "rgb(100,  0,  0)"],
                                         [0.9, "rgb( 50,  0,  0)"],
                                         [1.0, "rgb( 25,  0,  0)"]],
                             colorbar_tickfont=dict(size=18, ),
                             colorbar_title_font=dict(size=18, ),
                             )

        fig.update_layout(title_font_size=24,
                          autosize=True,
                          width=1200, height=900,
                          margin=dict(l=10, r=10, b=10, t=40),
                          )
        fig.update_xaxes(title_font=dict(size=22, ), tickfont=dict(size=18), )
        fig.update_yaxes(title_font=dict(size=22, ), tickfont=dict(size=18), )

        if save_file:
            fig.write_image(output_fpn)
        else:
            fig.show()

    @staticmethod
    def display_dioptric_map_residual(display_data, save_file=False, output_fpn=None):
        # creating a accumulative map of dioptric landscape
        fig = px.imshow(display_data,
                        title='Accumulated dioptric landscape - residual from central gaze',
                        labels=dict(x='Horizontal decentration from fovea in degrees [°]',
                                    y='Vertical decentration from fovea in degrees [°]',
                                    color="Dioptres [D]",
                                    ),
                        # pixels to degrees translation
                        x=np.array([float(x) * 0.278 for x in range(0, 448)]) - 62,
                        y=-1 * np.array([float(x) * 0.2647 for x in range(0, 342)]) + 45,

                        )
        fig.update_xaxes(side="bottom")
        fig.update_yaxes(autorange=True)

        fig.update_coloraxes(
                            cmid=0,
                            colorbar_title_side='right',
                            colorscale='RdYlGn',
                            colorbar_tickfont=dict(size=18, ),
                            colorbar_title_font=dict(size=18, ),
                            reversescale=True
                             )

        fig.update_layout(title_font_size=24,
                          autosize=True,
                          width=1200, height=900,
                          margin=dict(l=10, r=10, b=10, t=40),
                          )
        fig.update_xaxes(title_font=dict(size=22, ), tickfont=dict(size=18), )
        fig.update_yaxes(title_font=dict(size=22, ), tickfont=dict(size=18), )

        if save_file:
            fig.write_image(output_fpn)
        else:
            fig.show()


    @staticmethod
    def display_dioptric_map_counter(display_data, save_file=False, output_fpn=None):
        # creating map of pointcloud counter for each recording
        # create a new colour map to show no gaze data
        # from matplotlib import imshow
        from matplotlib import cm

        new_c_map = np.zeros((256, 3), dtype=float)
        for row_idx in range(0, 255):
            new_c_map[row_idx, 0:3] = cm.inferno(row_idx)[0:3]
        new_c_map = new_c_map * 255

        c_map_list = [[0.0, "rgb(  255, 255,  255)"], ]

        for row_idx in range(25, 255, 25):
            rgb = 'rgb(' + str(int(new_c_map[row_idx, 0])) + ',' + str(int(new_c_map[row_idx, 1])) + ',' + str(
                int(new_c_map[row_idx, 2])) + ')'
            new = [row_idx / 250, rgb]
            c_map_list.append(new)

        fig = px.imshow(display_data,
                        title='Point cloud count to determine accumulated dioptric landscape',
                        labels=dict(x='Horizontal decentration from fovea in degrees [°]',
                                    y='Vertical decentration from fovea in degrees [°]',
                                    color="pointcloud count [n]",
                                    ),
                        x=np.array([float(x) * 0.278 for x in range(0, 448)]) - 62,
                        y=-1 * np.array([float(x) * 0.2647 for x in range(0, 342)]) + 45,
                        )

        fig.update_xaxes(side="bottom")
        fig.update_yaxes(autorange=True)

        fig.update_coloraxes(
                            cmin=0,
                            cmax=np.nanmax(np.nanmax(display_data)),
                            colorbar_title_side='right',
                            colorscale=c_map_list,
                            colorbar_tickfont=dict(size=18, ),
                            colorbar_title_font=dict(size=18, ),
                             )

        fig.update_layout(title_font_size=24,
                          autosize=True,
                          width=1200, height=900,
                          margin=dict(l=10, r=10, b=10, t=40),
                          )
        fig.update_xaxes(title_font=dict(size=22, ), tickfont=dict(size=18), )
        fig.update_yaxes(title_font=dict(size=22, ), tickfont=dict(size=18), )

        if save_file:
            fig.write_image(output_fpn)
            print('dioptric landscape created as png')
        else:
            fig.show()


class PoR_Data:

    @staticmethod
    def check_source_f(folder):
        # check if all source files are available
        fns = [folder + '\\info.player.json',
               folder + r'\exports\000\gaze_positions.csv',
               folder + r'\exports\000\pupil_positions.csv',
               folder + r'\gaze_depth.csv']

        if not all([os.path.isfile(fn) for fn in fns]):

            for fn in fns:
                if not os.path.isfile(fn):
                    print(fn)

            sys.exit("Source files missing ")
        # else:
        #     print("Check_Source_f: All source files present")

    @staticmethod
    def pupil_rec_sync_time(fp):

        with open(os.path.join(fp, 'info.player.json')) as json_file:
            info_data = json.load(json_file)
            recording_start_time_synced = float(info_data["start_time_synced_s"])

        return recording_start_time_synced

    @staticmethod
    def distance_to_point_of_regard(fps):
        # iterates through depth_data.csv files for each recording and participant
        if len(fps) >1:
            for fp in fps:
                if 'gaze_data' in locals():
                    offset = gaze_data['gaze_timestamp'].iloc[-1]
                    print(offset)
                    gaze_depth_data_, gaze_data_ = PoR_Data.distance_to_point_of_regard_basics(fp, offset_time=offset)
                    gaze_depth_data = gaze_depth_data.append(gaze_depth_data_, ignore_index=True, sort=False)
                    gaze_data = gaze_data.append(gaze_data_, ignore_index=True, sort=False)
                else:
                    offset = 0
                    gaze_depth_data, gaze_data = PoR_Data.distance_to_point_of_regard_basics(fp, offset_time=0)

        else:
            gaze_depth_data, gaze_data = PoR_Data.distance_to_point_of_regard_basics(fps[0], offset_time=0)

        return gaze_depth_data, gaze_data

    @staticmethod
    def distance_to_point_of_regard_basics(fp, offset_time=0):
        PoR_Data.check_source_f(fp)
        recording_start_time_synced = PoR_Data.pupil_rec_sync_time(fp)

        # testing the depth data
        # #load gaze_depth.csv
        gaze_depth_data = pd.read_csv(os.path.join(fp, r'gaze_depth.csv'))

        # set gaze_ts relative to recording_start_time_system by deducting recording_start_time_synced
        gaze_depth_data[["gaze_ts", "frame_timestamp"]] = gaze_depth_data[["gaze_ts", "frame_timestamp"]] \
                                                          - recording_start_time_synced + offset_time
        gaze_depth_data[["gaze_ts", "frame_timestamp"]] = gaze_depth_data[["gaze_ts", "frame_timestamp"]].round(6)

        # # check if matching gaze confidence is high, if not exclude and record low confidence
        gaze_data = pd.read_csv(os.path.join(fp, r'exports\000\gaze_positions.csv'))

        # # set gaze_data relative to recording_start_time_system by deducting recording_start_time_synced
        # # offset_time just concatenate multiple recordings and eliminates time between recordings if present
        gaze_data["gaze_timestamp"] = gaze_data["gaze_timestamp"] - recording_start_time_synced + offset_time
        gaze_data["gaze_timestamp"] = gaze_data["gaze_timestamp"].round(6)

        for idx, ts in enumerate(pd.unique(gaze_depth_data["gaze_ts"])):
            # find closest gaze timestamp in depth and gaze data
            match_idx_depth_data = gaze_depth_data[gaze_depth_data.gaze_ts == ts].index
            min_idx = abs(gaze_data.gaze_timestamp - ts).idxmin()
            gaze_depth_data.loc[match_idx_depth_data, 'gaze_confidence'] = gaze_data.loc[min_idx, 'confidence']

        gaze_depth_data_high_confi = pd.unique(gaze_depth_data[gaze_depth_data["gaze_confidence"] >= 0.8].gaze_ts)

        gaze_depth_data_low_confi = pd.unique(gaze_depth_data[gaze_depth_data["gaze_confidence"] < 0.8].gaze_ts)

        # # in  gaze_depth_data unique timestamps for low confidence set  ["depth_confidence", "priority"] = [0 , 0.5]
        for uniqueTS in gaze_depth_data_low_confi:
            uniqueTS_index = gaze_depth_data.index[gaze_depth_data["gaze_ts"] == uniqueTS]
            gaze_depth_data.loc[uniqueTS_index[0], "depth_confidence"] = 0
            gaze_depth_data.loc[uniqueTS_index[0], "priority"] = .5

        # # set filters in high gaze_confidence data
        for uniqueTS in gaze_depth_data_high_confi:

            # find index for data with same unique timestamp in gaze_depth_data
            uniqueTS_index = gaze_depth_data.index[gaze_depth_data["gaze_ts"] == uniqueTS]

            # find overexposure in smallest radius and set priority to 1
            perc_over_exp = gaze_depth_data.loc[uniqueTS_index[0], "point_overexposed"] / gaze_depth_data.loc[
                uniqueTS_index[0], "total_point_count"]
            if perc_over_exp > 0.5:
                gaze_depth_data.loc[uniqueTS_index, "depth_confidence"] = (
                        gaze_depth_data.loc[uniqueTS_index, "point_overexposed"] /
                        gaze_depth_data.loc[uniqueTS_index, "total_point_count"] /
                        gaze_depth_data.loc[uniqueTS_index, "depth_stddev"]
                )

                gaze_depth_data.loc[pd.idxmax(gaze_depth_data.loc[uniqueTS_index, "depth_confidence"]), "priority"] = 1

            # radius 2 / 4 no depth data - set to distant data
            elif gaze_depth_data.loc[uniqueTS_index[0], "radius"] > 4:
                # add row in dataframe and copy
                gaze_depth_data = gaze_depth_data.append(
                    {"frame_timestamp": gaze_depth_data.loc[uniqueTS_index[0], "frame_timestamp"],
                     "gaze_ts": gaze_depth_data.loc[uniqueTS_index[0], "gaze_ts"],
                     "frame_idx": gaze_depth_data.loc[uniqueTS_index[0], "frame_idx"],
                     "tag": gaze_depth_data.loc[uniqueTS_index[0], "tag"],
                     "radius": 1,
                     "mask_size_pixels": 13,
                     "point_percentage": 1,
                     "point_overexposed": 0,
                     "point_missing": 0,
                     "depth_mean": 5.0,
                     "gaze_confidence": gaze_depth_data.loc[uniqueTS_index[0], "gaze_confidence"],
                     "depth_confidence": 1,
                     "priority": 0.8},
                    ignore_index=True)

            # data points with high point inclusions > .2 take smallest radius
            elif gaze_depth_data.loc[uniqueTS_index[0], "point_percentage"] > .2:
                gaze_depth_data.loc[uniqueTS_index[0], "priority"] = 1
            else:
                gaze_depth_data.loc[uniqueTS_index[1], "priority"] = 1

        # depth data within range 0.14- 4.8 m
        gaze_depth_data.loc[gaze_depth_data['depth_mean'] >= 5.01, 'depth_mean'] = 5.01

        # sort depth data
        gaze_depth_data = gaze_depth_data.sort_values(by=['frame_timestamp'], ).reset_index()

        # # fixation_ident = 0 == no fixation, 1 == fixation
        gaze_depth_data['fixation_ident'] = 0
        f_data = pd.read_csv(os.path.join(fp, r'exports\000\fixations.csv'), index_col='id')
        for idx in range(1, len(f_data)):
            f_start_time = f_data.loc[idx, 'start_timestamp'] - recording_start_time_synced + offset_time
            f_end_time = f_data.loc[idx, 'start_timestamp'] + f_data.loc[idx, 'duration'] - recording_start_time_synced + offset_time
                            
            gaze_depth_data.loc[(gaze_depth_data['frame_timestamp'] > f_start_time) &
                                (gaze_depth_data['frame_timestamp'] < f_end_time),
                                'fixation_ident'] = 1
        return gaze_depth_data, gaze_data

    @staticmethod
    def dioptric_translation_lib(task):
        lib = pd.DataFrame([('watching TV', 1),
                            ('conversation', 1),

                            ('playing board games', 2),
                            ('using computer', 2),

                            ('reading print', 3),
                            ('drawing', 3),
                            ('painting', 3),
                            ('writing', 3),
                            ('using hand-held device', 3), ]

                           , columns=('type', 'D_value')
                           )
        if lib.loc[:, 'type'].isin([task, ]).any():

            return_value = lib.loc[lib.type == task, 'D_value'].values[0]
        else:
            return_value = 0
            print(task + ' task not in list')
        return return_value