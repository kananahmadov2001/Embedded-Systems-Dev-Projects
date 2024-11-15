<div align="center">
    <h1 id="Header">PiCar-Control-System-Performance</h1>
</div>

PiCar is a robotic platform that uses Raspberry Pi, a small single-board computer, as its primary control unit. The PiCar we built for the Final Module included the sensors: Camera, DC Motor, Servos(s), Analog-to-Digital Converter, and Ultrasonic sensors. It has the Ultrasonic sensor for the eyes and the Camera as its mouth. The Ultrasonic Sensor also has a built in voltage divider to convert the 5 V for the Echo down to 3.3 V input to the Raspberry Pi. The DC motor is installed on the back of the PiCar; the motor has a rear-wheel drive connected to some gears underneath that drive the wheels. The Analog-to-Digital Converter (ADC) is also connected to the back end of the car next to the motor. The ADC was also connected to a photoresistor at channel 0 and an LED light that pointed at the inside of the left back wheel where the black and white disk is installed. Regarding the Servo(s), our PiCar has three servomotors on it:
* Nod servomotor (for tilting the head up and down)
* Swivel servomotor (for twisting the head left and right)
* Steer servomotor (for steering the front wheels left and right)

<p align="center" width="100%">
    <img width="50%" src="https://github.com/kananahmadov2001/PiCar-System-Control-Performance/assets/135070652/28984a60-a50c-4976-ba48-2b17961fa3f6"> 
</p>

Other than the sensors, the PiCar’s Power component is also essential. The Power LEDs and switch is located on the PWM HAT, which sits on top of the Raspberry Pi. The up/down switch controlls the power from the batteries located under the PiCar, and the four LEDs indicates how much power was left in the batteries.

<p align="center" width="100%">
    <img width="50%" src="https://github.com/kananahmadov2001/PiCar-System-Control-Performance/assets/135070652/fec7c5b2-c88e-4d00-b544-056300e7df36"> 
</p>

Through the implementation of knowledge and methods learned from our ESE 205: Engineering Design class and the idea of PID control, we were able to successfully complete our "PiCar System Performance and Control" project, which had three objectives: Control, Movement, and Movement with Control. 


<div align="center">
    <h2 id="Header">Objective 1: Control</h2>
</div>

The primary focus of our first objective was to design a control system for the PiCar. We overcame significant challenges and successfully implemented a PID-control system, effectively controlling motor speed in a no-load environment. 

<p align="center" width="100%">
    <img width="50%" src="https://github.com/kananahmadov2001/PiCar-System-Control-Performance/assets/135070652/ad107880-8322-4abc-84ff-783b036f044f"> 
</p>

We got a steady velocity-time plot for the PiCar with only Control at the RPS of 5. The strange bottom spike at the t = 2.4 sec could be due to some bad photo-resistor reading. Regarding the system performance results, we calculated the RPS of 4.929 for our plot and found the Peak RPS to be 6.240. Since calculated the RPS, then the Steady State Error is 0.071. The 90% of our calculated RPS is 4.436, therefore we found the Response Time to be t = 0.60 sec where the RPS value has a sharp increase to an RPS of 5.940 – past an RPS of 4.436. Finally, the OverShoot was -24.8%. To justify the reasoning why our real time calculations are accurate, we modified our plotting program and just examined a steady state portion of that data (power of 2 amount of data) to determine the FFT.

<p align="center" width="100%">
    <img width="50%" src="https://github.com/kananahmadov2001/PiCar-System-Control-Performance/assets/135070652/5fd64270-9a65-42ce-ae2f-2afe4d377a7f"> 
</p>


<div align="center">
    <h2 id="Header">Objective 2: Movement</h2>
</div>

The second objective was to create a program that would drive the PiCar to a blue object positioned at least 10 feet away, with the PiCar turned up to 30◦ degrees away from the blue object in either direction. We used an ultrasonic sensor to control motor speed and a camera-angle-tracking algorithm to control servos in an effort to meet speed, distance, and direction targets as the PiCar traversed to a blue object. 


<div align="center">
    <h2 id="Header">Objective 3: Movement with Control</h2>
</div>

For our third objective, we combined the methods from the first two objectives. This allowed us to use PID control and camera tracking to achieve a level of precision and accuracy in pathing to the blue object, all while maintaining a constant driving speed of 5 RPS. 

<p align="center" width="100%">
    <img width="50%" src="https://github.com/kananahmadov2001/PiCar-System-Control-Performance/assets/135070652/546e58ce-4fb0-4180-8fd1-6035fdde1a6b"> 
</p>

The velocity-time plot with Movement and Control is not as smooth as the velocity-time plot with only Control; this is due to the increased system dynamics, non-linearities, and the friction. Regarding the system performance results, we calculated the RPS of 4.812 for our plot and found the Peak RPS to be 6.450. Since calculated the RPS, then the Steady State Error is 0.188. The 90% of out calculated RPS is 4.331, therefore we founded Response Time to be t = 3.935 sec at RPS of 5.004. Finally, the OverShoot was 29.0%

<div align="center">
    <h2 id="Header">Conclusion</h2>
</div>

Ultimately, through these objectives, we concluded that Kp balances the stability. The system may be slow and exhibit steady-state error if it's too low. If it's too high, it can cause instability. Ki ensures the system remains stable while achieving the desired accuracy. It should be set to correct steady-state errors without causing oscillation or overshooting. Finally, Kd should dampen oscillations and stabilize the system without introducing excess noise. Future investigations into PID control would serve to further display the complex relationships between the three coefficients: Kp, Ki, and Kd.

If you would like to know more about our "PiCar-System-Control-Performance" project, checkout our report: https://github.com/kananahmadov2001/PiCar-System-Control-Performance/blob/main/Final_Report_ESE205.pdf
