<div align="center">
    <h1 id="Header">Autonomous-R/C Car Hybrid System</h1>
</div>

This is Robotic Car Model with two control modes: Autonomous Control Mode and Remote Control Mode (Default). In the Autonomous Control Mode, car drives forward until it detects an obstacle at which point it stops and changes 
direction. Or, if we push the button, the car switches modes to  Remote Control Mod and responds only to commands given to it from the Java program. The car also contains an LED to indicate which mode it is in and a power switch to turn the whole thing on or off.

<p align="center" width="100%">
    <img width="40.5%" src="https://github.com/kananahmadov2001/RoboticCar/assets/135070652/08e34bba-d932-44cd-874e-59fd0da262a7"> 
    <img width="39.2%" src="https://github.com/kananahmadov2001/RoboticCar/assets/135070652/c47827ce-942e-4949-b0ef-e5d9bfabae6a"> 
</p>

<div align="center">
    <h2 id="Header">Serial and Remote Control Communication</h2>
</div>
One of the most essential points of this project was establishing serial communication between the Arduino and a Java program running on the laptop. Serial communication provides a simple and efficient way to transmit data between the Arduino and a Java program running on the laptop over a physical connection; it enables real-time control and data exchange between the car and the computer. This communication allows the Java program to send control commands to the Arduino, such as directing the robot to move forward, backward, turn left, or turn right. Additionally, it enables Arduino to send back important information, such as sensor readings and status updates, which can be used by the Java program to monitor the car's environment and behavior. So, to achieve this, I established a protocol in Java to send a variety of meaningful messages one byte at a time. Then, I used this protocol to control (or not control!) a robotic car from a Java program and send useful data about the car's location back to Java.

<div align="center">
    <h2 id="Header">Autonomous Control Mode</h2>
</div>
The Autonomous Control mode involves the car continuously monitoring its surroundings using an ultrasonic distance sensor. When the sensor detects an obstacle within a certain range, the car initiates a sequence to avoid the obstacle by backing up and then turning in a new direction. This behavior allows the car to navigate its environment autonomously, reacting to obstacles in real-time to avoid collisions.

<div align="center">
    <h2 id="Header">Remote Control Mode</h2>
</div>
In the Remote Control mode, I have implemented a non-blocking delta timing, a practical technique, to control the timing of the car’s various outgoing messages. This technique equips the car with the ability to process incoming messages and determine its distance from obstacles in a non-blocking manner, enhancing its overall efficiency. I also implemented an FSM with four states (idle, receiving, move, moveFor) for moving the car, then defined the commands for moving the car: f (forward), b (back), l (left), and r (right), whichever distance was sent from the incoming messages.
