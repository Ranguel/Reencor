import sys,pygame,os,json,math,dict_path,random,numpy

color=[(255,0,255,80),(0,0,255,80),(255,0,0,80),(0,255,0,80),(255,255,0,80)]
def nomatch(*args):0

def palette_swap(image, palette):
    new =pygame.PixelArray(image)
    for color in palette:
        new.replace(tuple(color[0]),tuple(color[1]),.01)
    del new
    return image

class Rect(pygame.sprite.Sprite):
    def __init__(self,size,pos):self.rect,self.pos=pygame.Surface((size)).get_rect(),(pos)
    def display(self,color=(0,0,0)):pygame.draw.rect(screen,color,(self.rect[0]-scroll[0],self.rect[1]-scroll[1],self.rect[2],self.rect[3]),1)
    def update(self,pos,face):self.rect.bottomleft=pos[0]+self.pos[0]*face-self.rect.width*(face<0),pos[1]-self.pos[1]


class Visual(pygame.sprite.Sprite):
    def __init__(self,file,pos=(280,200),face=1,palette=0,inicial_state='g/g'):
        pygame.sprite.Sprite.__init__(self)
        self.dict,self.pos,self.face,self.palette=dict_path.DictPath(json.load(open(file))),[pos[0],pos[1]],face,palette
        self.rect=pygame.Surface((2,2)).get_rect(center=self.pos)
        self.frame=self.soff=[0,0]
        self.stop=0
        self.path=[pos]
        self.state_key=inicial_state
        self.sprite=list(spritedict.values())[0]
        getset(self,self.state_key)
    def display(self):
        screen.blit(self.sprite,(-scroll[0]+self.rect[0]+self.dict['offset'][0]+self.soff[0]*self.face,-scroll[1]+self.rect[1]+self.dict['offset'][1]+self.soff[1]))
        pygame.draw.line(screen,(0,0,0),(self.rect.centerx-8,self.rect.centery),(self.rect.centerx+8,self.rect.centery),1)
        pygame.draw.line(screen,(0,0,0),(self.rect.centerx,self.rect.centery-8),(self.rect.centerx,self.rect.centery+8),1)     
    def update(self):# update
        if not self.stop:self.frame[1]-=1           
        if self.frame[0]<0:self.kill()
        try:
            if self.frame[1]<=0:nextframe(self,self.dict.get(self.state_key+'data')[-self.frame[0]])
        except:self.frame=[0,1]
    def fisics(self):0
        
class Stage(pygame.sprite.Sprite):
    def __init__(self,file,pos=(280,200),face=1,palette=0,inicial_state='gnd/n/5'):
        pygame.sprite.Sprite.__init__(self)
        self.dict,self.pos,self.face,self.palette=dict_path.DictPath(json.load(open(file))),[pos[0],pos[1]],face,palette
        self.rect=pygame.Surface((2,2)).get_rect(bottomleft=(0,0))
        self.frame,self.shake,self.speed,self.accel,self.osc,self.block=[[0,0]for i in range(6)]
        self.scale=self.dict['scale']
        self.state_key=inicial_state
        self.path=[pos]
        self.sprite=list(spritedict.values())[0]
        self.layer={}
        loaddicts(self)
    def loadsprite(self):
        for layer in self.dict['layers']:
            self.layer[layer]={} 
            self.layer[layer]['pos']=self.dict['layers'][layer]['data']['pos'][0]*self.scale[0],self.dict['layers'][layer]['data']['pos'][1]*self.scale[1]
            self.layer[layer]['s']=pygame.transform.flip(spritedict[self.dict['name']+str(self.palette)+self.dict['layers'][layer]['data']['s']],self.face+abs(self.face),0)
    def display(self):
        for layer in self.layer:
            screen.blit(self.layer[layer]['s'],(-round(scroll[0]/self.dict['layers'][layer]['data']['dtn'])+self.layer[layer]['pos'][0]+self.dict['offset'][0]*self.face+(self.osc[1]/(1+self.osc[0]*.8))*math.sin(self.osc[0])*self.face,-scroll[1]+self.layer[layer]['pos'][1]+self.dict['offset'][1]))
    def update(self):0
    def fisics(self):
        if scroll[0]<self.dict['limit'][0][0]*self.scale[0]:scroll[0]=self.dict['limit'][0][0]*self.scale[0]
        if scroll[0]>self.dict['limit'][0][1]*self.scale[1]:scroll[0]=self.dict['limit'][0][1]*self.scale[1]
        if scroll[1]>self.dict['limit'][1][0]*self.scale[0]:scroll[1]=self.dict['limit'][1][0]*self.scale[0]
        if scroll[1]<self.dict['limit'][1][1]*self.scale[1]:scroll[1]=self.dict['limit'][1][1]*self.scale[1]
        

class Object(pygame.sprite.Sprite):
    def __init__(self,teamlist,enemylist,file,pos=(280,200),face=1,palette=0,inicial_state=['gnd','5'],keys=[]):
        pygame.sprite.Sprite.__init__(self)
        self.telist,self.enlist,self.dict,self.pos,self.face,self.palette,self.kbi=teamlist,enemylist,dict_path.DictPath(json.load(open(file))),[pos[0],pos[1]],face,palette,keys
        self.rect=pygame.Surface((2,2)).get_rect(bottomleft=(0,0))
        self.scale=self.dict['scale']
        self.frame,self.shake,self.speed,self.accel,self.osc,self.soff,self.block=[[0,0]for i in range(7)]
        self.path=[pos]
        self.stun=self.stop=0
        self.cancel=self.intime=self.fn=self.smear=self.aoh=0
        self.hurtbox,self.hitbox,self.takebox,self.grabbox,self.airbox,self.pushbox=[{'rects':[]}for i in range(6)]
        self.inter=1
        self.health=self.dict['health'][0]
        self.gauge=self.dict['gauge'][0]
        self.stamina=self.dict['stun']
        self.newpress=[5]
        self.oldpress=[5,0,0,0,0,0,0,0,0]
        self.buffer=[5]
        self.state_key='anm/none'
        self.fet='gnd'
        self.commdex=[0]*len(self.dict["commands"])
        self.hit=[]
        self.hurt=[]
        self.combo=0
        loaddicts(self)
        getset(self,inicial_state)
        try:self.update()
        except:0
        
        
    def Keyboard_mode(self):Control(self,[(keyboard[self.kbi[2]]*1+keyboard[self.kbi[3]]*-1,keyboard[self.kbi[0]]*1+keyboard[self.kbi[1]]*-1),keyboard [self.kbi[4]],keyboard[self.kbi[5]],keyboard[self.kbi[6]],keyboard[self.kbi[7]],keyboard[self.kbi[8]],keyboard[self.kbi[9]],keyboard[self.kbi[10]]])
    def display(self):
        try:
            screen.blit(self.sprite,(-scroll[0]+self.rect[0]+self.dict['offset'][0]*self.scale[0]+self.soff[0]*self.scale[0]*self.face+(self.osc[1]/(1+self.osc[0]*.8))*math.sin(self.osc[0])*3.6*self.face,-scroll[1]+self.rect[1]+self.dict['offset'][1]*self.scale[1]+self.soff[1]*self.scale[1]))
            for i in self.hurtbox['rects']:pygame.draw.rect(screen,color[1],(-scroll[0]+self.rect.centerx+i[2]*self.face-i[0]*(self.face<0),-scroll[1]+self.rect.centery-i[1]-i[3],i[0],i[1]),3)
            for i in self.hitbox['rects']:pygame.draw.rect(screen,color[2],(-scroll[0]+self.rect.centerx+i[2]*self.face-i[0]*(self.face<0),-scroll[1]+self.rect.centery-i[1]-i[3],i[0],i[1]),3)
            for i in self.pushbox['rects']:pygame.draw.rect(screen,color[0],(-scroll[0]+self.rect.centerx+i[2]*self.face-i[0]*(self.face<0),-scroll[1]+self.rect.centery-i[1]-i[3],i[0],i[1]),3)
            pygame.draw.line(screen,(0,0,0),(-scroll[0]+self.rect.centerx-16,-scroll[1]+self.rect.centery),(-scroll[0]+self.rect.centerx+16,-scroll[1]+self.rect.centery),3)
            pygame.draw.line(screen,(0,0,0),(-scroll[0]+self.rect.centerx,-scroll[1]+self.rect.centery-16),(-scroll[0]+self.rect.centerx,-scroll[1]+self.rect.centery+16),3)
        except:0  

    def update(self):# update
        if len(self.kbi):self.Keyboard_mode()
        hurt_by(self)
        if self.stop:self.stop,self.osc[0],self.osc=self.stop-1,self.osc[0]+1 if self.osc[1]else self.osc[0],[0,0]if not self.stop-1 else self.osc
        self.frame[1]-=1*(not self.stop or self.stop and self.smear)
        if not self.stop:
            if self.stun:self.stun-=1
            if self.cancel==0 and self.fet=='gnd' and self.face!=RoundSign(self.enlist[0].pos[0]-self.pos[0])and abs(self.enlist[0].pos[0]-self.pos[0])>32:self.face,self.buffer,self.inter=RoundSign(self.enlist[0].pos[0]-self.pos[0]),self.buffer+['turn'],1
            self.speed=[self.speed[0]+self.accel[0]*self.face,self.speed[1]-self.accel[1]]
            self.pos=[self.pos[0]+self.speed[0],self.pos[1]+self.speed[1]]            
            if self.pos[1]<680:self.fn,self.speed[1]=self.fn+1,self.speed[1]+self.dict['gravity']
            if (self.frame==[0,0]or (self.inter and type(self.cancel)==int)):getset(self,[self.fet]+self.buffer)
        if self.frame[1]<=0:
            try:nextframe(self,self.dict.get(self.state_key)[2][-self.frame[0]])
            except:self.frame,self.inter=[0,1],1
        for hurt in self.enlist:hitbox_hurtbox_return(self,hurt)
        self.fisics()
    def fisics(self):
        if self.pos[1]<680:self.fet='abn'
        else:
            if self.fet!='gnd':
                self.frame,self.fn=[0,0],0
                getset(self,['ldg',str(self.dict.get(self.state_key)[0])])
            self.fet,self.pos[1],self.speed[1]='gnd',680,self.speed[1]*int(self.stop!=0) 
        if self.pos[0]-scroll[0]>1280-self.dict['limit']:self.pos[0]=scroll[0]+1280-self.dict['limit']
        if self.pos[0]-scroll[0]<self.dict['limit']:self.pos[0]=scroll[0]+self.dict['limit']
        self.rect.centerx,self.rect.bottom=round(self.pos[0]),round(self.pos[1]) 
def Control(self,inputs):
    inputs[0]=[['plane','up','down'][inputs[0][1]],['mid','front','back'][inputs[0][0]*self.face]]
    if self.intime:self.intime-=1
    else:self.commdex,self.buffer=[0]*len(self.dict["commands"]),[]
    self.newpress=inputs[0]+[('0','r','f','h','c','s','j',"Start")[ind]for ind in range(1,len(inputs))if inputs[ind]and inputs[ind]!=self.oldpress[ind]]
    if inputs!=self.oldpress:
        self.intime,self.inter=12,1      
        for ind,comm in enumerate(self.dict["commands"]):
            if self.commdex[ind]>=len(comm[0]):
                for special in comm[1]:
                    if len(set(special[0].split(",")).intersection(self.newpress))>=len(special[0].split(",")):
                        self.newpress,self.commdex[ind]=self.newpress+[special[1]],0
                        break 
            elif len(set(comm[0][self.commdex[ind]].split(",")).intersection(self.newpress))>=len(comm[0][self.commdex[ind]].split(",")):self.commdex[ind]+=1
    self.buffer,self.oldpress=inputs[0]+list(set(self.newpress[2:]+self.buffer[2:])),inputs

def getset(self,buffer=False,force=0):
    for name in self.dict.get('anm'):
        if len(set(name.split(",")).intersection(buffer))>=len(name.split(",")):
            post,prep,path=self.dict.get(self.state_key),self.dict.get('anm/'+name),'anm/'+name
            if ((self.cancel in prep[1]and(self.cancel or post[0]!=prep[0]))or self.frame==[0,0]or force):
                self.state_key,self.frame,self.accel,self.inter,self.buffer,self.hurt=path,[len(prep[2]),0],[0,0],0,[self.buffer[0]]+[v for v in self.buffer[1:]if v not in path.split(",")],[]
                frame_hurtbox(self),frame_hitbox(self),frame_grabbox(self),frame_takebox(self),nextframe(self,self.dict.get(self.state_key)[2][-self.frame[0]])
                return

def nextframe(self,state):
    self.cancel,self.soff,self.smear=None,[0,0],0
    for value in state:valuedict[value](self,state[value])
    self.frame[0]-=1

def frame_duration(self,d=0,*args):self.frame[1]=d
def frame_sprite(self,s=0,*args):self.sprite=pygame.transform.flip(spritedict[self.dict['name']+str(self.palette)+str(s)],self.face+abs(self.face),0)
def frame_hurtbox(self,u=[],*args):self.hurtbox['rects']=u
def frame_offset(self,f=(0,0),*args):self.pos=[self.pos[0]+f[0]*self.face,self.pos[1]-f[1]]
def frame_velocity(self,v=(0,0),*args):self.speed=[v[0]*self.face,-v[1]]
def frame_acceleration(self,l,*args):self.accel=l[0],l[1]
def frame_hitbox(self,h={'rects':[]},*args):self.hitbox=dict(h)if h.get('rst',False) or h=={} else self.hitbox|h
def frame_cancel(self,c=0,*args):self.cancel=c
def frame_transition(self,*args):0
def frame_object(self,o,*args):self.telist+=[Object(self.telist,self.enlist,self.dict['objects'][o[0]],(self.pos[0]+o[1][0]*self.face,self.pos[1]-o[1][1]),self.face*o[2],o[3],o[4])]
def frame_grabbox(self,g={'rects':[]},*args):self.grabbox=dict(g)
def frame_facing(self,a=1,*args):self.face*=a
def frame_mirror(self,m=(0,0),*args):self.sprite=pygame.transform.flip(self.sprite,m[1],m[2])
def frame_cancelable(self,b,*args):getset(self,b+self.newpress,1)
def frame_pushbox(self,p=[],*args):self.pushbox['rects']=p
def frame_takebox(self,tk={'rects':[]},*args):self.takebox=dict(tk)
def frame_smear(self,sm,*args):self.smear=1
def frame_repeat(self,re,*args):
    self.frame=[self.frame[0]+re,0]
    nextframe(self,self.dict.get(self.state_key)[2][-self.frame[0]])
def frame_spriteoff(self,so,*args):self.soff=so
def frame_crouch(*args):0
def frame_multiplier(*args):0
def frame_sound(self,snd):
    try:
        sound=numpy.random.choice(snd[0],1,p=snd[1])[0]
        sounddict[self.dict['name']+sound].play(0)
    except:0

def attack_position(*args):0
def attack_reset(hit,rst,hurt):hit.hitbox['rst']-=1
def attack_damage(hit,dmg,hurt):hurt.health-={'parry':0,'block':hit.hitbox['dmg'][1],'hurt':hit.hitbox['dmg'][0]}[hurt.buffer[0]] #damage
def attack_gain(hit,gan,hurt):
    hit.gauge+={'parry':0,'block':hit.hitbox['gan'][1],'hurt':hit.hitbox['gan'][0]}[hurt.buffer[0]] #gain
    hurt.gauge+={'parry':4,'block':2,'hurt':2}[hurt.buffer[0]] #gain
def attack_stamina(hit,sma,hurt):hurt.stamina+={'parry':0,'block':hit.hitbox['sma'][1],'hurt':hit.hitbox['sma'][0]}[hurt.buffer[0]] #stun
def attack_hitstun(hit,stn,hurt):hurt.stun={'parry':0,'block':hit.hitbox['stn'][1],'hurt':hit.hitbox['stn'][0]}[hurt.buffer[0]] #hitstun
def attack_hitstop(hit,stp,hurt):
    hit.osc+=[0,{'parry':16,'block':0,'hurt':0}[hurt.buffer[0]]]
    hurt.stop+={'parry':16,'block':hit.hitbox['stp'],'hurt':hit.hitbox['stp']}[hurt.buffer[0]] #hitstop
    hurt.osc+=[0,{'parry':0,'block':hit.hitbox['stp'],'hurt':hit.hitbox['stp']}[hurt.buffer[0]]]
    hit.stop+={'parry':16+{'s':0,'h':4,'m':3,'l':2,'hard':1}[hit.hitbox['typ'][0]],'block':hit.hitbox['stp'],'hurt':hit.hitbox['stp']}[hurt.buffer[0]] #hitstop
def attack_forcestate(hit,fst,hurt):0#!!!
def attack_type(hit,typ,hurt):getset(hurt,[hurt.fet,'hurt']+list(typ),1)
def attack_specific(hit,spf,hurt):0
def attack_knockback(hit,knk,hurt):hurt.speed={'parry':[0,0],'block':[hit.hitbox['knk'][0]*hit.face,hit.hitbox['knk'][1]],'hurt':[hit.hitbox['knk'][0]*hit.face,-hit.hitbox['knk'][1]]}[hurt.buffer[0]]#knockback
def super_stop(cst,*args):
    for o in totallist+P2list+P1list:o.stop=50
def path_camera(pth,*args):campath=pth
def shake_camera(shk,*args):shake=shk
def kill_object(self,*args):self.telist.remove(self)

def hurt_by(self):
    for hit in self.hurt:
        hit.combo,self.buffer=hit.combo*bool(self.stun)+1,['hurt']
        resp=dict(hit.hitbox)
        for value in resp:valuedict[value](hit,resp[value],self)
        self.hurt=[]
        self.frame=[0,0]

valuedict={
            'd':frame_duration,# duration in frames #dict
            's':frame_sprite,# sprite image #dict
            'a':frame_facing,# facing #dict
            'm':frame_mirror,# sprite mirror #function
            'smear':frame_smear,# sprite smear skip on hit #dict
            'so':frame_spriteoff,# current sprite offset #dict
            'f':frame_offset,# offset object pos in first frame #dict
            'v':frame_velocity,# velocity #dict
            'l':frame_acceleration,# acceleration #dict
            'hurtbox':frame_hurtbox,# hurtbox data #dict
            'hitbox':frame_hitbox,# hitbox data #dict
            'grabbox':frame_grabbox,# grabbox data #dict
            'pushbox':frame_pushbox,# create pushbox #dict
            'takebox':frame_takebox,# create takebox #dict
            'b':frame_cancelable,# cancel to next move #function
            'trn':frame_transition,# find transition for given move/anm #dict
            'cancel':frame_cancel,# cancelable #dict
            'crh':frame_crouch,# state crouch #dict
            'mult':frame_multiplier,# damage, gain, stun, hitstun, stop multiplier #dict
            'object':frame_object,# object generation #function
            're':frame_repeat,# go back n frames #function
            


            'rects':attack_position,# hitbox size
            'rst':attack_reset,# reset hitbox hit state
            'dmg':attack_damage,# damage
            'gan':attack_gain,# bar gain
            'sma':attack_stamina,# stun bar or stamina
            'stn':attack_hitstun,# hitstun
            'stp':attack_hitstop,# hitstop
            'fst':attack_forcestate,# force state on hurted
            'typ':attack_type,# hit type force, style 
            'spf':attack_specific,# specific hitstun animation
            'knk':attack_knockback,# knockback on object

            'cst':super_stop,# stop in every object
            'pth':path_camera,# camera path and zoom
            'shk':shake_camera,# camera shake horizontal, vertical
            'snd':frame_sound,# current sprite offset #function
            'kill':kill_object,# destroy object
        }

def Collirect(r1x, r1y, r1w, r1h, r2x, r2y, r2w, r2h):
    return r1x + r1w >= r2x and r1x <= r2x + r2w and r1y + r1h >= r2y and r1y <= r2y + r2h

def hitbox_hurtbox_return(hit,hurt):
    for i in hit.hitbox.get('rects',[]):
        for u in hurt.hurtbox.get('rects',[]):
            if Collirect(hit.rect.centerx+i[2]*hit.face-i[0]*(hit.face<0),hit.rect.centery-i[1]-i[3],i[0],i[1],hurt.rect.centerx+u[2]*hurt.face-u[0]*(hurt.face<0),hurt.rect.centery-u[1]-u[3],u[0],u[1]) and hit.hitbox['rst'] and (hit.stop==0 or hurt.stop==0):
                hurt.hurt.append(hit)
                return
            
def pushbox_pushbox_collide(p1,p2):
    if Collirect(p1.rect.centerx+p1.pushbox['rects'][0][2]*p1.face-p1.pushbox['rects'][0][0]*(p1.face<0),p1.rect.centery-p1.pushbox['rects'][0][1]-p1.pushbox['rects'][0][3],p1.pushbox['rects'][0][0],p1.pushbox['rects'][0][1],
            p2.rect.centerx+p2.pushbox['rects'][0][2]*p2.face-p2.pushbox['rects'][0][0]*(p2.face<0),p2.rect.centery-p2.pushbox['rects'][0][1]-p2.pushbox['rects'][0][3],p2.pushbox['rects'][0][0],p2.pushbox['rects'][0][1]):
        if p1.rect.centerx+p1.pushbox['rects'][0][2]*p1.face-p1.pushbox['rects'][0][0]*(p1.face<0)+p1.pushbox['rects'][0][0]> p2.rect.centerx+p2.pushbox['rects'][0][2]*p2.face-p2.pushbox['rects'][0][0]*(p2.face<0)and p1.pos[0]<p2.pos[0]:
            d=round(abs((p1.rect.centerx+p1.pushbox['rects'][0][2]*p1.face-p1.pushbox['rects'][0][0]*(p1.face<0)+p1.pushbox['rects'][0][0])-(p2.rect.centerx+p2.pushbox['rects'][0][2]*p2.face-p2.pushbox['rects'][0][0]*(p2.face<0)))/2,1)
            p1.pos[0],p2.pos[0]=p1.pos[0]-d,p2.pos[0]+d
        elif p2.rect.centerx+p2.pushbox['rects'][0][2]*p2.face-p2.pushbox['rects'][0][0]*(p2.face<0)+p2.pushbox['rects'][0][0]>p1.rect.centerx+p1.pushbox['rects'][0][2]*p1.face-p1.pushbox['rects'][0][0]*(p1.face<0)and p2.pos[0]<p1.pos[0]:
            d=round(abs((p2.rect.centerx+p2.pushbox['rects'][0][2]*p2.face-p2.pushbox['rects'][0][0]*(p2.face<0)+p2.pushbox['rects'][0][0])-(p1.rect.centerx+p1.pushbox['rects'][0][2]*p1.face-p1.pushbox['rects'][0][0]*(p1.face<0)))/2,1)
            p2.pos[0],p1.pos[0]=p2.pos[0]-d,p1.pos[0]+d
        else:p2.pos[0],p1.pos[0]=p2.pos[0]-p2.face,p1.pos[0]-p1.face

P1_KB=[82,81,79,80,8,26,20,7,22,4,114,102,116]
P2_KB=[15,55,56,54,97,96,95,94,93,92,257,258,259]
P1_CB=[0,1,4,3,2,5,1,0,0]
P2_CB=[0,1,4,1,2,5,3,0,0]
#P2_KB=[82,81,80,79,8,26,20,7,22,4,114,102,116]

def RoundSign(n):return 1 if n>0 else -1 if n<0 else 0
def reescale(values,escale):return [round(i*escale) for i in values]
def loaddicts(self):
    spritedirect=os.listdir(self.dict['sprites'])
    if spritedict.get(self.dict['name']+str(self.palette)+spritedirect[0].split('.')[0])!=None:return
    for sprite in spritedirect:spritedict[self.dict['name']+str(self.palette)+sprite.split('.')[0]]=pygame.transform.scale_by(palette_swap(pygame.image.load(self.dict['sprites']+'/'+str(sprite)),self.dict['palette'][self.palette]),self.dict['scale'])
    for sound in os.listdir(self.dict['sounds']):sounddict[self.dict['name']+sound.split('.')[0]]=pygame.mixer.Sound(self.dict['sounds']+'/'+str(sound))
def show_text( msg, color, x=20, y=20):screen.blit(pygame.font.SysFont("Arial", 36).render( msg, True, color), ( x, y ) )
class Game(object):
    def __init__(self):
        pygame.mixer.pre_init(44100,-16,1,1024)
        pygame.init()
        self.dict={'name':'stn','scale':(1,1),'sprites':'game/sprites','sounds':'game/sounds','objects':(),'palette':([],[])}
        self.palette=0
        global screen,main,scroll,shake,zoom,objectdict,spritedict,sounddict,totallist,P1list,P2list,Input_classes,controller
        
        self.active,self.frame=True,pygame.time.Clock()
        
        objectdict={}
        spritedict={}
        sounddict={}

        loaddicts(self)
        totallist=[]
        P1list=[]
        P2list=[]
        totallist.append(Stage("stages/castle/castle.json"))
        P1list.append(Object(P1list,P2list,"characters/Ryu/Ryu.json",(200,700),1,0,'gnd/5',P1_KB))
        P2list.append(Object(P2list,P1list,"characters/Ryu/Ryu.json",(1300,700),-1,1,'gnd/5',P2_KB))
        totallist[0].loadsprite()
       
        main,screen=pygame.display.set_mode((720,450)),pygame.surface.Surface((1280,800))
        scroll=shake=zoom=[0,0]
        self.frame.tick(60)
        try:controller = pygame.joystick.Joystick(0)
        except:0
        self.skip=0
        self.Gameplay()

    def inpu(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.active=False 
                pygame.quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    if main.get_flags() & pygame.FULLSCREEN:pygame.display.set_mode((1280,800))
                    else:pygame.display.set_mode((0,0),pygame.HWSURFACE | pygame.FULLSCREEN)
                if event.key==pygame.K_1:
                    self.active=False 
                    pygame.quit()
                if event.key==pygame.K_f:self.skip=1
                
            
    def Gameplay(self):
        global keyboard,smooth,scroll,shake,zoom
        smooth=shake=zoom=[0,0]
        scroll=[258,0]
        while self.active:
            self.frame.tick(60)
            if self.skip or 1:
                screen.fill((100,100,100))
                keyboard=tuple(pygame.key.get_pressed())

                for t in totallist+P2list+P1list:
                    t.update(),t.fisics(),t.display()

                pushbox_pushbox_collide(P2list[0],P1list[0])
                smooth=[int(((P2list[0].rect.centerx-scroll[0]+P1list[0].rect.centerx-scroll[0])/2-640)/36),int(((P2list[0].rect.centery-scroll[1]+P1list[0].rect.centery-scroll[1])/2-608)/70)]
                scroll=[scroll[0]+smooth[0],scroll[1]+smooth[1]]

                self.skip=0
   

           
            main.blit(pygame.transform.scale(screen,reescale(main.get_size(),1)),(0,0))
            pygame.display.update()
            self.inpu()
Gameglobal=Game()

