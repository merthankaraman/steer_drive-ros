#include <ros/ros.h>
#include <std_msgs/Float64.h>
#include <std_msgs/Bool.h>
#include <std_msgs/Int8.h>


#include "steer_drive_autonomous/actuators.h"
#include "steer_drive_autonomous/sensors.h"
#include <stdint.h>
#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <unistd.h>
#include <chrono>
#include <thread>
using namespace std;


int s;
struct sockaddr_can addr;
struct ifreq ifr;
struct can_frame frame;


void can_send_motor(float speed, float angle){
    float s = speed, a = angle;
    frame.can_id = 0x17;
    memcpy(frame.data, &s, 4);
    memcpy(&frame.data[4], &a, 4);
    write(s, &frame, sizeof(struct can_frame));
    //cout << "data send "<< endl;
}

// actuators.msg datas
/*
float32 motor_speed
float32 motor_angle
*/

// sensors.mgs datas:
/*
float32 motor_speed_now
float32 motor_angle_now
float32 motor_heat
float32 current
float32 current
*/
void send_sensors(const ros::Publisher pub){
    steer_drive_autonomous::sensors sensor;
    sensor.current = 2.0;
    sensor.current = 25.2;
    sensor.motor_heat = 22.2;
    sensor.motor_speed_now = 1.3;
    sensor.motor_angle_now = 3.14;
    pub.publish(sensor);

}

void motorsCallback(const steer_drive_autonomous::actuators& data){
    can_send_motor(data.motor_speed, data.motor_angle);
}

int main(int argc, char** argv){
    s = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    strcpy(ifr.ifr_name, "can0" ); // VCAN0 arayüzünün adı
    ioctl(s, SIOCGIFINDEX, &ifr);

    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    bind(s, (struct sockaddr *)&addr, sizeof(addr));

    frame.can_id = 0x17;
    frame.can_dlc = 8;

    ros::init(argc, argv, "can_communication_node");
    ros::NodeHandle nh;
    ros::Subscriber motors_sub = nh.subscribe("/Steer/motors", 1, motorsCallback);
    ros::Publisher pub = nh.advertise<steer_drive_autonomous::sensors>("/Steer/status", 10);

    ROS_INFO("CAN communication node has started");

    ros::Rate rate(20);
    while (ros::ok())
    {
        send_sensors(pub);
        rate.sleep();
        ros::spinOnce();
    }

    return 0;
}
