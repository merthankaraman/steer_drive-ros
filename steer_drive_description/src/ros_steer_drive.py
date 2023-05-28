#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
from steer_drive_autonomous.msg import actuators
import std_msgs.msg
import math
node_name = "Ros_Steer_Drive_Controller"
steers_msg = std_msgs.msg.Float64()
drives_msg = std_msgs.msg.Float64()
status_msg = std_msgs.msg.Float64MultiArray()

lineer_speed_limit = 2.0
soft_inc = True
speed_now= 0.0
angular_now = 0.0
angle = 0.0
x = 0.0
motor_datas = {"angles": 0.0, "velocities": 0.0 }


def soft_inc_fon(speed_now, speed_ask, inc_rate = 60.0):
	if speed_ask > speed_now:
		speed_now += inc_rate
	elif speed_ask < speed_now:
		speed_now -= inc_rate
	if abs(speed_ask - speed_now) < 0.1:
		speed_now = speed_ask
	return speed_now

def actuators_fonk(data):
	global speed, angle, lineer_speed_limit
	lineer_speed_limit = rospy.get_param("Steer/lineer_speed_limit", 2.0)
	steer_gear_ratio = rospy.get_param("steer_gear_ratio", 1)
	drive_gear_ratio = rospy.get_param("drive_gear_ratio", 60)

	speed, angle = data.motor_speed * drive_gear_ratio, data.motor_angle * steer_gear_ratio

	# if data.motor_speed > 0.0 and data.motor_speed > lineer_speed_limit:
	# 	speed = lineer_speed_limit * drive_gear_ratio
	# elif data.motor_speed < 0.0 and data.motor_speed < -lineer_speed_limit:
	# 	speed = -lineer_speed_limit * drive_gear_ratio
		
	# if speed < 0.0:
	# 	angle *= -1

	motor_datas["velocities"] = speed
	motor_datas["angles"] = angle


def control():
	global steers, drives, status, speed, angle, soft_inc
	global steers_msg, drives_msg, status_msg, speed_now, angular_now
	soft_inc = rospy.get_param("user_param_steer_soft_motion", False)
	if soft_inc:
		steers_msg.data= soft_inc_fon(steers_msg.data, motor_datas["angles"], abs(steers_msg.data - motor_datas["angles"])/8)
		drives_msg.data = soft_inc_fon(drives_msg.data, motor_datas["velocities"] , abs(drives_msg.data- motor_datas["velocities"])/10)
	else:
		steers_msg.data = motor_datas["angles"]
		drives_msg.data = motor_datas["velocities"]
	status_msg.data = [steers_msg.data] + [drives_msg.data]
	#print(status_msg.data )
	steers.publish(steers_msg.data)
	drives.publish(drives_msg.data)
	status.publish(status_msg)

rospy.init_node(node_name, anonymous=True)

publisher_name = rospy.get_param("publisher_name", "steer_drive")

controls = "rear"

steers = rospy.Publisher(f"/{publisher_name}/{controls}_steer_pos_motor_controller/command", std_msgs.msg.Float64, queue_size=10)
drives = rospy.Publisher(f"/{publisher_name}/{controls}_drive_vel_motor_controller/command", std_msgs.msg.Float64, queue_size=10)
status = rospy.Publisher(f"/{publisher_name}/status", std_msgs.msg.Float64MultiArray, queue_size=10)
sub = rospy.Subscriber("/Steer/motors", actuators, actuators_fonk)

def main():
	rospy.loginfo(f"{node_name} has started")
	rate = rospy.Rate(50)
	while True:
		control()
		rate.sleep()
	#rospy.spin()


if __name__ == '__main__':
	try:
		main()
		
	except rospy.ROSInterruptException:
		pass