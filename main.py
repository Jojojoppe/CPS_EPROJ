import random                                                                                   
import time                      
import pickle                                                               
import sys
import traceback
from enum import Enum                                                                           
import algorithm.algo as algo                                                                   
import controller.aruco as aruco                                                                
import gopigo                                                                                   
import NetEmuC.python.netemuclient as netemuclient                                              
from controller.space import Direction                                                          

# Base driving speed per wheel, this never changes
base_speed = 140
# Proportional gain                                                                               
kp = 77 
# Hardcoded turn angle                                                                                       
turn_angle = 75                                                                                 
compass = Direction()                                                                           

algoInstance = None            
network = None                                                                 


# The controller for the wheels
def get_control_out(p0):                                                                        
    # P controller                                                                              
    # P_out = P0 + Kp * e                                                                       
    # Per wheel assume that P0 is a constant for driving spesified in this file                 

    global base_speed                                                                           
    error = p0 - 0.5 # Deviation from middle                                                    
                                                                                                
    left  = base_speed + kp * error                                                             
    right = base_speed - kp * error                                                             
    return left, right                                                                          


# Drive forwards
def drive_forwards(target):                                                                     
    left, right = get_control_out(target)                                                       
    time.sleep(0.001)                                                                           
    gopigo.set_left_speed(int(left))                                                            
    gopigo.set_right_speed(int(right))                                                          


# Recieve from network                                                                                        
def rec(data:bytes, rssi:int):                                                                  
    #print("Received a packet")
    global algoInstance                                                                         
    algoInstance.recv(data, rssi)                                                               


# Get next position update from the algorithm                                                                                         
def newPosition(markerID:int):                                                                  
    global network, algoInstance

    x = markerID&0x0f                                                                           
    y = (markerID//16)&0x0f                                                                     
    info = network.maze[(x,y)]                                                                  
    network.position(float(x), float(y))                                                        
    algoInstance.newPos((x,y), info)                                                            
    return info                                                                                 


# Turn around 180 degrees
def around():                                                                                   
    gopigo.set_left_speed(250)                                                                  
    gopigo.set_right_speed(250)                                                                 
    gopigo.left_rot()                                                                           
    time.sleep(1.30)                                                                            
    while True:
        time.sleep(0.2)                                                                                                                                                                                                                           
        marker, t = aruco.get_result()                                                          
        if t > 0.01:                                                                            
            break    
        gopigo.stop()                                                                           
        gopigo.set_left_speed(250)                                                              
        gopigo.set_right_speed(250)                                                             
        gopigo.left_rot()                                                                       

        time.sleep(0.2)                                                                         
    gopigo.stop()
    time.sleep(0.2)


# Turn left or right
def do_turn(d):                                                                                 
    global turn_angle, compass                                                                  

    gopigo.set_left_speed(210)                                                                  
    gopigo.set_right_speed(210)                                                                 
    time.sleep(0.1)                                                                             

    compass.turn_c(d)                                                                           
    if d == "left":                                                                             
        gopigo.turn_left_wait_for_completion(turn_angle)                                        
    elif d == "around":                                                                         
        around()                                                                                

        gopigo.stop()                                                                           
    else:
        try:
            gopigo.turn_right_wait_for_completion(turn_angle)
        except TypeError:
            do_turn(d)                                                                                       
        
    time.sleep(0.1)                                                                             
    gopigo.fwd()                                                                                
    drive_forwards(0.5)                                                                         


# Assume turn is successful
def turn_done():                                                                                

    return True                                                                                 

# States for the state machine
class State(Enum):                                                                              
    DRIVE = 1                                                                                   
    TURN_RIGHT = 2                                                                              
    TURN_LEFT = 3                                                                               
    STOP = 4                                                                                    
    TURN_AROUND = 5                                                                             

state = State.DRIVE                                                                             
state_timer = time.time()                                                                       
prev_marker = -1                                                                                


# Change the state based on the previous state and if we see an aruco marker
def change_state(m_, t):

    global state, prev_marker, state_timer  

    direction = None                                                                        
    if m_ is not None:  
        m = int(m_)                                                                     
    else:  
        m = None 

    new_state = State.STOP 

    if state == State.DRIVE:
                                                                    
        if m is None or m == -1:                                                                
            new_state = State.DRIVE                                                             
        elif m >= 0 and m != prev_marker:                                                                                                  
            newPosition(m)
            new_state = State.STOP                                                              
        else:                                                                                   
            new_state = State.DRIVE

    elif state == State.STOP:

        prev_marker = m  
        # Check if we waited for 1 second                                                                       
        if time.time() - 1 > state_timer:   
            # Get the direction from the algorithm                                                    
            direction = algoInstance.getDirection()

            # Save the current state, since we got new directions
            with open("last_state.pickle", "wb") as f_pickle:
                f_pickle.write(pickle.dumps(algoInstance))

            if direction == algo.LEFT:                                                          
                new_state = State.TURN_LEFT                                                     
            elif direction == algo.RIGHT:                                                       
                new_state = State.TURN_RIGHT                                                    
            elif direction == algo.BACK:                                                        
                new_state = State.TURN_AROUND                                                   
            elif direction == algo.STOP:                                                        
                new_state = State.STOP
            elif direction == algo.STRAIGHT:
                new_state = State.DRIVE
            else:       
                print("Broken direction:", direction)                                                                        
                new_state = State.STOP                                                         
        else:                                                                                   
            new_state = State.STOP                                                              

    elif state == State.TURN_LEFT:

        if turn_done():                                                                         
            new_state = State.DRIVE                                                             
        else:                                                                                   
            new_state = State.TURN_LEFT                                                         

    elif state == State.TURN_RIGHT:

        if turn_done():                                                                         
            new_state = State.DRIVE                                                             
        else:                                                                                   
            new_state = State.TURN_RIGHT                                                        

    elif state == State.TURN_AROUND:

        if turn_done():                                                                         
            new_state = State.DRIVE                                                             
        else:                                                                                   
            new_state = State.TURN_AROUND     

    # We changed state
    if new_state != state:                                                                      
        if state == State.STOP and new_state == State.DRIVE:                                    
            gopigo.fwd()                                                                        
        state_timer = time.time()
    return new_state                                                                            


# This is only called when gopigo stops driving for no reason                               
# The only way to fix it is to stop it and then restart       
def rescue():                                                                                               
    gopigo.stop()                                                                               
    print("Rescue")                                                                             
    time.sleep(1)                                                                               
    gopigo.set_left_speed(130)                                                                  
    gopigo.set_right_speed(130)                                                                 
    gopigo.fwd()                                                                                
    time.sleep(0.2)                                                                             


# Main control function
def main():                                                                                     
    global network, state, prev_marker, algoInstance                                            

    if network is None:
        # Setup network                                                                             
        ip = "localhost"
        with open("server.ip") as f:
            ip = f.read()
        x,y = 1,0                                                                                   
        network = netemuclient.NetEmuClient(rec, ip, 8080)                                 
        network.start()                                                                             
        network.waitForMaze()                                                                       
        network.position(x,y)                                                                       
        network.txpower(0.02)    

    if algoInstance is None:
        # If the program is started with arguments, this will load the last saved state
        if len(sys.argv)>1:
            with open("last_state.pickle", "rb") as f_pickle:
                algoInstance = pickle.loads(f_pickle.read())
                algoInstance.restoreState(network)
                network.position(*algoInstance.position)
        # Start the algorithm without a saved state
        else:
            algoInstance = algo.Algorithm(network, (x,y))                                               

    # Give everything time to warm up
    time.sleep(2)                                                                               
    gopigo.set_left_speed(0)                                                                    
    gopigo.set_right_speed(0)                                                                   
    gopigo.fwd()                                                                                

    save_timer = time.time() 
    # Save the latest encoder reading                                                                   
    save_enc = (0, 0)

    
    while True:

        # Move in the alorithm
        algoInstance.step()

        # Call the latest camera results
        (marker, t) = aruco.get_result()

        # GoPiGo is not very stable, this block is just to make it stable
        if save_timer + 2 < time.time():
            try:
                new_enc = (gopigo.enc_read(0), gopigo.enc_read(1))
                print(save_enc, new_enc)
            except TypeError:
                print("GoPiGo breaks when you enc read sometimes just restart the main, the state should be fine")
                gopigo.stop()
                time.sleep(0.2)
                gopigo.stop()
                main()

            # We have been stopping while we should be driving
            if new_enc == save_enc and state == State.DRIVE:
                rescue()
            save_enc = new_enc

        # Update the state
        state = change_state(marker, t)


        if state == State.DRIVE:
            drive_forwards(t)

        elif state == State.STOP:
            gopigo.stop()

        elif state == State.TURN_LEFT:
            do_turn("left")

        elif state == State.TURN_RIGHT:
            do_turn("right")
        elif state == State.TURN_AROUND:
            do_turn("around")
            time.sleep(0.001)
        else:
            raise ValueError


if __name__ == "__main__":

    # No matter what, just rerun the main
    while True:
        try:
            main()
            gopigo.stop()
        except KeyboardInterrupt:
            gopigo.stop()
            break 
        except ValueError as e:
            print("Value error!, probably within the algorithm ", str(e))
            traceback.print_exc()
        except Exception as e:
            traceback.print_exc()
            print("RERUN MAIN WITH BROAD EXCEPTION", aruco.get_result())
        