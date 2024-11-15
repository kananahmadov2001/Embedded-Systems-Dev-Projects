package communication;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

import jssc.*;

enum State {
	MAGICNUMBER,
	KEY,
	ERROR,
	INFO,
	TIMESTAMP,
	POTENTIAL,
	ECHO,
	BADMESSAGE
}

public class RemoteControl {
	
	final private SerialComm port;
	
	public RemoteControl(String portname) throws SerialPortException {
		port = new SerialComm(portname);
	}
	
	
	final byte magicNum = 0x21;
	final byte info = 0x30;
	final byte error = 0x31;
	final byte time = 0x32;
	final byte potentiometer = 0x33;
	final byte echo = 0x34;
	final byte move = 0x35;
	
	
	State state = State.MAGICNUMBER;

	public void run() throws SerialPortException, IOException {
		port.setDebug(false);
		double sonic = 0;
		
		while (true) {
				if(System.in.available() > 0) {
					byte input = (byte) System.in.read();
					if(input == 0x66 || input == 0x62 || input == 0x6c || input == 0x72) {
						port.writeByte((byte) magicNum);
						port.writeByte((byte) move);
					}
					port.writeByte(input);
					port.writeByte((byte) 20);
				}
				switch(state) {
				case MAGICNUMBER:
					byte curByte;
					while (true) {
						if(port.available()) {
							curByte = port.readByte();
							break;
						}
					}
					if (curByte == 0x21) {
						state = State.KEY;
					}
					break;
					
				case KEY:
					sonic = 0;
					byte key;
					while (true) {
						if(port.available()) {
							key = port.readByte();
							break;
						}
					}
					if (key == info) {
						state = State.INFO;
					} else if (key == time) {
						state = State.TIMESTAMP;
					} else if (key == potentiometer) {
						state = State.POTENTIAL;
					} else if (key == echo) {
						state = State.ECHO;
					} else if (key == error) {
						state = State.ERROR;
					} else {
						state = State.BADMESSAGE;
					}
					break;
					
				case INFO:
					byte infoB1;
					byte infoB2;
					while (true) {
						if(port.available()) {
							infoB1 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							infoB2 = port.readByte();
							break;
						}
					}
					int message = (((infoB1&0xFF)<<8) + (infoB2&0xFF));
					byte []chars = new byte[message];
					for(int j = 0; j<message; j++) {
						while (true) {
							if(port.available()) {
								chars[j] = port.readByte();
								break;
							}
						}
					}
					String infoString = new String(chars, StandardCharsets.UTF_8);
					System.out.println("Info: " + infoString);
					state = State.MAGICNUMBER;
					break;
					
				case TIMESTAMP:
					byte timeB1;
					byte timeB2;
					byte timeB3;
					byte timeB4;
					while (true) {
						if(port.available()) {
							timeB1 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							timeB2 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							timeB3 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							timeB4 = port.readByte();
							break;
						}
					}
					long timeStamp = (((timeB1&0xff)<<24) + ((timeB2&0xff)<<16) + ((timeB3&0xFF)<<8) + (timeB4&0xff));
					System.out.println("Timestamp: " + timeStamp);
					state = State.MAGICNUMBER;
					break;
					
				case POTENTIAL:
					byte potB1;
					byte potB2;
					while (true) {
						if(port.available()) {
							potB1 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							potB2 = port.readByte();
							break;
						}
					}
					
					long potReading = ((potB1&0xff)<<8) + (potB2&0xff);
					System.out.println("Potentiometer reading: " + potReading);
					state = State.MAGICNUMBER;
					break;
					
				case ECHO:
					byte echoB1;
					byte echoB2;
					byte echoB3;
					byte echoB4;
					while (true) {
						if(port.available()) {
							echoB1 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							echoB2 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							echoB3 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							echoB4 = port.readByte();
							break;
						}
					}
					int echo = (((echoB1&0xff)<<24) + ((echoB2&0xff)<<16) + ((echoB3&0xff)<<8) + (echoB4&0xff));
					sonic = ((echo*0.0343)/2.0);
					System.out.println("Ultrasonic sensor reading: " + echo);
					System.out.println("Converted reading (cm): " + sonic);
					state = State.MAGICNUMBER;
					break;
					
				case ERROR:
					byte errorB1;
					byte errorB2;
					while (true) {
						if(port.available()) {
							errorB1 = port.readByte();
							break;
						}
					}
					while (true) {
						if(port.available()) {
							errorB2 = port.readByte();
							break;
						}
					}
					int error = ((errorB1&0xff)<<8) + (errorB2&0xff);
					byte []errorChars = new byte[error];
					for(int j = 0; j<error; j++) {
						while (true) {
							if(port.available()) {
								errorChars[j] = port.readByte();
								break;
							}
						}
					}
					String errorString = new String(errorChars, StandardCharsets.UTF_8);
					System.out.println("Error: " + errorString);
					state = State.MAGICNUMBER;
					break;
					
				case BADMESSAGE:
					System.out.println("!----ERROR----!");
					state = State.MAGICNUMBER;
					break;
				}
			}
	}

	public static void main(String[] args) throws SerialPortException, IOException {
		RemoteControl rc = new RemoteControl("COM5"); // Adjust this to be the right port for your machine
		rc.run();
	}
}
