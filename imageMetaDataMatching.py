import os
import cv2
import pandas as pd
import json
import argparse
from datetime import datetime

def get_frame_from_video(video_path, video_start_datetime, timestamp):
    """
    Extract a frame from the video at a specific timestamp.
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Calculate the frame number based on the timestamp and video's FPS
    fps = cap.get(cv2.CAP_PROP_FPS)
    time_diff = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S') - datetime.strptime(video_start_datetime, '%Y-%m-%d %H:%M:%S')
    frame_number = int(time_diff.total_seconds() * fps)

    # Set the video position to the frame number
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    # Read the frame
    success, frame = cap.read()
    
    # Release the video capture object
    cap.release()
    
    return success, frame

def save_frame_and_data(frame, data, base_name):
    """
    Save the frame as a JPEG image and data as a JSON file.
    """
    image_name = f"{base_name}.jpeg"
    json_name = f"{base_name}.json"

    # Save the frame
    cv2.imwrite(image_name, frame)

    # Save the data
    with open(json_name, 'w') as f:
        json.dump(data, f)

def process_video_and_csv(video_path, csv_path, video_start_datetime, outdir):
    """
    Process the video and CSV to extract frames and save data.
    """
    # Trying to edit this to not have it rely on csv
    if not outdir:
        outdir = os.path.join(os.getcwd(), "uas_data")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)

    df = pd.read_csv(csv_path)

    # Iterate over the rows in the DataFrame
    for index, row in df.iterrows():
        timestamp = row['datetime']
        success, frame = get_frame_from_video(video_path, video_start_datetime, timestamp)

        if success:
            base_name = os.path.join(outdir, f"frame_{index}")
            save_frame_and_data(frame, row.to_dict(), base_name)
        else:
            print(f"Failed to extract frame for timestamp: {timestamp}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract frames from video based on CSV datetime.")
    parser.add_argument("--video", required=True, help="Path to the video file.")
    parser.add_argument("--csv", required=True, help="Path to the CSV file.")
    parser.add_argument("--start_datetime", required=True, help="Start datetime of the video (YYYY-MM-DD HH:MM:SS).")
    parser.add_argument("-o",
                        "--outdir",
                        help="Output Directory",
                        )
    args = parser.parse_args()

    process_video_and_csv(args.video, args.csv, args.start_datetime, args.outdir)

# python script_name.py --video path/to/video.mp4 --csv path/to/info.csv --start_datetime "2023-12-01 00:00:00"
