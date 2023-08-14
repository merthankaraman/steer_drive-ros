#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
import sensor_msgs.msg
import math
import time
from rosgraph_msgs.msg import Log

cmd_vel_msg = Twist()
node_name = "ROS_Joystick_Cmd_Controller"
old_x = 0
old_qz = 0
lineer_speed_limit = 1.0
wireless = False
use_joystick = True
hand_break = True
hand_break_stuff = False

first_control_r = True
first_control_l = True

message_periodic = True 
message_period = 10
time_old = time.time()
joystick_node_ok = True
x, y, qz = 0.0, 0.0, 0.0


def cmd_fonk(data):
	global wireless, use_joystick, hand_break, hand_break_stuff
	global cmd_vel, cmd_vel_msg, first_control_r, first_control_l, x, y, qz
	#wireless = rospy.get_param("user_param_joystick_wireless")
	#use_joystick = rospy.get_param("user_param_joystick_use")
	lineer_speed_limit = rospy.get_param("Steer/lineer_speed_limit", 2.0)
	rate = rospy.Rate(10)
	l3 = [0.0, 0.0]
	r3 = [0.0, 0.0]
	l2 = 1.0
	r2 = 1.0
	if use_joystick:
		#print(data.axes[:6])
		#print(data.buttons)
		#print(data)
		#print("aa")
		x, qz, y = 0.0, 0.0, 0.0
		if wireless:
			button_x = data.buttons[1]
			l3[0] = data.axes[0]# * -1
			l3[1] = data.axes[1]
			l2 = ((data.axes[3] * -1) + 1.0) / 2.0
			r2 = ((data.axes[4] * -1) + 1.0) / 2.0
			r3[0] = data.axes[2]
			r3[1] = data.axes[5]
			button_o = data.buttons[2]
			button_r1 = data.buttons[5]
		else:
			button_x = data.buttons[0]
			l3[0] = data.axes[0]# * -1
			l3[1] = data.axes[1]
			l2 = ((data.axes[2] * -1) + 1.0) / 2.0
			r2 = ((data.axes[5] * -1) + 1.0) / 2.0
			button_o = data.buttons[1]
			button_r1 = data.buttons[2]
		if first_control_r:
			if r2 == 0.5:
				r2 = 0.0
			else:
				first_control_r = False
		if first_control_l:
			if l2 == 0.5:
				l2 = 0.0
			else:
				first_control_l = False

		if r3[0] == 0.0 and r3[1] == 0.0:
			x = (r2 + (l2 * -1)) * lineer_speed_limit
			qz = l3[0] * (math.pi/2)/2
		else:
			y = r3[0] * lineer_speed_limit
			x = r3[1] * lineer_speed_limit
		if button_x == 1:
			if x < 0:
				x -= 5
			elif x > 0:
				x += 5
			else:
				x = 0
		if button_o:
			qz += math.pi
		if hand_break_stuff:
			if button_r1:
				cmd_vel_msg.linear.x = x
				cmd_vel_msg.linear.y = y
				cmd_vel_msg.angular.z = qz
			elif not button_r1:
				rospy.logfatal("Hand break is on")
				cmd_vel_msg = Twist()
		else:
			cmd_vel_msg.linear.x = x
			cmd_vel_msg.linear.y = y
			if x < 0.0:
				cmd_vel_msg.angular.z = -qz
			else:
				cmd_vel_msg.angular.z = qz
		cmd_vel.publish(cmd_vel_msg)
		#rate.sleep()
	else:
		rospy.logfatal_once(f"{node_name} Has Stopped")
		rospy.get_node_uri()

def log_callback(data):
	global joystick_node_ok
	joystick_node_ok = True
	if "Couldn't open joystick /dev/input/js0. Will retry every second" in data.msg:
		joystick_node_ok = False

rospy.init_node(node_name, anonymous=True)
cmd_vel = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
sub = rospy.Subscriber('/j0/joy', sensor_msgs.msg.Joy, cmd_fonk)
sub2 = rospy.Subscriber('/rosout', Log, log_callback)

def stop():
	cmd_vel_msg = Twist()
	cmd_vel.publish(cmd_vel_msg)
	rospy.logfatal(f"{node_name} Has Stopped")


def main():
	global wireless, use_joystick, hand_break, hand_break_stuff
	global cmd_vel, cmd_vel_msg, first_control_r, first_control_l, time_old, x, y, qz

	rospy.loginfo_once(f"{node_name} has started")
	rospy.on_shutdown(stop)
	while not rospy.is_shutdown ():
		if not joystick_node_ok:
			rospy.signal_shutdown("disconnect")
			stop()
			
		if message_periodic and ((time.time() - time_old) >= 1.0/message_period):
			#print(joystick_node_ok)
			#print(cmd_vel_msg.linear.x, "\t", cmd_vel_msg.angular.z)
			#print(1/(time.time() - time_old) ," hz")
			#print("\n\n", cmd_vel_msg, "\n\n", x, "\t", qz, "\n")
			cmd_vel.publish(cmd_vel_msg)
			time_old = time.time()
	rospy.spin()

if __name__ == '__main__':
	try:
		main()		
	except rospy.ROSInterruptException:
		pass
