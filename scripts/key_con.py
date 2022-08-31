#!/usr/bin/env python  
# -*- coding: utf-8 -*  
  
import  os  
import  sys  
import  tty, termios  
import roslib; roslib.load_manifest('keyboard_control')  
import rospy  
from geometry_msgs.msg import Twist  
from std_msgs.msg import String  
from select import select
  
cmd = Twist()  
pub = rospy.Publisher('cmd_vel', Twist)  


def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)

def keyboardLoop():  
    settings = saveTerminalSettings()
    rospy.init_node('keyboard_control')  
    rate = rospy.Rate(rospy.get_param('~hz', 100))  
  
    walk_vel_ = rospy.get_param('walk_vel', 1.0)  
    run_vel_ = rospy.get_param('run_vel', 1.0)  
    yaw_rate_ = rospy.get_param('yaw_rate', 1.0)  
    yaw_rate_run_ = rospy.get_param('yaw_rate_run', 1.0)  
    timeout = rospy.get_param("~key_timeout", 0.2)
    max_tv = walk_vel_  
    max_rv = yaw_rate_  
  
    print ("Reading from keyboard" ) 
    print ("Use WASD keys to control the robot"  )
    print ("Press Caps to move faster" )
    print ("Press q to quit"  )
  
    while not rospy.is_shutdown():  
        
        fd = sys.stdin.fileno()  
        old_settings = termios.tcgetattr(fd)  
        old_settings[3] = old_settings[3] & ~termios.ICANON & ~termios.ECHO  
        
        tty.setraw(sys.stdin.fileno())
        # sys.stdin.read() returns a string on Linux
        rlist, _, _ = select([sys.stdin], [], [], timeout)
        if rlist:
            ch = sys.stdin.read(1)
        else:
            ch = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

        # try :  
        #     tty.setraw( fd )  
        #     ch = sys.stdin.read( 1 )  
        # finally :  
        #     termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  
  
        if ch == 'w':  
            max_tv = walk_vel_  
            speed = 1  
            turn = 0  
        elif ch == 's':  
            max_tv = walk_vel_  
            speed = -1  
            turn = 0  
        elif ch == 'a':  
            max_rv = yaw_rate_  
            speed = 0  
            turn = 1  
        elif ch == 'd':  
            max_rv = yaw_rate_  
            speed = 0  
            turn = -1  
        elif ch == 'W':  
            max_tv = run_vel_  
            speed = 1  
            turn = 0  
        elif ch == 'S':  
            max_tv = run_vel_  
            speed = -1  
            turn = 0  
        elif ch == 'A':  
            max_rv = yaw_rate_run_  
            speed = 0  
            turn = 1  
        elif ch == 'D':  
            max_rv = yaw_rate_run_  
            speed = 0  
            turn = -1  
        elif ch == 'q':  
            exit()  
        else:  
            max_tv = walk_vel_  
            max_rv = yaw_rate_  
            speed = 0  
            turn = 0  
  

        cmd.linear.x = speed * max_tv;  
        cmd.angular.z = turn * max_rv;  
        pub.publish(cmd)  
        
        rate.sleep()  
        stop_robot();  
  
def stop_robot():  
    cmd.linear.x = 0.0  
    cmd.angular.z = 0.0  
    #pub.publish(cmd)  
  
if __name__ == '__main__':  
    try:  
        keyboardLoop()  
    except rospy.ROSInterruptException:  
        pass