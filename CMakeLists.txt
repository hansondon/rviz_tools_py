cmake_minimum_required(VERSION 2.8.3)
project(rviz_tools_py)

find_package(catkin REQUIRED
  rospy
  tf
  geometry_msgs
  std_msgs
  visualization_msgs
  message_generation
)

catkin_python_setup()
add_service_files(FILES MarkerLines.srv MarkerShapes.srv)
generate_messages(DEPENDENCIES geometry_msgs std_msgs visualization_msgs)

catkin_package(
  CATKIN_DEPENDS geometry_msgs message_runtime 
)