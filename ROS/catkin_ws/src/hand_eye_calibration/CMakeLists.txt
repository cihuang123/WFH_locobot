cmake_minimum_required(VERSION 2.8.3)
project(hand_eye_calibration)
add_compile_options(-std=c++11)

set(CMAKE_AUTOMOC ON)

SET(CMAKE_CXX_FLAGS "-fPIC")
set(CMAKE_INCLUDE_CURRENT_DIR ON)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  roslib
  tf
  std_msgs
  sensor_msgs
  geometry_msgs
  message_filters
  #visual_system
)

find_package(Boost REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(OpenCV REQUIRED)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES ${PROJECT_NAME}
  CATKIN_DEPENDS message_runtime
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
  ${Eigen3_INCLUDE_DIRS}
)


add_executable(static_hand_eye_calibration src/static_cam_calibration.cpp)
add_dependencies(static_hand_eye_calibration ${catkin_EXPORTED_TARGETS})
target_link_libraries(static_hand_eye_calibration ${catkin_LIBRARIES})

add_executable(static_hand_eye_calibration_left src/static_cam_left_calibration.cpp)
add_dependencies(static_hand_eye_calibration_left ${catkin_EXPORTED_TARGETS})
target_link_libraries(static_hand_eye_calibration_left ${catkin_LIBRARIES})

add_executable(get_transform src/get_transform.cpp)
target_link_libraries(get_transform ${Eigen3_LIBRARIES} ${catkin_LIBRARIES})
