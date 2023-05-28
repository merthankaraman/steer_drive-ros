#include <ros/ros.h>
#include <tf/transform_broadcaster.h>
#include <nav_msgs/Odometry.h>
#include <std_msgs/Float64.h>
#include <geometry_msgs/Twist.h>
#include "steer_drive_autonomous/actuators.h"
#include "math.h"

double angle = 0.0, linear = 0.0;
double pi = 3.14159265;

double x = 0.0;
double y = 0.0;
double theta = 0.0;

ros::Publisher pub;
void cmv_vel_func(const geometry_msgs::Twist& msg);
float lineer_speed_limit = 2.0;

ros::Time current_time, last_time;

int main(int argc, char **argv){
    ros::init(argc, argv, "Steer_Drive_topic_node");
    ros::NodeHandle nh;
    
    pub = nh.advertise<steer_drive_autonomous::actuators>("/Steer/motors", 10);
    ros::Rate rate(20);
    ros::Subscriber cmd_sub = nh.subscribe("/cmd_vel",10,&cmv_vel_func);

    ros::Publisher odom_pub = nh.advertise<nav_msgs::Odometry>("odom", 50);
    tf::TransformBroadcaster odom_broadcaster;

    current_time = ros::Time::now();
    last_time = ros::Time::now();

    while (ros::ok()){
        /*
        current_time = ros::Time::now();

        // Calculate time elapsed since last loop
        double dt = (current_time - last_time).toSec();

        // Calculate distance traveled by each wheel since last loop
        double left_distance = hiz_sol_angular * dt;
        double right_distance = hiz_sag_angular * dt;

        // Calculate distance traveled and new position and heading of robot
        double distance = (left_distance + right_distance) / 2;
        double heading = theta + (right_distance - left_distance) / wheel_distance;
        x = x + distance * cos(heading);
        y = y + distance * sin(heading);
        theta = heading;

        // Publish odom message
        nav_msgs::Odometry odom;
        odom.header.stamp = current_time;
        odom.header.frame_id = "odom";
        odom.child_frame_id = "base_footprint";
        odom.pose.pose.position.x = x;
        odom.pose.pose.position.y = y;
        odom.pose.pose.position.z = 0.0;
        odom.pose.pose.orientation = tf::createQuaternionMsgFromYaw(theta);
        odom.twist.twist.linear.x = distance / dt;
        odom.twist.twist.angular.z = (right_distance - left_distance) / dt;
        odom_pub.publish(odom);

        // Publish transform between odom and base_link frames
        geometry_msgs::TransformStamped odom_trans;
        odom_trans.header.stamp = current_time;
        odom_trans.header.frame_id = "odom";
        odom_trans.child_frame_id = "base_footprint";
        odom_trans.transform.translation.x = x;
        odom_trans.transform.translation.y = y;
        odom_trans.transform.translation.z = 0.0;
        odom_trans.transform.rotation = tf::createQuaternionMsgFromYaw(theta);
        odom_broadcaster.sendTransform(odom_trans);

        // Update last loop time
        last_time = current_time;
        */
        
        ros::spinOnce();
        rate.sleep();
    }

    return 0;
}

void cmv_vel_func(const geometry_msgs::Twist& msg){
    linear = msg.linear.x;
    angle = msg.angular.z;
    if (ros::param::has("/Steer/lineer_speed_limit")) ros::param::get("/Steer/lineer_speed_limit", lineer_speed_limit);
    steer_drive_autonomous::actuators motors;

	if (linear > 0.0 and linear > lineer_speed_limit){
		linear = lineer_speed_limit;
    }
	else if (linear < 0.0 and linear < -lineer_speed_limit){
		linear = -lineer_speed_limit;
    }
		
	if (linear < 0.0)
	    angle *= -1;

    motors.motor_speed = linear;
    motors.motor_angle = angle;
    //printf("\n\nlinear: %f\nangle: %f\n\n\n", linear, angle); 
    pub.publish(motors);
}
