#!~/ros2-ai/objectpushing/bin python3
# -*- coding: utf-8 -*-

# ROS related
import rclpy
from rclpy.node import Node
from msgs_interfaces.srv import ChatGPT
from std_msgs.msg import Float64MultiArray, MultiArrayDimension, MultiArrayLayout
from std_srvs.srv import Empty

# LLM related
import json
import os
from openai_config import UserConfig
config = UserConfig()


class ArmRobot(Node):
    def __init__(self):
        super().__init__("arm_robot")

        # Publisher for target_pose
        self.target_pose_publisher = self.create_publisher(
            Float64MultiArray, "/target_pose", 10
        )

        # Server for function call
        self.function_call_server = self.create_service(
            ChatGPT, "/ChatGPT_function_call_service", self.function_call_callback
        )
        # Node initialization log
        self.get_logger().info("ArmRobot node has been initialized")

    def function_call_callback(self, request, response):
        req = json.loads(request.request_text)
        function_name = req["name"]
        function_args = json.loads(req["arguments"])
        func_obj = getattr(self, function_name)
        try:
            function_execution_result = func_obj(**function_args)
        except Exception as error:
            self.get_logger().info(f"Failed to call function: {error}")
            response.response_text = str(error)
        else:
            response.response_text = str(function_execution_result)
        return response

    def publish_target_pose(self, **kwargs):
        """
        Publishes target_pose message to control the movement of arx5_arm
        """

        x_value = kwargs.get("x", 0.2)
        y_value = kwargs.get("y", 0.2)
        z_value = kwargs.get("z", 0.2)

        roll_value = kwargs.get("roll", 0.2)
        pitch_value = kwargs.get("pitch", 0.2)
        yaw_value = kwargs.get("yaw", 0.2)

        pose = [x_value, y_value, z_value, roll_value, pitch_value, yaw_value]
        pose_str = ', '.join(map(str, pose))

        command=f"ros2 topic pub /target_pose std_msgs/msg/Float64MultiArray '{{data: [{pose_str}]}}' -1"
        os.system(command)
        self.get_logger().info(f"Published target message successfully: {pose}")
        return pose_str



def main():
    rclpy.init()
    arm_robot = ArmRobot()
    rclpy.spin(arm_robot)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
