import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import yaml
from ament_index_python.packages import get_package_share_directory
import os
import serial
import json
import asyncio

class EmotionsBridge(Node):

    def __init__(self, pause=False):

        super().__init__('emotions_bridge')

        self.serial = serial.Serial('/dev/ttyUSB1')

        self.motors = None
        #CARREGAR PARÂMETROS DO YAML    
        self.load_motors_params('motors.yaml')

        self.send_motors_config()
        
        self.current_emotion = 'neutral'
        self.send_emotion(self.current_emotion)

        self.sub_emotion = self.create_subscription(String, 'fbot_face/emotion', self.emotion_callback, 10)
        
    def send_motors_config(self):

        max_retries = 3
        retries = 0
        success = False

        while not success and retries<max_retries:
        
            motors_pins: dict = {
                "cmd": 1
            }

            for motor in self.motors:

                motors_pins[motor] = self.get_parameter(motor+'.pin').value

            data_str = json.dumps(motors_pins)

            data_bytes = data_str.encode('utf-8')

            self.serial.write(data_bytes)

            self.get_logger().info(data_bytes)

            if self.waitSerialResponse("success"):
                success = True
            else:
                retries+=1
                self.get_logger().info("send_motors_config() failed: trying again ("+str(max_retries-retries)+" left)")


    def waitSerialResponse(self, response_msg):

        received_msg = ""

        

        while True:
            if self.serial.in_waiting > 0:
                received_msg += self.serial.read(self.serial.in_waiting).decode('utf-8')

                if "}" in received_msg:  # Supondo que '\n' seja o delimitador
                    break

        start_index = received_msg.find("{\"response\"")
        end_index = received_msg.find("}", start_index)
        message = received_msg[start_index : end_index+1]

        received_json = json.loads(message)

        if response_msg == received_json["response"]:
            self.get_logger().info(f'Received expected response: {message}')
            return True
        else:
            self.get_logger().warn(f'Unexpected response received: {message}')
            return False



    def emotion_callback(self, msg):

        self.get_logger().info('Emotion received! ')
        self.current_emotion = msg.data
        self.send_emotion(self.current_emotion)

    def send_emotion(self, emotion):
        
        log_message = ''

        motors_dict = {
            "cmd": 2
        }

        for motor in self.motors:
            # write_msg = [motor, self.get_parameter(self.get_name()+'.'+motor+'.'+emotion).value] #opção com namespace
            write_msg = [motor, self.get_parameter(motor+'.'+emotion).value] #opção sem namespace

            #REALIZAR O ENVIO NO PROTOCOLO DO MICROCONTROLADOR
            #ROSTOPIC ou SERIAL

            motors_dict[motor] = write_msg[1]

            log_message = log_message + write_msg[0] + ': ' + str(write_msg[1]) + '\n'

        self.get_logger().info('Writing: '+self.current_emotion+'\n'+log_message)

        data_str = json.dumps(motors_dict)

        data_bytes = data_str.encode('utf-8')

        self.serial.write(data_bytes)

        self.get_logger().info(data_bytes)

        self.waitSerialResponse("success")

        return


    def load_motors_params(self, filename):

        with open(os.path.join(get_package_share_directory('fbot_head'), 'config', filename)) as config_file:
            config = yaml.safe_load(config_file)[self.get_name()]['ros__parameters']

        self.motors = config
        for motor, value in config.items():
            # self.declare_parameters(namespace=, parameters=[(motor+'.'+prop, subvalue) for prop, subvalue in value.items()]) #opção com namespace
            for param, value in value.items():
                self.declare_parameter(motor+'.'+param, value) #opção sem namespace
            

        # self.declare_parameter('eyebrow_left_vert.pin', 0)
            

def main(args=None):
    rclpy.init(args=args)
    node = EmotionsBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()