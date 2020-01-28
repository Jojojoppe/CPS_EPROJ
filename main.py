import random                                                                                   
import time                      
import pickle                                                               
import sys
from enum import Enum                                                                           

import algorithm.algo as algo                                                                   
import controller.aruco as aruco                                                                
import gopigo                                                                                   
import NetEmuC.python.netemuclient as netemuclient                                              
from controller.space import Direction                                                          

base_speed = 140                                                                                
kp = 100                                                                                        
turn_angle = 75                                                                                 
compass = Direction()                                                                           

algoInstance = None            
network = None                                                                 


def get_control_out(p0):                                                                        
    # P controller                                                                              
    # P_out = P0 + Kp * e                                                                       
    # Per wheel assume that P0 is a constant for driving spesified in this file                 

    global base_speed                                                                           
    error = p0 - 0.5 # Deviation from middle                                                    
                                                                                                
    left  = base_speed + kp * error                                                             
    right = base_speed - kp * error                                                             
    return left, right                                                                          


def drive_forwards(target):                                                                     
    left, right = get_control_out(target)                                                       
    time.sleep(0.001)                                                                           
    gopigo.set_left_speed(int(left))                                                            
    gopigo.set_right_speed(int(right))                                                          


"""Data received from network                                                                   
"""                                                                                             
def rec(data:bytes, rssi:int):                                                                  
    global algoInstance                                                                         
    algoInstance.recv(data, rssi)                                                               


"""Get information of net position and update the network emulator                              
Returns tupe with:                                                                              
    north, east, south, west: True if wall, False if open                                       
    final: True if exit of maze                                                                 
"""                                                                                             
def newPosition(markerID:int):                                                                  
    global network, algoInstance

    x = markerID&0x0f                                                                           
    y = (markerID//16)&0x0f                                                                     
    info = network.maze[(x,y)]                                                                  
    network.position(float(x), float(y))                                                        
    algoInstance.newPos((x,y), info)                                                            



    return info                                                                                 

def get_turn(m):                                                                                
    # Rescue                                                                                    

    if m == None:                                                                               
        print("None m")                                                                         
        return "straight"                                                                       

    # if int(m) == 4:                                                                           
    #     return "stop"                                                                         


    if int(m) == 300:                                                                           
        return "straight"                                                                       
    # m_info = newPosition(m)                                                                   
    # # (north, east, south, west, final_pos)                                                   
    # # TODO Add algorithm decision making here                                                 

    # # For now find first open wall clockwise from north                                       
    # dirs = ["straight", "right", "around", "left"]                                            
    # for i in range(4):                                                                        
    #     if not m_info[i]:                                                                     
    #         return dirs[i]                                                                    

    # return "straight"                                                                         
    return "around"                                                                             

def around():                                                                                   
    gopigo.set_left_speed(250)                                                                  
    gopigo.set_right_speed(250)                                                                 
    gopigo.left_rot()                                                                           
    time.sleep(1.30)                                                                            
    while True:                                                                                 
        gopigo.stop()                                                                           
        time.sleep(0.2)                                                                         
        marker, t = aruco.get_result()                                                          
        if t > 0.01:                                                                            
            break                                                                               
        gopigo.set_left_speed(250)                                                              
        gopigo.set_right_speed(250)                                                             
        gopigo.left_rot()                                                                       

        time.sleep(0.2)                                                                         


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
            print("Second TypeError")
            do_turn(d)                                                                                       
        
    time.sleep(0.1)                                                                             
    gopigo.fwd()                                                                                
    drive_forwards(0.5)                                                                         

def turn_done():                                                                                

    return True                                                                                 



class State(Enum):                                                                              
    DRIVE = 1                                                                                   
    TURN_RIGHT = 2                                                                              
    TURN_LEFT = 3                                                                               
    STOP = 4                                                                                    
    TURN_AROUND = 5                                                                             

state = State.DRIVE                                                                             
state_timer = time.time()                                                                       
prev_marker = -1                                                                                

def change_state(m_, t):
    direction = None                                                                        
    if m_ is not None:  
        m = int(m_)
        print("Not none", m)                                                                        
                                                                             
    else:  
        print("None")                                                                                     
        m = None                                                                                
    global state, prev_marker, state_timer                                                      
    new_state = State.STOP 
    print("old:", state)                                                                     

    if state == State.DRIVE:
        print("1")
                                                                    
        if m is None or m == -1:                                                                
            new_state = State.DRIVE                                                             
        elif m >= 0 and m != prev_marker:                                                       
            # Marker found
            # New position is sent to the maze                                                  
            newPosition(m)
            new_state = State.STOP                                                              
        else:                                                                                   
            new_state = State.DRIVE                                                             
    elif state == State.STOP:
        print("2")                                                                   
        prev_marker = m                                                                         
        if time.time() - 1 > state_timer:                                                       
            #direction = get_turn(m)                                                            

            # Get new direction
            print("before")
            direction = algoInstance.getDirection()
            print("after")                                             

            print("Pickle state")
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
        print("3")                                                              
        if turn_done():                                                                         
            new_state = State.DRIVE                                                             
        else:                                                                                   
            new_state = State.TURN_LEFT                                                         

    elif state == State.TURN_RIGHT:
        print("4")                                                             
        if turn_done():                                                                         
            new_state = State.DRIVE                                                             
        else:                                                                                   
            new_state = State.TURN_RIGHT                                                        

    elif state == State.TURN_AROUND:
        print("5")                                                            
        if turn_done():                                                                         
            new_state = State.DRIVE                                                             
        else:                                                                                   
            new_state = State.TURN_AROUND     
    print("Before if")

    if new_state != state:                                                                      
        if state == State.STOP and new_state == State.DRIVE:                                    
            gopigo.fwd()                                                                        
        state_timer = time.time()
    print("new:", new_state)
    return new_state                                                                            


def rescue():                                                                                   
    # This is only called when gopigo stops driving for no reason                               
    # The only way to fix it is to stop it and then restart                                     
    gopigo.stop()                                                                               
    print("Rescue")                                                                             
    time.sleep(1)                                                                               
    gopigo.set_left_speed(130)                                                                  
    gopigo.set_right_speed(130)                                                                 
    gopigo.fwd()                                                                                
    time.sleep(0.2)                                                                             

def main():                                                                                     
    global network, state, prev_marker, algoInstance                                            

    if network is None:
        # Setup network                                                                             
        # Read ip address
        ip = "localhost"
        with open("server.ip") as f:
            ip = f.read()
        # TODO STARTING POSITION                                                                    
        x,y = 1,0                                                                                   
        network = netemuclient.NetEmuClient(rec, ip, 8080)                                 
        network.start()                                                                             
        network.waitForMaze()                                                                       
        network.position(x,y)                                                                       
        network.txpower(0.02)    

    if algoInstance is None:
        if len(sys.argv)>1:
            with open("last_state.pickle", "rb") as f_pickle:
                algoInstance = pickle.loads(f_pickle.read())
                algoInstance.restoreState(network)
                network.position(*algoInstance.position)
        else:
            # Startup algorithm                                                                         
            algoInstance = algo.Algorithm(network, (x,y))                                               
            #newPosition(x+16*y)                                                                         

    time.sleep(2)                                                                               
    gopigo.set_left_speed(0)                                                                    
    gopigo.set_right_speed(0)                                                                   
    gopigo.fwd()                                                                                

    save_timer = time.time()                                                                    
    save_enc = (0, 0)

    # print("Before while")
    
    while True:
        # print(".", end="")
        # print("Before step")

        algoInstance.step()

        # print("Stepped")

        (marker, t) = aruco.get_result()

        # print("markered", marker)

        # GoPiGo is not very stable, this block is just to make it stable
        if save_timer + 2 < time.time():
            try:
                new_enc = (gopigo.enc_read(0), gopigo.enc_read(1))
            except TypeError:
                print("GoPiGo breaks when you enc read sometimes just restart the main, the state should be fine")
                gopigo.stop()
                time.sleep(0.2)
                gopigo.stop()
                main()

            if new_enc == save_enc and state == State.DRIVE:
                print("Before rescue")
                rescue()

        # print("Before state")
        state = change_state(marker, t)

        print("stated")
        

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
    while True:
        try:
            main()
            gopigo.stop()
        except KeyboardInterrupt:
            gopigo.stop()
            break 
        except Exception as e:
            print(str(e))
            print("LOLOLOLOLOLOL", aruco.get_result())
        