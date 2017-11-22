#!/usr/bin/env python

import rospy
from tf import transformations
from geometry_msgs.msg import Pose, Point, Quaternion, Vector3, Polygon
from std_msgs import ColorRGBA
from rviz_tools_py.srv import MarkerLines, MarkerShapes
import rviz_tools

class MarkerManager:
  """
  Provide a service to publish different markers using rviz tools
  """
  def __init__(self):
    self.marker_factory = rviz_tools.RvizMarkers('world', 'visualization_marker')
    self.shapes_dict = {
      "Sphere":   self.marker_factory.publishSpheres,
      "Cube":     self.marker_factory.publishCubes,
      "Cylinder": self.marker_factory.publishCylinder,
      "Arrow":    self.marker_factory.publishArrow,
      "Axis":     self.marker_factory.publishAxis,
      "Plane":    self.marker_factory.publishPlane,
      "Mesh":     self.marker_factory.publishMesh,
      "Text":     self.marker_factory.publishText
    }
    self.lines_dict = {
      "Rectangle": self.marker_factory.publishRectangle,
      "Polygon":   self.marker_factory.publishPolygon,
      "Line":      self.marker_factory.publishLine,
      "Path":      self.marker_factory.publishPath
    }

  def lines_cb(self, req):
    if req.type not in self.lines_dict:
      rospy.logerr("[" + rospy.get_name + "]: Marker type" + req.type + "not available")
      return {'success': False}
    else:
      args = dict()
      # Parse points
      if len(req.points) < 2:
        rospy.logerr("[" + rospy.get_name + "]: Not enough points")
        return {'success': False}
      else:
        if req.type == "Rectangle" or req.type == "Line":
          args["point1"] = req.points[0]
          args["point2"] = req.points[1]
        elif req.type == "Path":
          args["path"] = req.points
        else:
          args["polygon"] = Polygon(req.points)
      # Parse color. If colorRGBA is empty, try using color instead. If not available, use random color.
      if req.colorRGBA != ColorRGBA():
        args["color"] = req.colorRGBA
      else:
        if req.color:
          args["color"] = self.marker_factory.getColor(req.color)
        else:
          args["color"] = self.marker_factory.getRandomColor()
        if req.alpha > 0 and req.alpha <= 1:
          args["color"].a = req.alpha
      # Parse width.
      if req.type != "Rectangle":
        if req.width > 0:
          args["width"] = req.width
        else:
          rospy.logerr("[" + rospy.get_name + "]: Invalid width")
          return {'success': False}
      # Parse lifetime_s
      if req.lifetime_s < 0:
        rospy.logerr("[" + rospy.get_name + "]: Negative lifetime_s")
        return {'success': False}
      elif req.lifetime_s == 0: # default
        args["lifetime"] = None
      else:
        args["lifetime"] = req.lifetime_s

      return {'success': self.lines_dict[req.type](**args)}

  def shapes_cb(self, req):
    if req.type not in self.shapes_dict:
      rospy.logerr("[" + rospy.get_name + "]: Marker type" + req.type + "not available")
      return {'success': False}
    else:
      args = dict()
      # Parse pose
      if not req.pose:
        rospy.logerr("[" + rospy.get_name + "]: Not enough pose")
        return {'success': False}
      else:
        if req.type == "Sphere":
          args["list_of_spheres"] = req.pose
        elif req.type == "Cube":
          args["list_of_cubes"] = req.pose
        else:
          args["pose"] = req.pose[0]
      # Parse color. If colorRGBA is empty, try using color instead. If not available, use random color.
      if req.colorRGBA != ColorRGBA():
        args["color"] = req.colorRGBA
      else:
        if req.color:
          args["color"] = req.color
        else:
          args["color"] = self.marker_factory.getRandomColor()
        if req.alpha > 0 and req.alpha <= 1:
          args["color"].a = req.alpha
      # Parse scale and dimensions (height, length, depth, width and radius).
      if req.type != "Cylinder" and req.type != "Axis" and req.type != "Plane":
        if req.scaleVector3 != Vector3():
          args["scale"] = req.scaleVector3
        else:
          if req.scale > 0:
            args["scale"] = req.scale
          else:
            rospy.logerr("[" + rospy.get_name + "]: No valid scale to use")
            return {'success': False}
      else:
        if req.type == "Cylinder":
          if req.height > 0:
            args["height"] = req.height
          else:
            rospy.logerr("[" + rospy.get_name + "]: Invalid height")
            return {'success': False}
          if req.radius > 0:
            args["radius"] = req.radius
          else:
            rospy.logerr("[" + rospy.get_name + "]: Invalid radius")
            return {'success': False}
        elif req.type == "Axis":
          if req.length > 0:
            args["length"] = req.length
          else:
            rospy.logerr("[" + rospy.get_name + "]: Invalid length")
            return {'success': False}
          if req.radius > 0:
            args["radius"] = req.radius
          else:
            rospy.logerr("[" + rospy.get_name + "]: Invalid radius")
            return {'success': False}
        else:
          if req.depth > 0:
            args["depth"] = req.depth
          else:
            rospy.logerr("[" + rospy.get_name + "]: Invalid depth")
            return {'success': False}
          if req.width > 0:
            args["width"] = req.width
          else:
            rospy.logerr("[" + rospy.get_name + "]: Invalid width")
            return {'success': False}
      # Parse filename
      if req.type == "Mesh":
        if req.filename:
          args["filename"] = req.filename
        else:
          rospy.logerr("[" + rospy.get_name + "]: Invalid filename")
          return {'success': False}
      # Parse text
      if req.type == "Text":
        if req.text:
          args["text"] = req.text
        else:
          rospy.logerr("[" + rospy.get_name + "]: Invalid text")
          return {'success': False}
      # Parse lifetime_s
      if req.lifetime_s < 0:
        rospy.logerr("[" + rospy.get_name + "]: Negative lifetime_s")
        return {'success': False}
      elif req.lifetime_s == 0:
        args["lifetime"] = None
      else:
        args["lifetime"] = req.lifetime_s

      return {'success': self.shapes_dict[req.type](**args)}

  def clean_up(self):
    rospy.loginfo("[" + rospy.get_name + "]: Clean up all markers")
    self.marker_factory.deleteAllMarkers()

if __name__ == "__main__":
  rospy.init_node("rviz_tools_py")
  marker_manager = MarkerManager()
  marker_lines_server = rospy.Service('marker_lines_server', MarkerLines, marker_manager.lines_cb)
  marker_shapes_server = rospy.Service('marker_shapes_server', MarkerShapes, marker_manager.shapes_cb)
  
  rospy.spin()