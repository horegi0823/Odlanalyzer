import os, csv, re, argparse
import pandas as pd
import subprocess

sha1_pattern = r'([a-fA-F0-9]{40})_Sha1_'

def Transform_to_cloud_status(odl_path):
    df = pd.read_csv(odl_path, encoding = 'UTF8', encoding_errors = 'ignore', header = 0)
    df = df.drop(['Filename', 'File_Index'], axis = 'columns')  
    df_len = len(df)
    df_DiskFileToDBHashComparer_DoWork = df[(df['Code_File'] == 'localChange.cpp') & (df['Function'] == 'DiskFileToDBHashComparer::DoWork')]
    if df_DiskFileToDBHashComparer_DoWork.empty: return
    df_DiskFileToDBHashComparer_DoWork_idx_list = df_DiskFileToDBHashComparer_DoWork.index.tolist()
    cnt = len(df_DiskFileToDBHashComparer_DoWork_idx_list)
    df_DiskFileToDBHashComparer_DoWork_idx_list.append(df_len)
    result = [["User behavior", "file_path", "file_name", "file_sha1", "timestamp"]]

    for idx in range(cnt):
        df_DiskFileToDBHashComparer_DoWork_idx = df_DiskFileToDBHashComparer_DoWork_idx_list[idx]
        df_DiskFileToDBHashComparer_DoWork_idx_next = df_DiskFileToDBHashComparer_DoWork_idx_list[idx + 1]
        df_tmp = df.iloc[df_DiskFileToDBHashComparer_DoWork_idx:df_DiskFileToDBHashComparer_DoWork_idx_next]

        df_ActivityItemsModel_AddItemToHistory = df_tmp[(df_tmp['Code_File'] == 'ActivityItemsModel.cpp') & (df_tmp['Function'] == 'ActivityItemsModel::AddItemToHistory') & (df_tmp['Params_Decoded'].str.contains("PlaceholderCreated"))]
        if df_ActivityItemsModel_AddItemToHistory.empty: continue
        df_ActivityItemsModel_AddItemToHistory_idx = 0
        df_ActivityItemsModel_AddItemToHistory_idx_list_tmp = df_ActivityItemsModel_AddItemToHistory.index.tolist()

        try:
            file_path = eval(df.loc[df_DiskFileToDBHashComparer_DoWork_idx, "Params_Decoded"])[1]
            file_name = file_path.split('\\')[-1]
        except:
            continue

        for idx in df_ActivityItemsModel_AddItemToHistory_idx_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[0] == file_name) & (eval(df.loc[idx, "Params_Decoded"])[1] == "PlaceholderCreated"):
                    df_ActivityItemsModel_AddItemToHistory_idx = idx
                    break
            except:
                continue

        if df_ActivityItemsModel_AddItemToHistory_idx == 0 : continue

        df_tmp = df.iloc[df_ActivityItemsModel_AddItemToHistory_idx:df_DiskFileToDBHashComparer_DoWork_idx_next]
        df_DehydrateFile_Process = df_tmp[(df_tmp['Code_File'] == 'DehydrateFile.cpp') & (df_tmp['Function'] == 'DehydrateFile::Process')]
        if df_DehydrateFile_Process.empty: continue
        df_DehydrateFile_Process_idx = 0
        df_DehydrateFile_Process_idx_list_tmp = df_DehydrateFile_Process.index.tolist()

        for idx in df_DehydrateFile_Process_idx_list_tmp:
            try:
                if eval(df.loc[idx, "Params_Decoded"])[0] == file_path:
                    df_DehydrateFile_Process_idx = idx
                    break
            except:
                continue

        if df_DehydrateFile_Process_idx == 0 : continue

        df_tmp = df.iloc[df_DehydrateFile_Process_idx:df_DiskFileToDBHashComparer_DoWork_idx_next]
        df_DehydrateFile_RecordTelemetry = df_tmp[(df_tmp['Code_File'] == 'DehydrateFile.cpp') & (df_tmp['Function'] == 'DehydrateFile::RecordTelemetry')]
        if df_DehydrateFile_RecordTelemetry.empty: continue
        df_DehydrateFile_RecordTelemetry_idx = 0
        df_DehydrateFile_RecordTelemetry_idx_list_tmp = df_DehydrateFile_RecordTelemetry.index.tolist()

        for idx in df_DehydrateFile_RecordTelemetry_idx_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[0] == eval(df.loc[df_DehydrateFile_Process_idx, "Params_Decoded"])[1]) & (eval(df.loc[idx, "Params_Decoded"])[3] == "Success"):
                    df_DehydrateFile_RecordTelemetry_idx = idx
                    break
            except:
                continue

        if df_DehydrateFile_RecordTelemetry_idx == 0 : continue

        try:
            file_sha1 = re.findall(sha1_pattern, eval(df.loc[df_DiskFileToDBHashComparer_DoWork_idx, "Params_Decoded"])[2])[0]
        except:
            file_sha1 = "None"
        timestamp = df.loc[df_DehydrateFile_RecordTelemetry_idx, "Timestamp"]
        result.append(["Transform to cloud status", file_path, file_name, file_sha1, timestamp])

    return result

def download(odl_path):
    df = pd.read_csv(odl_path, encoding = 'UTF8', encoding_errors = 'ignore', header = 0)
    df = df.drop(['Filename', 'File_Index'], axis = 'columns')  
    df_len = len(df)
    df_EnclosureDownloader_StartDownload = df[(df['Code_File'] == 'EnclosureDownloader.cpp') & (df['Function'] == 'EnclosureDownloader::StartDownload')]
    if df_EnclosureDownloader_StartDownload.empty: return
    df_EnclosureDownloader_StartDownload_idx_list = []
    df_EnclosureDownloader_StartDownload_idx_list_tmp = df_EnclosureDownloader_StartDownload.index.tolist()

    for idx in df_EnclosureDownloader_StartDownload_idx_list_tmp:
        try:
            if df.loc[idx + 1, "Function"] == "EnclosureDownloader::StartDownload": 
                df_EnclosureDownloader_StartDownload_idx_list.append(idx)
        except:
            continue

    cnt = len(df_EnclosureDownloader_StartDownload_idx_list)
    df_EnclosureDownloader_StartDownload_idx_list.append(df_len)
    result = [["User behavior", "file_status", "file_path", "file_name", "file_sha1", "Download_Start_timestamp", "Download_Complete_timestamp"]]

    for idx in range(cnt):
        user_behavior = "Download"
        file_status = "None"

        df_EnclosureDownloader_StartDownload_idx_previous = df_EnclosureDownloader_StartDownload_idx_list[idx - 1] if idx != 0 else 0
        df_EnclosureDownloader_StartDownload_idx = df_EnclosureDownloader_StartDownload_idx_list[idx] 
        df_EnclosureDownloader_StartDownload_idx_next = df_EnclosureDownloader_StartDownload_idx_list[idx + 1]

        df_tmp = df.iloc[df_EnclosureDownloader_StartDownload_idx_previous:df_EnclosureDownloader_StartDownload_idx]
        df_DriveChangeGenerator_GetUpdatePHState = df_tmp[(df_tmp['Code_File'] == 'DriveChangeGenerator.cpp') & (df_tmp['Function'] == 'DriveChangeGenerator::GetUpdatePHState')]

        try:
            file_path = eval(df.loc[df_EnclosureDownloader_StartDownload_idx, "Params_Decoded"])[1]
            file_name = file_path.split('\\')[-1]
            file_path_onedrive = eval(df.loc[df_EnclosureDownloader_StartDownload_idx, "Params_Decoded"])[0]
            if (df.loc[df_EnclosureDownloader_StartDownload_idx + 1, "Params_Decoded"] != file_path_onedrive):
                continue
        except:
            continue

        df_DriveChangeGenerator_GetUpdatePHState_idx = 0
        if not df_DriveChangeGenerator_GetUpdatePHState.empty:
            df_DriveChangeGenerator_GetUpdatePHState_idx_list_tmp = df_DriveChangeGenerator_GetUpdatePHState.index.tolist()
            for idx in df_DriveChangeGenerator_GetUpdatePHState_idx_list_tmp:
                try:
                    if (df.loc[idx + 1, "Function"] == "DriveChangeGenerator::GetUpdatePHState") & (df.loc[idx + 2, "Function"] == "DriveChangeGenerator::QueueUpdatePHStateDC") & (eval(df.loc[idx, "Params_Decoded"])[3] == file_path) & (eval(df.loc[idx, "Params_Decoded"])[2] == "Pinned"):
                        df_DriveChangeGenerator_GetUpdatePHState_idx = idx
                        df_tmp = df.iloc[df_DriveChangeGenerator_GetUpdatePHState_idx:df_EnclosureDownloader_StartDownload_idx_next]
                        file_status = "Green with White Tick"
                        break
                except:
                    continue

        if df_DriveChangeGenerator_GetUpdatePHState_idx == 0:
            df_tmp = df.iloc[df_EnclosureDownloader_StartDownload_idx:df_EnclosureDownloader_StartDownload_idx_next]
            file_status = "Partial Green Tick"

        df_EnclosureDownloader_CompleteDownload = df_tmp[(df_tmp['Code_File'] == 'EnclosureDownloader.cpp') & (df_tmp['Function'] == 'EnclosureDownloader::CompleteDownload') & (df_tmp['Params_Decoded'].str.contains("SUCCEEDED"))]
        if df_EnclosureDownloader_CompleteDownload.empty: continue
        df_EnclosureDownloader_CompleteDownload_idx = 0
        df_EnclosureDownloader_CompleteDownload_idx_list_tmp = df_EnclosureDownloader_CompleteDownload.index.tolist()

        for idx in df_EnclosureDownloader_CompleteDownload_idx_list_tmp:
            try:
                if df.loc[idx + 1, "Function"] == "EnclosureDownloader::CompleteDownload":
                    if df.loc[idx + 1, "Params_Decoded"] == file_path_onedrive:
                        df_EnclosureDownloader_CompleteDownload_idx = idx
                        break
            except:
                continue
        
        if df_EnclosureDownloader_CompleteDownload_idx == 0 : continue

        df_tmp = df.iloc[df_EnclosureDownloader_CompleteDownload_idx:df_EnclosureDownloader_StartDownload_idx_next]
        df_ActivityItemsModel_AddItemToHistory = df_tmp[(df_tmp['Code_File'] == 'ActivityItemsModel.cpp') & (df_tmp['Function'] == 'ActivityItemsModel::AddItemToHistory')]
        if df_ActivityItemsModel_AddItemToHistory.empty: continue

        df_ActivityItemsModel_AddItemToHistory_idx = 0
        df_ActivityItemsModel_AddItemToHistory_idx_list_tmp = df_ActivityItemsModel_AddItemToHistory.index.tolist()

        for idx in df_ActivityItemsModel_AddItemToHistory_idx_list_tmp:
            try:
                if ((eval(df.loc[idx, "Params_Decoded"])[0]) == file_name) & ((eval(df.loc[idx, "Params_Decoded"])[1]) == 'Downloaded'):
                    df_ActivityItemsModel_AddItemToHistory_idx = idx
                    break
            except:
                continue

        if df_ActivityItemsModel_AddItemToHistory_idx == 0 : continue

        try:
            file_sha1 = re.findall(sha1_pattern, eval(df.loc[df_EnclosureDownloader_CompleteDownload_idx, "Params_Decoded"])[2])[0]
        except:
            file_sha1 = "None"
        Download_Start_timestamp = df.loc[df_EnclosureDownloader_StartDownload_idx, "Timestamp"]
        Download_Complete_timestamp = df.loc[df_EnclosureDownloader_CompleteDownload_idx, "Timestamp"]
        result.append([user_behavior, file_status, file_path, file_name, file_sha1, Download_Start_timestamp, Download_Complete_timestamp])

    return result

def upload_create(odl_path):
    df = pd.read_csv(odl_path, encoding = 'UTF8', encoding_errors = 'ignore', header = 0)
    df = df.drop(['Filename', 'File_Index'], axis = 'columns')  
    df_len = len(df)
    df_WatcherWin_ExamineChange = df[(df['Code_File'] == 'WatcherWin.cpp') & (df['Function'] == 'WatcherWin::ExamineChange') & df['Params_Decoded'].str.contains("FILE_ACTION_ADDED")]
    if df_WatcherWin_ExamineChange.empty: return
    df_WatcherWin_ExamineChange_idx_list = []
    df_WatcherWin_ExamineChange_idx_list_tmp = df_WatcherWin_ExamineChange.index.tolist()

    for idx in df_WatcherWin_ExamineChange_idx_list_tmp:
        try:
            if (df.loc[idx + 1, 'Function'] == "WatcherWin::AddPossibleChangeIfNotAlreadyAdded") & (eval(df.loc[idx, "Params_Decoded"])[1] == df.loc[idx + 1, "Params_Decoded"]): 
                df_WatcherWin_ExamineChange_idx_list.append(idx)
        except:
            continue

    cnt = len(df_WatcherWin_ExamineChange_idx_list)
    df_WatcherWin_ExamineChange_idx_list.append(df_len)
    result = [["User behavior", "file_status", "file_path", "file_name", "file_sha1","Upload_Start_timestamp", "Upload_Complete_timestamp"]]

    for idx in range(cnt):
        file_status = "None"

        df_WatcherWin_ExamineChange_idx = df_WatcherWin_ExamineChange_idx_list[idx] 
        df_WatcherWin_ExamineChange_idx_next = df_WatcherWin_ExamineChange_idx_list[idx + 1]
        df_tmp = df.iloc[df_WatcherWin_ExamineChange_idx:df_WatcherWin_ExamineChange_idx_next]
        df_WatcherWin_ExamineChange_modified = df_tmp[(df_tmp['Code_File'] == 'WatcherWin.cpp') & (df_tmp['Function'] == 'WatcherWin::ExamineChange') & df_tmp['Params_Decoded'].str.contains("FILE_ACTION_MODIFIED")]
        if df_WatcherWin_ExamineChange_modified.empty: continue
        df_WatcherWin_ExamineChange_modified_idx = 0
        df_WatcherWin_ExamineChange_modified_idx_list_tmp = df_WatcherWin_ExamineChange_modified.index.tolist()

        try:
            file_path = eval(df.loc[df_WatcherWin_ExamineChange_idx, "Params_Decoded"])[1]
            file_name = file_path.split('\\')[-1]
        except:
            continue

        for idx in df_WatcherWin_ExamineChange_modified_idx_list_tmp:
            try:
                if (df.loc[idx + 1, "Function"] == "WatcherWin::AddPossibleChangeIfNotAlreadyAdded") & (eval(df.loc[idx, "Params_Decoded"])[1] == df.loc[idx + 1, "Params_Decoded"]) & (df.loc[idx + 1, "Params_Decoded"] == file_path):
                    df_WatcherWin_ExamineChange_modified_idx = idx
                    break
            except:
                continue
                
        if df_WatcherWin_ExamineChange_modified_idx == 0 : continue

        df_tmp = df.iloc[df_WatcherWin_ExamineChange_modified_idx:df_WatcherWin_ExamineChange_idx_next]
        df_DriveChangeGenerator_HandleScannedFullFile = df_tmp[(df_tmp['Code_File'] == 'DriveChangeGenerator.cpp') & (df_tmp['Function'] == 'DriveChangeGenerator::HandleScannedFullFile')]

        if df_DriveChangeGenerator_HandleScannedFullFile.empty: continue

        df_DriveChangeGenerator_HandleScannedFullFile_idx = 0
        df_DriveChangeGenerator_HandleScannedFullFile_idx_list_tmp = df_DriveChangeGenerator_HandleScannedFullFile.index.tolist()

        for idx in df_DriveChangeGenerator_HandleScannedFullFile_idx_list_tmp:
            try:
                if (file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[1] == "Unspecified"):
                    df_DriveChangeGenerator_HandleScannedFullFile_idx = idx
                    file_status = "Partial Green Tick"
                    break
                elif (file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[1] == "Pinned"):
                    df_DriveChangeGenerator_HandleScannedFullFile_idx = idx
                    file_status = "Green with White Tick"
                    break
            except:
                continue

        if df_DriveChangeGenerator_HandleScannedFullFile_idx == 0 : continue

        df_tmp = df.iloc[df_DriveChangeGenerator_HandleScannedFullFile_idx:df_WatcherWin_ExamineChange_idx_next]
        df_EnclosureUploader_StartUpload = df_tmp[(df_tmp['Code_File'] == 'EnclosureUploader.cpp') & (df_tmp['Function'] == 'EnclosureUploader::StartUpload')]
        if df_EnclosureUploader_StartUpload.empty: continue
        df_EnclosureUploader_StartUpload_idx = 0
        df_EnclosureUploader_StartUpload_idx_list_tmp = df_EnclosureUploader_StartUpload.index.tolist()

        for idx in df_EnclosureUploader_StartUpload_idx_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[1] == file_path):
                    df_EnclosureUploader_StartUpload_idx = idx
                    break
            except:
                continue

        if df_EnclosureUploader_StartUpload_idx == 0 : continue

        df_tmp = df.iloc[df_EnclosureUploader_StartUpload_idx:df_WatcherWin_ExamineChange_idx_next]
        df_UploadTelemetry_LogFullFileUploadComplete = df_tmp[(df_tmp['Code_File'] == 'SyncUploadTelemetry.cpp') & (df_tmp['Function'] == 'UploadTelemetry::LogFullFileUploadComplete')]
        if df_UploadTelemetry_LogFullFileUploadComplete.empty: continue

        df_UploadTelemetry_LogFullFileUploadComplete_idx = 0
        df_UploadTelemetry_LogFullFileUploadComplete_idx_list_tmp = df_UploadTelemetry_LogFullFileUploadComplete.index.tolist()

        for idx in df_UploadTelemetry_LogFullFileUploadComplete_idx_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[0]) == "Success":
                    df_UploadTelemetry_LogFullFileUploadComplete_idx = idx
                    break
            except:
                continue

        if df_UploadTelemetry_LogFullFileUploadComplete_idx == 0 : continue

        df_tmp = df.iloc[df_UploadTelemetry_LogFullFileUploadComplete_idx:df_WatcherWin_ExamineChange_idx_next]
        df_CreateNewFile_AddFileToDriveWithStatus = df_tmp[(df_tmp['Code_File'] == 'CreateFile.cpp') & (df_tmp['Function'] == 'CreateNewFile::AddFileToDriveWithStatus')]
        if df_CreateNewFile_AddFileToDriveWithStatus.empty: continue

        df_CreateNewFile_AddFileToDriveWithStatus_idx = 0
        df_CreateNewFile_AddFileToDriveWithStatus_list_tmp = df_CreateNewFile_AddFileToDriveWithStatus.index.tolist()

        for idx in df_CreateNewFile_AddFileToDriveWithStatus_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[1]) == file_path:
                    df_CreateNewFile_AddFileToDriveWithStatus_idx = idx
                    break
            except:
                continue

        if df_CreateNewFile_AddFileToDriveWithStatus_idx == 0 : continue

        df_tmp = df.iloc[df_CreateNewFile_AddFileToDriveWithStatus_idx:df_WatcherWin_ExamineChange_idx_next]
        df_ActivityItemsModel_AddItemToHistory = df_tmp[(df_tmp['Code_File'] == 'ActivityItemsModel.cpp') & (df_tmp['Function'] == 'ActivityItemsModel::AddItemToHistory')]
        if df_ActivityItemsModel_AddItemToHistory.empty: continue

        df_ActivityItemsModel_AddItemToHistory_idx = 0
        df_ActivityItemsModel_AddItemToHistory_idx_list_tmp = df_ActivityItemsModel_AddItemToHistory.index.tolist()

        for idx in df_ActivityItemsModel_AddItemToHistory_idx_list_tmp:
            try:
                if ((eval(df.loc[idx, "Params_Decoded"])[0]) == file_name) & ((eval(df.loc[idx, "Params_Decoded"])[1]) == 'Uploaded'):
                    df_ActivityItemsModel_AddItemToHistory_idx = idx
                    break
            except:
                continue

        if df_ActivityItemsModel_AddItemToHistory_idx == 0 : continue

        try:
            file_sha1 = re.findall(sha1_pattern, eval(df.loc[df_CreateNewFile_AddFileToDriveWithStatus_idx, "Params_Decoded"])[3])[0]
        except:
            file_sha1 = "None"
        Upload_Start_timestamp = df.loc[df_EnclosureUploader_StartUpload_idx, "Timestamp"]
        Upload_Complete_timestamp = df.loc[df_ActivityItemsModel_AddItemToHistory_idx, "Timestamp"]
        result.append(["Upload/Create", file_status, file_path, file_name, file_sha1, Upload_Start_timestamp, Upload_Complete_timestamp])

    return result

def delete(odl_path):
    df = pd.read_csv(odl_path, encoding = 'UTF8', encoding_errors = 'ignore', header = 0)
    df = df.drop(['Filename', 'File_Index'], axis = 'columns')  
    df_len = len(df)
    df_WatcherWin_ExamineChange_removed = df[(df['Code_File'] == 'WatcherWin.cpp') & (df['Function'] == 'WatcherWin::ExamineChange') & df['Params_Decoded'].str.contains("FILE_ACTION_REMOVED")]
    if df_WatcherWin_ExamineChange_removed.empty: return
    df_WatcherWin_ExamineChange_removed_idx_list = df_WatcherWin_ExamineChange_removed.index.tolist()
    cnt = len(df_WatcherWin_ExamineChange_removed_idx_list)
    df_WatcherWin_ExamineChange_removed_idx_list.append(df_len)
    result = [["User behavior", "file_status", "file_path", "file_name", "file_sha1","timestamp"]]

    for idx in range(cnt): 
        user_behavior = "Delete"
        file_status = "None"

        df_WatcherWin_ExamineChange_removed_idx = df_WatcherWin_ExamineChange_removed_idx_list[idx] 
        df_WatcherWin_ExamineChange_removed_idx_next = df_WatcherWin_ExamineChange_removed_idx_list[idx + 1]
        df_tmp = df.iloc[df_WatcherWin_ExamineChange_removed_idx:df_WatcherWin_ExamineChange_removed_idx_next]
        df_FileRealPath_DiskLookup = df_tmp[(df_tmp['Code_File'] == 'FileRealPath.cpp') & (df_tmp['Function'] == 'FileRealPath::DiskLookup')]

        try:
            file_path = eval(df.loc[df_WatcherWin_ExamineChange_removed_idx, "Params_Decoded"])[1]
            file_name = file_path.split('\\')[-1]
        except:
            continue

        if not df_FileRealPath_DiskLookup.empty:
            df_FileRealPath_DiskLookup_idx_list_tmp = df_FileRealPath_DiskLookup.index.tolist()
            for idx in df_FileRealPath_DiskLookup_idx_list_tmp:
                try:
                    if (eval(df.loc[idx, "Params_Decoded"])[3] == file_path):
                        df_FileRealPath_DiskLookup_idx = idx
                        df_tmp = df.iloc[df_FileRealPath_DiskLookup_idx:df_WatcherWin_ExamineChange_removed_idx_next]
                        file_status = "Partial Green Tick or Green with White Tick"
                        break
                except:
                    continue
        else:
            file_status = "Blue Cloud"

        df_FileNeededEventListener_NotifyFileNotNeeded = df_tmp[(df_tmp['Code_File'] == 'FileNeededEventListener.cpp') & (df_tmp['Function'] == 'FileNeededEventListener::NotifyFileNotNeeded')]
        if df_FileNeededEventListener_NotifyFileNotNeeded.empty: continue
        df_FileNeededEventListener_NotifyFileNotNeeded_idx = df_FileNeededEventListener_NotifyFileNotNeeded.index.tolist()[0]

        df_tmp = df.iloc[df_FileNeededEventListener_NotifyFileNotNeeded_idx:df_WatcherWin_ExamineChange_removed_idx_next]
        df_ActivityItemsModel_AddItemToHistory = df_tmp[(df_tmp['Code_File'] == 'ActivityItemsModel.cpp') & (df_tmp['Function'] == 'ActivityItemsModel::AddItemToHistory')]
        if df_ActivityItemsModel_AddItemToHistory.empty: continue

        df_ActivityItemsModel_AddItemToHistory_idx = 0
        df_ActivityItemsModel_AddItemToHistory_idx_list_tmp = df_ActivityItemsModel_AddItemToHistory.index.tolist()

        for idx in df_ActivityItemsModel_AddItemToHistory_idx_list_tmp:
            try:
                if ((eval(df.loc[idx, "Params_Decoded"])[0]) == file_name) & ((eval(df.loc[idx, "Params_Decoded"])[1]) == 'Deleted'):
                    df_ActivityItemsModel_AddItemToHistory_idx = idx
                    break
            except:
                continue

        if df_ActivityItemsModel_AddItemToHistory_idx == 0 : continue

        try:
            file_sha1 = re.findall(sha1_pattern, eval(df.loc[df_FileNeededEventListener_NotifyFileNotNeeded_idx, "Params_Decoded"])[2])[0]
        except:
            file_sha1 = "None"
        Delete_Complete_timestamp = df.loc[df_ActivityItemsModel_AddItemToHistory_idx, "Timestamp"]
        result.append([user_behavior, file_status, file_path, file_name, file_sha1, Delete_Complete_timestamp])

    return result

def edit_filename(odl_path):
    df = pd.read_csv(odl_path, encoding = 'UTF8', encoding_errors = 'ignore', header = 0)
    df = df.drop(['Filename', 'File_Index'], axis = 'columns')  
    df_len = len(df)
    df_WatcherWin_ExamineChange_old = df[(df['Code_File'] == 'WatcherWin.cpp') & (df['Function'] == 'WatcherWin::ExamineChange') & df['Params_Decoded'].str.contains("FILE_ACTION_RENAMED_OLD_NAME")]
    if df_WatcherWin_ExamineChange_old.empty: return
    
    df_WatcherWin_ExamineChange_old_idx_list = []
    df_WatcherWin_ExamineChange_old_idx_list_tmp = df_WatcherWin_ExamineChange_old.index.tolist()

    for idx in df_WatcherWin_ExamineChange_old_idx_list_tmp:
        try:
            if (df.loc[idx + 1, 'Function'] == "WatcherWin::ExamineChange") & (eval(df.loc[idx + 1, "Params_Decoded"])[0] == "FILE_ACTION_RENAMED_NEW_NAME"):
                df_WatcherWin_ExamineChange_old_idx_list.append(idx)
        except:
            continue

    cnt = len(df_WatcherWin_ExamineChange_old_idx_list)
    df_WatcherWin_ExamineChange_old_idx_list.append(df_len)
    result = [["User behavior", "file status", "file_path", "old_file_name", "new_file_name","file_sha1","timestamp"]]

    for idx in range(cnt):
        file_status = "None"

        df_WatcherWin_ExamineChange_old_idx = df_WatcherWin_ExamineChange_old_idx_list[idx] 
        df_WatcherWin_ExamineChange_old_idx_next = df_WatcherWin_ExamineChange_old_idx_list[idx + 1]

        df_tmp = df.iloc[df_WatcherWin_ExamineChange_old_idx:df_WatcherWin_ExamineChange_old_idx_next]
        df_detectMoveFromDB = df_tmp[(df_tmp['Code_File'] == 'drive.cpp') & (df_tmp['Function'] == 'detectMoveFromDB')]
        
        if df_detectMoveFromDB.empty: continue

        try:
            old_file_path = eval(df.loc[df_WatcherWin_ExamineChange_old_idx, "Params_Decoded"])[1]
            new_file_path = eval(df.loc[df_WatcherWin_ExamineChange_old_idx + 1, "Params_Decoded"])[1]
            old_file_name = old_file_path.split('\\')[-1]
            new_file_name = new_file_path.split('\\')[-1]
            if old_file_path.replace(old_file_name, "") != new_file_path.replace(new_file_name, ""): continue
            file_path = old_file_path.replace(old_file_name, "")
        except:
            continue

        df_detectMoveFromDB_idx = 0
        df_detectMoveFromDB_idx_list_tmp = df_detectMoveFromDB.index.tolist()

        for idx in df_detectMoveFromDB_idx_list_tmp:
            if ((eval(df.loc[idx, "Params_Decoded"])[0]) == new_file_name) & ((eval(df.loc[idx, "Params_Decoded"])[1]) == old_file_name):
                df_detectMoveFromDB_idx = idx
                break
        
        if df_detectMoveFromDB_idx == 0 : continue

        df_tmp = df.iloc[df_detectMoveFromDB_idx:df_WatcherWin_ExamineChange_old_idx_next]
        df_DriveChangeGenerator_HandleScannedFullFile = df_tmp[(df_tmp['Code_File'] == 'DriveChangeGenerator.cpp') & (df_tmp['Function'] == 'DriveChangeGenerator::HandleScannedFullFile')]

        if df_DriveChangeGenerator_HandleScannedFullFile.empty: continue

        df_DriveChangeGenerator_HandleScannedFullFile_idx = 0
        df_DriveChangeGenerator_HandleScannedFullFile_idx_list_tmp = df_DriveChangeGenerator_HandleScannedFullFile.index.tolist()

        for idx in df_DriveChangeGenerator_HandleScannedFullFile_idx_list_tmp:
            try:
                if (new_file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[1] == "Unspecified"):
                    df_DriveChangeGenerator_HandleScannedFullFile_idx = idx
                    file_status = "Partial Green Tick"
                    break
                elif (new_file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[1] == "Pinned"):
                    df_DriveChangeGenerator_HandleScannedFullFile_idx = idx
                    file_status = "Green with White Tick"
                    break
            except:
                continue

        if df_DriveChangeGenerator_HandleScannedFullFile_idx == 0 : continue

        df_tmp = df.iloc[df_DriveChangeGenerator_HandleScannedFullFile_idx:df_WatcherWin_ExamineChange_old_idx_next]
        df_MoveRenameFile_LogInfo = df_tmp[(df_tmp['Code_File'] == 'MoveFile.cpp') & (df_tmp['Function'] == 'MoveRenameFile::LogInfo')]
        if df_MoveRenameFile_LogInfo.empty: continue

        df_MoveRenameFile_LogInfo_idx = 0
        df_MoveRenameFile_LogInfo_idx_list_tmp = df_MoveRenameFile_LogInfo.index.tolist()

        for idx in df_MoveRenameFile_LogInfo_idx_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[2]) == new_file_name:
                    df_MoveRenameFile_LogInfo_idx = idx
                    break
            except:
                continue

        if df_MoveRenameFile_LogInfo_idx == 0 : continue

        df_tmp = df.iloc[df_MoveRenameFile_LogInfo_idx:df_WatcherWin_ExamineChange_old_idx_next]
        df_ActivityItemsModel_AddItemToHistory = df_tmp[(df_tmp['Code_File'] == 'ActivityItemsModel.cpp') & (df_tmp['Function'] == 'ActivityItemsModel::AddItemToHistory')]
        if df_ActivityItemsModel_AddItemToHistory.empty: continue

        df_ActivityItemsModel_AddItemToHistory_idx = 0
        df_ActivityItemsModel_AddItemToHistory_idx_list_tmp = df_ActivityItemsModel_AddItemToHistory.index.tolist()

        for idx in df_ActivityItemsModel_AddItemToHistory_idx_list_tmp:
            try:
                if ((eval(df.loc[idx, "Params_Decoded"])[0]) == new_file_name) & ((eval(df.loc[idx, "Params_Decoded"])[1]) == 'Renamed'):
                    df_ActivityItemsModel_AddItemToHistory_idx = idx
                    break
            except:
                continue

        if df_ActivityItemsModel_AddItemToHistory_idx == 0 : continue

        try:
            file_sha1 = re.findall(sha1_pattern, eval(df.loc[df_MoveRenameFile_LogInfo_idx, "Params_Decoded"])[6])[0]
        except:
            file_sha1 = "None"
        timestamp = df.loc[df_ActivityItemsModel_AddItemToHistory_idx, "Timestamp"]
        result.append(["edit_filename", file_status, file_path, old_file_name, new_file_name, file_sha1, timestamp])

    return result

def edit_filecontent(odl_path):
    df = pd.read_csv(odl_path, encoding = 'UTF8', encoding_errors = 'ignore', header = 0)
    df = df.drop(['Filename', 'File_Index'], axis = 'columns')  
    df_len = len(df)
    df_WatcherWin_ExamineChange_modified = df[(df['Code_File'] == 'WatcherWin.cpp') & (df['Function'] == 'WatcherWin::ExamineChange') & df['Params_Decoded'].str.contains("FILE_ACTION_MODIFIED")]
    if df_WatcherWin_ExamineChange_modified.empty: return
    df_WatcherWin_ExamineChange_modified_idx_list = []
    df_WatcherWin_ExamineChange_modified_idx_list_tmp = df_WatcherWin_ExamineChange_modified.index.tolist()

    for idx in df_WatcherWin_ExamineChange_modified_idx_list_tmp:
        try:
            if (df.loc[idx + 1, 'Function'] == "WatcherWin::AddPossibleChangeIfNotAlreadyAdded") & (eval(df.loc[idx, "Params_Decoded"])[1] == df.loc[idx + 1, "Params_Decoded"]): 
                df_WatcherWin_ExamineChange_modified_idx_list.append(idx)
        except:
            continue

    cnt = len(df_WatcherWin_ExamineChange_modified_idx_list)
    df_WatcherWin_ExamineChange_modified_idx_list.append(df_len)
    result = [["User behavior", "file_status", "file_path", "file_name", "old_file_sha1", "new_file_sha1","edit_start_timestamp", "edit_complete_timestamp"]]

    for idx in range(cnt):
        file_status = "None"

        df_WatcherWin_ExamineChange_modified_idx = df_WatcherWin_ExamineChange_modified_idx_list[idx] 
        df_WatcherWin_ExamineChange_modified_idx_next = df_WatcherWin_ExamineChange_modified_idx_list[idx + 1]

        try:
            file_path = eval(df.loc[df_WatcherWin_ExamineChange_modified_idx, "Params_Decoded"])[1]
            file_name = file_path.split('\\')[-1]
        except:
            continue

        df_tmp = df.iloc[df_WatcherWin_ExamineChange_modified_idx:df_WatcherWin_ExamineChange_modified_idx_next]
        df_DriveChangeGenerator_HandleScannedFullFile = df_tmp[(df_tmp['Code_File'] == 'DriveChangeGenerator.cpp') & (df_tmp['Function'] == 'DriveChangeGenerator::HandleScannedFullFile')]

        if df_DriveChangeGenerator_HandleScannedFullFile.empty: continue

        df_DriveChangeGenerator_HandleScannedFullFile_idx = 0
        df_DriveChangeGenerator_HandleScannedFullFile_idx_list_tmp = df_DriveChangeGenerator_HandleScannedFullFile.index.tolist()

        for idx in df_DriveChangeGenerator_HandleScannedFullFile_idx_list_tmp:
            try:
                if (file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[2] == "Unspecified"):
                    df_DriveChangeGenerator_HandleScannedFullFile_idx = idx
                    file_status = "Partial Green Tick"
                    break
                elif (file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[2] == "Pinned"):
                    df_DriveChangeGenerator_HandleScannedFullFile_idx = idx
                    file_status = "Green with White Tick"
                    break
            except:
                continue

        if df_DriveChangeGenerator_HandleScannedFullFile_idx == 0 : continue

        df_tmp = df.iloc[df_DriveChangeGenerator_HandleScannedFullFile_idx:df_WatcherWin_ExamineChange_modified_idx_next]
        df_EnclosureUploader_StartUpload = df_tmp[(df_tmp['Code_File'] == 'EnclosureUploader.cpp') & (df_tmp['Function'] == 'EnclosureUploader::StartUpload')]
        if df_EnclosureUploader_StartUpload.empty: continue
        df_EnclosureUploader_StartUpload_idx = 0
        df_EnclosureUploader_StartUpload_idx_list_tmp = df_EnclosureUploader_StartUpload.index.tolist()

        for idx in df_EnclosureUploader_StartUpload_idx_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[1] == file_path):
                    df_EnclosureUploader_StartUpload_idx = idx
                    break
            except:
                continue

        if df_EnclosureUploader_StartUpload_idx == 0 : continue

        df_tmp = df.iloc[df_EnclosureUploader_StartUpload_idx:df_WatcherWin_ExamineChange_modified_idx_next]
        df_UploadTelemetry_LogFullFileUploadComplete = df_tmp[(df_tmp['Code_File'] == 'SyncUploadTelemetry.cpp') & (df_tmp['Function'] == 'UploadTelemetry::LogFullFileUploadComplete')]
        if df_UploadTelemetry_LogFullFileUploadComplete.empty: continue

        df_UploadTelemetry_LogFullFileUploadComplete_idx = 0
        df_UploadTelemetry_LogFullFileUploadComplete_idx_list_tmp = df_UploadTelemetry_LogFullFileUploadComplete.index.tolist()

        for idx in df_UploadTelemetry_LogFullFileUploadComplete_idx_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[0]) == "Success":
                    df_UploadTelemetry_LogFullFileUploadComplete_idx = idx
                    break
            except:
                continue

        if df_UploadTelemetry_LogFullFileUploadComplete_idx == 0 : continue

        df_tmp = df.iloc[df_UploadTelemetry_LogFullFileUploadComplete_idx:df_WatcherWin_ExamineChange_modified_idx_next]
        df_ChangeFile_Process = df_tmp[(df_tmp['Code_File'] == 'ChangeFile.cpp') & (df_tmp['Function'] == 'ChangeFile::Process')]
        if df_ChangeFile_Process.empty: continue

        df_ChangeFile_Process_idx = 0
        df_ChangeFile_Process_list_tmp = df_ChangeFile_Process.index.tolist()

        for idx in df_ChangeFile_Process_list_tmp:
            try:
                if (eval(df.loc[idx, "Params_Decoded"])[1]) == file_name:
                    df_ChangeFile_Process_idx = idx
                    break
            except:
                continue

        if df_ChangeFile_Process_idx == 0 : continue

        df_tmp = df.iloc[df_ChangeFile_Process_idx:df_WatcherWin_ExamineChange_modified_idx_next]
        df_ActivityItemsModel_AddItemToHistory = df_tmp[(df_tmp['Code_File'] == 'ActivityItemsModel.cpp') & (df_tmp['Function'] == 'ActivityItemsModel::AddItemToHistory')]
        if df_ActivityItemsModel_AddItemToHistory.empty: continue

        df_ActivityItemsModel_AddItemToHistory_idx = 0
        df_ActivityItemsModel_AddItemToHistory_idx_list_tmp = df_ActivityItemsModel_AddItemToHistory.index.tolist()

        for idx in df_ActivityItemsModel_AddItemToHistory_idx_list_tmp:
            try:
                if ((eval(df.loc[idx, "Params_Decoded"])[0]) == file_name) & ((eval(df.loc[idx, "Params_Decoded"])[1]) == 'Uploaded'):
                    df_ActivityItemsModel_AddItemToHistory_idx = idx
                    break
            except:
                continue

        if df_ActivityItemsModel_AddItemToHistory_idx == 0 : continue

        try:
            old_file_sha1 = re.findall(sha1_pattern, eval(df.loc[df_ChangeFile_Process_idx, "Params_Decoded"])[3])[0]
        except:
            old_file_sha1 = "None"
        try:
            new_file_sha1 = re.findall(sha1_pattern, eval(df.loc[df_ChangeFile_Process_idx, "Params_Decoded"])[5])[0]
        except:
            new_file_sha1 = "None"
        edit_start_timestamp = df.loc[df_EnclosureUploader_StartUpload_idx, "Timestamp"]
        edit_complete_timestamp = df.loc[df_ActivityItemsModel_AddItemToHistory_idx, "Timestamp"]
        result.append(["edit_filecontent", file_status, file_path, file_name, old_file_sha1, new_file_sha1, edit_start_timestamp, edit_complete_timestamp])

    return result

def move(odl_path):
    df = pd.read_csv(odl_path, encoding = 'UTF8', encoding_errors = 'ignore', header = 0)
    df = df.drop(['Filename', 'File_Index'], axis = 'columns')  
    df_len = len(df)
    df_WatcherWin_ExamineChange_removed = df[(df['Code_File'] == 'WatcherWin.cpp') & (df['Function'] == 'WatcherWin::ExamineChange') & df['Params_Decoded'].str.contains("FILE_ACTION_REMOVED")]
    if df_WatcherWin_ExamineChange_removed.empty: return
    df_WatcherWin_ExamineChange_removed_idx_list = df_WatcherWin_ExamineChange_removed.index.tolist()
    cnt = len(df_WatcherWin_ExamineChange_removed_idx_list)
    df_WatcherWin_ExamineChange_removed_idx_list.append(df_len)
    result = [["User behavior", "file status", "before_file_path", "after_file_path", "file_name","timestamp"]]

    for idx in range(cnt): 
        user_behavior = "File Move"
        file_status = "None"

        df_WatcherWin_ExamineChange_removed_idx = df_WatcherWin_ExamineChange_removed_idx_list[idx] 
        df_WatcherWin_ExamineChange_removed_idx_next = df_WatcherWin_ExamineChange_removed_idx_list[idx + 1]

        df_tmp = df.iloc[df_WatcherWin_ExamineChange_removed_idx:df_WatcherWin_ExamineChange_removed_idx_next]
        df_WatcherWin_ExamineChange_added = df_tmp[(df_tmp['Code_File'] == 'WatcherWin.cpp') & (df_tmp['Function'] == 'WatcherWin::ExamineChange') & (df_tmp['Params_Decoded'].str.contains("FILE_ACTION_ADDED"))]

        if df_WatcherWin_ExamineChange_added.empty: continue

        try:
            before_file_path = eval(df.loc[df_WatcherWin_ExamineChange_removed_idx, "Params_Decoded"])[1]
            file_name = before_file_path.split('\\')[-1]
        except:
            continue

        df_WatcherWin_ExamineChange_added_idx = 0
        df_WatcherWin_ExamineChange_added_idx_list_tmp = df_WatcherWin_ExamineChange_added.index.tolist()

        for idx in df_WatcherWin_ExamineChange_added_idx_list_tmp:
            try:
                if (file_name in (eval(df.loc[idx, "Params_Decoded"])[1])):
                    df_WatcherWin_ExamineChange_added_idx = idx
                    break
            except:
                continue

        if df_WatcherWin_ExamineChange_added_idx == 0 : continue

        df_tmp = df.iloc[df_WatcherWin_ExamineChange_added_idx:df_WatcherWin_ExamineChange_removed_idx_next]
        df_WatcherWin_ExamineChange_modified = df_tmp[(df_tmp['Code_File'] == 'WatcherWin.cpp') & (df_tmp['Function'] == 'WatcherWin::ExamineChange') & (df_tmp['Params_Decoded'].str.contains("FILE_ACTION_MODIFIED"))]

        if df_WatcherWin_ExamineChange_modified.empty: continue

        try:
            after_file_path = eval(df.loc[df_WatcherWin_ExamineChange_added_idx, "Params_Decoded"])[1]
        except:
            continue

        df_WatcherWin_ExamineChange_modified_idx = 0
        df_WatcherWin_ExamineChange_modified_idx_list_tmp = df_WatcherWin_ExamineChange_modified.index.tolist()

        for idx in df_WatcherWin_ExamineChange_modified_idx_list_tmp:
            try:
                if ((eval(df.loc[df_WatcherWin_ExamineChange_added_idx, "Params_Decoded"])[1]) == (eval(df.loc[idx, "Params_Decoded"])[1])):
                    df_WatcherWin_ExamineChange_modified_idx = idx
                    break
            except:
                continue

        if df_WatcherWin_ExamineChange_modified_idx == 0 : continue

        df_tmp = df.iloc[df_WatcherWin_ExamineChange_modified_idx:df_WatcherWin_ExamineChange_removed_idx_next]
        df_DriveChangeGenerator_HandleScannedPlaceHolderFile = df_tmp[(df_tmp['Code_File'] == 'DriveChangeGenerator.cpp') & (df_tmp['Function'] == 'DriveChangeGenerator::HandleScannedPlaceholderFile')]

        if df_DriveChangeGenerator_HandleScannedPlaceHolderFile.empty: 
            df_DriveChangeGenerator_HandleScannedFullFile = df_tmp[(df_tmp['Code_File'] == 'DriveChangeGenerator.cpp') & (df_tmp['Function'] == 'DriveChangeGenerator::HandleScannedFullFile')]

            if df_DriveChangeGenerator_HandleScannedFullFile.empty: continue

            df_DriveChangeGenerator_HandleScannedFullFile_idx = 0
            df_DriveChangeGenerator_HandleScannedFullFile_idx_list_tmp = df_DriveChangeGenerator_HandleScannedFullFile.index.tolist()

            for idx in df_DriveChangeGenerator_HandleScannedFullFile_idx_list_tmp:
                try:
                    if (file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[1] == "Unspecified"):
                        df_DriveChangeGenerator_HandleScannedFullFile_idx = idx
                        df_tmp = df.iloc[df_DriveChangeGenerator_HandleScannedFullFile_idx:df_WatcherWin_ExamineChange_removed_idx_next]
                        file_status = "Partial Green Tick"
                        break
                    elif (file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[1] == "Pinned"):
                        df_DriveChangeGenerator_HandleScannedFullFile_idx = idx
                        df_tmp = df.iloc[df_DriveChangeGenerator_HandleScannedFullFile_idx:df_WatcherWin_ExamineChange_removed_idx_next]
                        file_status = "Green with White Tick"
                        break
                except:
                    continue

            if df_DriveChangeGenerator_HandleScannedFullFile_idx == 0 : continue
        else:
            df_DriveChangeGenerator_HandleScannedPlaceHolderFile_idx = 0
            df_DriveChangeGenerator_HandleScannedPlaceHolderFile_idx_list_tmp = df_DriveChangeGenerator_HandleScannedPlaceHolderFile.index.tolist()

            for idx in df_DriveChangeGenerator_HandleScannedPlaceHolderFile_idx_list_tmp:
                try:
                    if (file_name in (eval(df.loc[idx, "Params_Decoded"])[0])) & (eval(df.loc[idx, "Params_Decoded"])[1] == "Unpinned"):
                        df_DriveChangeGenerator_HandleScannedPlaceHolderFile_idx = idx
                        df_tmp = df.iloc[df_DriveChangeGenerator_HandleScannedPlaceHolderFile_idx:df_WatcherWin_ExamineChange_removed_idx_next]
                        file_status = "Blue Cloud"
                        break
                except:
                    continue

            if df_DriveChangeGenerator_HandleScannedPlaceHolderFile_idx == 0 : continue

        df_ActivityItemsModel_AddItemToHistory = df_tmp[(df_tmp['Code_File'] == 'ActivityItemsModel.cpp') & (df_tmp['Function'] == 'ActivityItemsModel::AddItemToHistory')]

        if df_ActivityItemsModel_AddItemToHistory.empty: continue

        df_ActivityItemsModel_AddItemToHistory_idx = 0
        df_ActivityItemsModel_AddItemToHistory_idx_list_tmp = df_ActivityItemsModel_AddItemToHistory.index.tolist()

        for idx in df_ActivityItemsModel_AddItemToHistory_idx_list_tmp:
            try:
                if ((eval(df.loc[idx, "Params_Decoded"])[0]) == file_name) & ((eval(df.loc[idx, "Params_Decoded"])[1]) == 'Moved'):
                    df_ActivityItemsModel_AddItemToHistory_idx = idx
                    break
            except:
                continue

        if df_ActivityItemsModel_AddItemToHistory_idx == 0 : continue

        timestamp = df.loc[df_ActivityItemsModel_AddItemToHistory_idx, "Timestamp"]
        result.append([user_behavior, file_status, before_file_path, after_file_path, file_name, timestamp])

    return result

if __name__ == "__main__":
    
    usage = "test"

    parser = argparse.ArgumentParser(description = 'OneDrive User Behavior analyzer', epilog = usage, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('odl_folder', help='Path to folder with .odl files')
    parser.add_argument('-o', '--output_folder', help='Output folder', default = 'User_Behavior_Report')
    parser.add_argument('-g', '--general_keystore_folder', help='Path to general.keystore (if not in odl_folder)')

    args = parser.parse_args()

    odl_folder = os.path.abspath(args.odl_folder)
    output_folder = args.output_folder
    odl_parsed_result = "odl_parsed_result.csv"

    if not os.path.exists(odl_folder):
        print(f'Error, {odl_folder} not exist')
        exit(1)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if args.general_keystore_folder:
        general_keystore_folder = os.path.abspath(args.general_keystore_folder) 
    else:
        general_keystore_folder = os.path.abspath(odl_folder)
    if not os.path.exists(os.path.join(general_keystore_folder, "general.keystore")):
        print(f'Error, "general.keystore" not found in {general_keystore_folder}')
        exit(1)

    odl_parser_command = ["python", ".\odl.py", "-g", general_keystore_folder, "-o", odl_parsed_result, odl_folder]
    try:
        subprocess.run(odl_parser_command)
    except Exception as ex:
        print("ERROR parsing odl file : ", ex)
        exit(1)
    print(f"[*] Success parsing odl file, {odl_parsed_result} created")
    
    behavior_list = [Transform_to_cloud_status, download, upload_create, delete, edit_filename, edit_filecontent, move]
    
    for func in behavior_list:
        csv_f = open(os.path.join(output_folder, func.__name__ + '.csv'), 'w', newline = "" , encoding='utf-8-sig')#encoding without hangul being garbled 
        writer = csv.writer(csv_f)

        odl_rows = func(odl_parsed_result)
        try:
            if odl_rows:
                writer.writerows(odl_rows)
                print(f'Wrote {len(odl_rows)} rows')
            else:
                print("No log data was found in this file.")
        except Exception as ex:
            print("ERROR writing rows:", type(ex), ex)

        csv_f.close()
    