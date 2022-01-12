import math
from typing import List, Mapping, Optional, Tuple, Union

import cv2
import dataclasses
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as ax
import pandas as pd

from mediapipe.framework.formats import detection_pb2
from mediapipe.framework.formats import location_data_pb2
from mediapipe.framework.formats import landmark_pb2

_PRESENCE_THRESHOLD = 0.5
_VISIBILITY_THRESHOLD = 0.5
_RGB_CHANNELS = 3

WHITE_COLOR = (224, 224, 224)
BLACK_COLOR = (0, 0, 0)
RED_COLOR = (0, 0, 255)
GREEN_COLOR = (0, 128, 0)
BLUE_COLOR = (255, 0, 0)

@dataclasses.dataclass
class DrawingSpec:
  # Color for drawing the annotation. Default to the white color.
  color: Tuple[int, int, int] = WHITE_COLOR
  # Thickness for drawing the annotation. Default to 2 pixels.
  thickness: int = 2
  # Circle radius. Default to 2 pixels.
  circle_radius: int = 2

def _normalize_color(color):
  return tuple(v / 255. for v in color)

def plot_landmarks(dst_path, landmark_list: landmark_pb2.NormalizedLandmarkList,
                   connections: Optional[List[Tuple[int, int]]] = None,
                   landmark_drawing_spec: DrawingSpec = DrawingSpec(
                       color=RED_COLOR, thickness=5),
                   connection_drawing_spec: DrawingSpec = DrawingSpec(
                       color=BLACK_COLOR, thickness=5),
                   elevation: int = 10,
                   azimuth: int = 10):
  """Plot the landmarks and the connections in matplotlib 3d.
  Args:
    landmark_list: A normalized landmark list proto message to be plotted.
    connections: A list of landmark index tuples that specifies how landmarks to
      be connected.
    landmark_drawing_spec: A DrawingSpec object that specifies the landmarks'
      drawing settings such as color and line thickness.
    connection_drawing_spec: A DrawingSpec object that specifies the
      connections' drawing settings such as color and line thickness.
    elevation: The elevation from which to view the plot.
    azimuth: the azimuth angle to rotate the plot.
  Raises:
    ValueError: If any connetions contain invalid landmark index.
  """
  if not landmark_list:
    return
  # plt.figure(figsize=(10, 10))
  # ax = plt.axes(projection='3d')
  # ax.view_init(elev=elevation, azim=azimuth)
  print(landmark_drawing_spec)
  plotted_landmarks = {}
  data_list = []
  dct = {'x': [], 'y': [], 'z': [], "color":[]}
  for idx, landmark in enumerate(landmark_list.landmark):
    if ((landmark.HasField('visibility') and
         landmark.visibility < _VISIBILITY_THRESHOLD) or
        (landmark.HasField('presence') and
         landmark.presence < _PRESENCE_THRESHOLD)):
      continue

    # data_list.append([-landmark.z, landmark.x, -landmark.y])
    dct["x"].append(-landmark.z)
    dct["y"].append(landmark.x)
    dct["z"].append(-landmark.y)
    color = landmark_drawing_spec.color[::-1]
    dct["color"].append(f"rgb({color[0]},{color[1]},{color[2]})")
    plotted_landmarks[idx] = (-landmark.z, landmark.x, -landmark.y)

  df = pd.DataFrame(dct)
  fig = ax.scatter_3d(
      df, x='x', y='y', z='z',
      # color="petal_length"
      color="color",
      # linewidth=landmark_drawing_spec.thickness
      )
  # if connections:
  #   num_landmarks = len(landmark_list.landmark)
  #   # Draws the connections if the start and end landmarks are both visible.
  #   for connection in connections:
  #     start_idx = connection[0]
  #     end_idx = connection[1]
  #     if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
  #       raise ValueError(f'Landmark index is out of range. Invalid connection '
  #                        f'from landmark #{start_idx} to landmark #{end_idx}.')
  #     if start_idx in plotted_landmarks and end_idx in plotted_landmarks:
  #       landmark_pair = [
  #           plotted_landmarks[start_idx], plotted_landmarks[end_idx]
  #       ]
  #       ax.line_3d(
  #           xs=[landmark_pair[0][0], landmark_pair[1][0]],
  #           ys=[landmark_pair[0][1], landmark_pair[1][1]],
  #           zs=[landmark_pair[0][2], landmark_pair[1][2]],
  #           color=_normalize_color(connection_drawing_spec.color[::-1]),
  #           linewidth=connection_drawing_spec.thickness)

  fig.write_html(dst_path)
