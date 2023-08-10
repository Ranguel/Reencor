import json,pygame
#command list
comm_list=[['6','2','3'],(('j','Jab Shoryuken!'),('s','Strong Shoryuken!'),('c','Fierce Shoryuken!'))],[['2','3','6'],(('j','Jab Hadouken!'),('s','Strong Hadouken!'),('c','Fierce Hadouken!'))]

# down > down+right > right > A = Jab Shoryuken!
#                           > S = Strong Shoryuken!
#                           > D = Fierce Shoryuken!

#command match index
comm_indx=[0 for i in range(len(comm_list))]
#current key pressed
press=['5']
#old inputs, used to determine if a key was pressed
oldinputs=[]

pygame.init()
screen=pygame.display.set_mode((720,450))
active,frame=True,pygame.time.Clock()


#keyboard key indexes, may vary between keyboards
P1_KB=[82,81,79,80,8,26,20,7,22,4,114,102,116]

#function to get directional and attack input

def Keyboard_press(keys):
                         #(Numpad notation)
     return ([[('5','6','4'),('8','9','7'),('2','3','1')][keyboard[keys[0]]*1+keyboard[keys[1]]*-1][keyboard[keys[2]]*1+keyboard[keys[3]]*-1]]
     ,keyboard[keys[4]],keyboard[keys[5]],keyboard[keys[6]],keyboard[keys[7]],keyboard[keys[8]],keyboard[keys[9]],keyboard[keys[10]])

#function that finds the matches between the input keys and the command list
#refreshes the command list index to determine if a command was performed
def comm_match(inlist):
    for ind,comm in enumerate(comm_list):
        if comm_indx[ind]>=len(comm[0]):
            for special in comm[1]:
                if special[0] in inlist:
                    print('special move: ',special[1])
                    comm_indx[ind]=0
                    return 
        elif(comm[0][comm_indx[ind]] in inlist):comm_indx[ind]+=1
timeout=0

while active:
     frame.tick(60)
     #reduce the timeout, when the time is up the command list index is reset
     if timeout:timeout-=1
     else:comm_indx=[0 for i in range(len(comm_list))]

     for event in pygame.event.get():
          if event.type==pygame.QUIT:
               active=False 
               pygame.quit()
     #get the state of the keys  
     keyboard=tuple(pygame.key.get_pressed())
     inputs=Keyboard_press(P1_KB)
     if inputs!=oldinputs:
          #add the key to the key list if it was pressed and start the timeout
          press=inputs[0]+[(0,'r','f','h','c','s','j','s','g','u')[ind]for ind in range(1,len(inputs))if inputs[ind]and inputs[ind]!=oldinputs[ind]]
          timeout=12
          comm_match(press)
     oldinputs=inputs
     pygame.display.update()

