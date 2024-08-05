#include <cv_bridge/cv_bridge.h>
#include <image_transport/image_transport.h>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <ros/ros.h>
#include <sensor_msgs/image_encodings.h>

class ImageProcessor
{
public:
    ImageProcessor(const ros::NodeHandle &nh, const ros::NodeHandle &nh_private)
        : nh_(nh), nh_private_(nh_private)
    {
        image_transport::ImageTransport it(nh_);
        sub = it.subscribe("image", 1, &ImageProcessor::imageCallback, this);
        pub = it.advertise("output_image", 1);
        nh_private_.param<std::string>("output_frame_id", output_frame_id, "");
    }

    void imageCallback(const sensor_msgs::ImageConstPtr &msg)
    {
        cv_bridge::CvImagePtr cv_ptr;
        try
        {
            if (msg->encoding == "16UC1")
            {
                cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::TYPE_16UC1);
            }
            else
            {
                cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
            }
        }
        catch (cv_bridge::Exception &e)
        {
            ROS_ERROR("cv_bridge exception: %s", e.what());
            return;
        }
        cv::Mat rotated_image;
        cv::rotate(cv_ptr->image, rotated_image, cv::ROTATE_180);

        cv_ptr->image = rotated_image;

        sensor_msgs::ImagePtr msg_out = cv_ptr->toImageMsg();
        msg_out->header.stamp = msg->header.stamp;
        msg_out->header.frame_id = output_frame_id.empty() ? msg->header.frame_id : output_frame_id;
        pub.publish(msg_out);
    }

private:
    ros::NodeHandle nh_;
    ros::NodeHandle nh_private_;
    image_transport::Subscriber sub;
    image_transport::Publisher pub;
    std::string output_frame_id;
};

int main(int argc, char **argv)
{
    ros::init(argc, argv, "rotate_compress_image");
    ros::NodeHandle nh;
    ros::NodeHandle nh_private("~");
    ImageProcessor imageProcessor(nh, nh_private);
    ros::spin();
    return 0;
}
