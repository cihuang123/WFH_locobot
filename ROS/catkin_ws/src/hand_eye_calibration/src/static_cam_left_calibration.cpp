#include <fstream>
#include <boost/filesystem.hpp>
#include <ros/ros.h>
#include <ros/package.h>
#include <tf/transform_listener.h>
#include <geometry_msgs/Pose.h>
#include <sensor_msgs/JointState.h>

/*
 *  Hand-eye automatically calibration, collecting data process
 *  Note: Remember to broadcast \fake_tcp\ frame, this can be measured easily
 *        This frame represents the tag center in arm's coordinate
 *  
 *  Parameters:
 *    dy: y difference in meter
 *    dz: z difference in meter
 *    tag_frame: target tag frame
 *    file_name: output file name
 *  Service: /ur5_control_server/ur_control/goto_pose
 *  Frame: base_link, ee_link, tcp_link, tag_frame
 *  Editor: Sean Lu
 *  Last edited: 5/16, 2019
 */

class calibration{
 private:
  int count = 0; // Counter for process
  double dx, dz; // Predefined path distance
  std::fstream fs; // file stream
  std::string tag_frame; // frame id for tag, from parameter server
  std::string package_path; // package path
  std::string file_name; // file name, from parameter server
  std::string file_path; // file path = package path + folder + file name + file extension
  ros::NodeHandle nh_; // public node handler
  ros::NodeHandle pnh_; // private node handler
  ros::Publisher arm_control;
  geometry_msgs::Pose original_pose; // robot arm pose
  sensor_msgs::JointState joint_command; // robot arm pose
  tf::TransformListener listener;
  /*
   *  Write the data to file
   *  format: x(hand coord.) y(hand coord.) z(hand coord.) x(eye_coord.) y(eye_coord.) z(eye_coord.)
   *  [param]in geometry_msgs::Pose p_tcp: pose of tag in hand coordinate
   *  [param]in geometry_msgs::Pose p_tag: pose of tag in eye coordinate
   */
  void write_data(geometry_msgs::Pose p_tcp, geometry_msgs::Pose p_tag){
    fs << p_tcp.position.x << " "
       << p_tcp.position.y << " "
       << p_tcp.position.z << " "
       << p_tag.position.x << " "
       << p_tag.position.y << " "
       << p_tag.position.z << "\n";
  }
  /*
   *  Get tag transformation in eye coordinate
   *  [param]in tf::StampedTransform &t: transform reference
   *  [param]out bool: 0 if cannot get transform, 1 otherwise
   */
  bool get_tag_data(tf::StampedTransform &t){
    try{
      listener.waitForTransform("camera_left_link", "left_tag_0", ros::Time(0), ros::Duration(2.0));
      listener.lookupTransform("camera_left_link", "left_tag_0", ros::Time(0), t);
    } catch(tf::TransformException ex){
      ROS_ERROR("%s", ex.what());
      return 0;
    }
    ROS_INFO("Eye coord.: %f, %f, %f", t.getOrigin().getX(), t.getOrigin().getY(), t.getOrigin().getZ());
    return 1;
  }
  /*
   *  Get tag transformation in hand coordinate
   *  [param]in tf::StampedTransform &t: transform reference
   *  [param]in std::string target: which frame we want, either \ee_link\ or \tcp_link\
   *  [param]out bool: 0 if cannot get transform, 1 otherwise
   */
  bool get_arm_data(tf::StampedTransform &t, std::string target){
    try{
      listener.waitForTransform("base_link", "ar_tag", ros::Time(0), ros::Duration(2.0));
      listener.lookupTransform("base_link", "ar_tag", ros::Time(0), t);
    } catch(tf::TransformException ex){
      ROS_ERROR("%s", ex.what());
      return 0;
    }
    if(target=="ar_tag")
      ROS_INFO("Hand coord.: %f, %f, %f", t.getOrigin().getX(), t.getOrigin().getY(), t.getOrigin().getZ());
    return 1;
  }
  /*
   *  Convert stamped transform to pose
   *  [param]in tf::StampedTransform t: transform to convert
   *  [param]out geometry_msgs::Pose: pose that encode the information of t
   */
  geometry_msgs::Pose transform2Pose(tf::StampedTransform t){
    geometry_msgs::Pose res;
    res.position.x = t.getOrigin().getX();
    res.position.y = t.getOrigin().getY();
    res.position.z = t.getOrigin().getZ();
    res.orientation.x = t.getRotation().getX();
    res.orientation.y = t.getRotation().getY();
    res.orientation.z = t.getRotation().getZ();
    res.orientation.w = t.getRotation().getW();
    res.orientation.x = 0;
    res.orientation.y = 0;
    res.orientation.z = 0;
    res.orientation.w = 1;
    return res;
  }
  /*
   *  Calibration process, the robot arm will follow the predefined path and receive data
   *  Predefined path:
   *    0  3  4  7  8
   *     --         |
   *     dy      dz |
   *                |
   *    1  2  5  6  9
   */
  void calibration_process(void){
    while(count<9){
      ROS_INFO("----------- %d -----------", count);
      
      joint_command.position.resize(7);
      // switch(count){
      //  //2023 old path of calibration
      //   case 0:
      //     joint_command.position[0] = 0.0;
      //     joint_command.position[1] = 0.0;
      //     joint_command.position[2] = -0.17947575449943542;
      //     joint_command.position[3] = -0.42031073570251465;
      //     joint_command.position[4] = 1.2793400287628174;
      //     joint_command.position[5] = -0.921922504901886;
      //     joint_command.position[6] = 0.0;
          
      //     break;
      //   case 1:
      //     joint_command.position[0] = 0.0;
      //     joint_command.position[1] = 0.0;
      //     joint_command.position[2] = -0.4463884234428406;
      //     joint_command.position[3] = -0.4801360070705414;
      //     joint_command.position[4] = 1.2041749954223633;
      //     joint_command.position[5] = -0.7516506314277649;
      //     joint_command.position[6] = 0.0;
          
      //     break;
      //   case 2:
      //     joint_command.position[0] = 0.0;
      //     joint_command.position[1] = 0.0;
      //     joint_command.position[2] = -0.21935926377773285;
      //     joint_command.position[3] = 0.33133986592292786;
      //     joint_command.position[4] = 0.24236896634101868;
      //     joint_command.position[5] = -0.7102331519126892;
      //     joint_command.position[6] = 0.0;
          
      //     break;
      //   case 3:
      //     joint_command.position[0] = 0.0;
      //     joint_command.position[1] = 0.0;
      //     joint_command.position[2] = -0.01840776950120926;
      //     joint_command.position[3] = -0.2346990704536438;
      //     joint_command.position[4] = 1.0323691368103027;
      //     joint_command.position[5] = -0.7992039918899536;
      //     joint_command.position[6] = 0.0;
          
      //     break;
      
      //   case 4:
      //     joint_command.position[0] = 0.0;
      //     joint_command.position[1] = 0.0;
      //     joint_command.position[2] = 0.39599651930881474;
      //     joint_command.position[3] = 0.694925283216342;
      //     joint_command.position[4] = -0.30707004722297415;
      //     joint_command.position[5] = -0.3878552359933678;
      //     joint_command.position[6] =  -0.0;
        
      //     break;
      //   case 5:
      //     joint_command.position[0] = 0.0;
      //     joint_command.position[1] = 0.0;
      //     joint_command.position[2] = 0.7608544826507568;
      //     joint_command.position[3] = -0.2208932340145111;
      //     joint_command.position[4] = 1.142815709114747;
      //     joint_command.position[5] = -0.8835729360580444;
      //     joint_command.position[6] = 0.0;
         
      //     break;
      //   case 6:
      //     joint_command.position[0] = 0.0;
      //     joint_command.position[1] = 0.0;
      //     joint_command.position[2] = 0.03374757990241051;
      //     joint_command.position[3] = -0.2653786838054657;
      //     joint_command.position[4] = 1.4051264524459839;
      //     joint_command.position[5] = -1.1627575159072876;
      //     joint_command.position[6] = -0.0;
      //     break;
      // }
      switch(count){
       // new path in tutorial
        case 0:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = 0.7192560919416702;
          joint_command.position[3] = 0.007935531271520774;
          joint_command.position[4] = 0.8674325239257196;
          joint_command.position[5] = -0.8753680551972404;
          joint_command.position[6] = 0.0;
          
          break;
        case 1:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = 0.43680286462764245;
          joint_command.position[3] = 0.4535056365584407;
          joint_command.position[4] = -0.031556044701666786;
          joint_command.position[5] = -0.4219495918567739;
          joint_command.position[6] = 0.0;
          
          break;
        case 2:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = 0.31840939618232694;
          joint_command.position[3] = -0.17884662415840327;
          joint_command.position[4] = 0.6440863581064384;
          joint_command.position[5] = -0.4652397339480352;
          joint_command.position[6] = 0.0;
          
          break;
        case 3:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = 0.4127262431486712;         
          joint_command.position[3] = -0.043653784566603376;
          joint_command.position[4] = 1.1187589264379618;
          joint_command.position[5] = -1.0751051418713584;
          joint_command.position[6] = 0.0;
          
          break;  
        case 4:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = 0.0;         
          joint_command.position[3] = -0.12038027303164923;
          joint_command.position[4] = 0.9573324703816067;
          joint_command.position[5] = -0.8369521973499575;
          joint_command.position[6] = 0.0;
          
          break;
      
        case 5:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = -0.20466997064680967;
          joint_command.position[3] = -0.18059834043596634;
          joint_command.position[4] = 1.1052399907767243;
          joint_command.position[5] = -0.924641650340758;
          joint_command.position[6] =  -0.0;
        
          break;
        case 6:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = -0.19483267984183247;
          joint_command.position[3] = -0.46850018532652804;
          joint_command.position[4] = 0.7999040321528218;
          joint_command.position[5] = -0.33140384682629376;
          joint_command.position[6] =  -0.0;
        
          break;
        case 7:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = -0.45698761867037224;
          joint_command.position[3] = -0.3722117745093646;
          joint_command.position[4] = 1.136903525580398;
          joint_command.position[5] = -0.7646917510710335;
          joint_command.position[6] = 0.0;
         
          break;
        case 8:
          joint_command.position[0] = 0.0;
          joint_command.position[1] = 0.0;
          joint_command.position[2] = -0.2890000205307939;
          joint_command.position[3] = 0.2777687362896786;
          joint_command.position[4] = 0.4470723703809171;
          joint_command.position[5] = -0.7248411066705956;
          joint_command.position[6] = -0.0;
          break;
      }


      arm_control.publish(joint_command);
      ros::Duration(5.0).sleep();

      tf::StampedTransform st;
      get_tag_data(st);
      geometry_msgs::Pose p_tag = transform2Pose(st);
      get_arm_data(st, "ar_tag"); // Remember to broadcast fake_tcp frame
      geometry_msgs::Pose p_tcp = transform2Pose(st);
      write_data(p_tcp, p_tag);

      ++count;
    }
    ROS_INFO("Go home..."); // back to first pose
    // joint_command.position = [0.0, 0.0, -0.17947575449943542, -0.42031073570251465, 1.2793400287628174, -0.921922504901886, 0.11504856497049332];
    // arm_control.publish(joint_command);

    ros::Duration(1.0).sleep();
  }
  
 public:
  // Constructor
  calibration(ros::NodeHandle nh, ros::NodeHandle pnh): nh_(nh), pnh_(pnh), count(0){
    // Get parameters
    if(!pnh_.getParam("dx", dx)) dx = 0.05; ROS_INFO("dx: %f", dx);
    if(!pnh_.getParam("dz", dz)) dz = 0.05; ROS_INFO("dz: %f", dz);
    if(!pnh_.getParam("tag_frame", tag_frame)) tag_frame = "tag_0"; ROS_INFO("tag frame is: %s", tag_frame.c_str());
    if(!pnh_.getParam("file_name", file_name)) file_name = "calibration"; ROS_INFO("file_name: %s", file_name.c_str());

    package_path = ros::package::getPath("hand_eye_calibration");
    file_path = package_path + "/data/" + file_name + ".txt";
    // Check if data directory exist
    boost::filesystem::path p(package_path+"/data");
    if(!boost::filesystem::exists(p)){
      ROS_INFO("Directory doesnot exist, creating one...");
      boost::filesystem::create_directory(p);
    }

    fs.open(file_path, std::fstream::out | std::fstream::app); // Write file at the end
    if(!fs.is_open()) {ROS_ERROR("Cannot open file!"); ros::shutdown();}
    
    arm_control = nh_.advertise<sensor_msgs::JointState>("/joint_states_test", 10);

    ROS_INFO("Start process");
    tf::StampedTransform transform;
    get_arm_data(transform, "ar_tag");
    original_pose = transform2Pose(transform);

    calibration_process();

    ROS_INFO("End process");
    ros::shutdown();
  }
  // Desctructor
  ~calibration(){
    fs.close();
  }
};

int main(int argc, char** argv)
{
  ros::init(argc, argv, "calibration_node");
  ros::NodeHandle nh, pnh("~");
  calibration foo(nh, pnh);
  while(ros::ok()) ros::spinOnce();
  return 0;
}