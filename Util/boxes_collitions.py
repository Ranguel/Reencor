from itertools import combinations, permutations
from Util.Active_Objects import VisualEffectObject
from Util.Object_functions import colors, object_dict, object_list, function_dict, default_hitbox, attack_tipe_value, get_object_per_team, get_object_per_class, get_command, get_state, next_frame


def box_collide(r1x, r1y, r1w, r1h, r2x, r2y, r2w, r2h): return r1x < r2x + \
    r2w and r1x + r1w > r2x and r1y < r2y + r2h and r1y + r1h > r2y


def boundingbox_boundingbox_collide(self, other, game, *args):
    for bi in self.boxes['boundingbox'].get('boxes', []):
        for bu in other.boxes['boundingbox'].get('boxes', []):
            if box_collide(self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0), self.pos[1]-bi[3]-bi[1], bi[2], bi[3], other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0), other.pos[1]-bu[3]-bu[1], bu[2], bu[3]):
                if self.pos[1] > other.pos[1]-bu[1]-bu[3]:
                    if self.fet != 'grounded' and self.grabed == None and self.hitstop == 0:
                        self.fet, self.frame, self.current_command, self.wallbounce, self.hitstun, self.air_time = 'grounded', [
                            0, 0], self.current_command+['landing'], False, 0, 0
                        self.juggle = 100
                        get_command(self, self.current_command +
                                    list(self.inputdevice.current_input))
                        got_state = get_state(self, self.buffer_state)
                        if got_state:
                            next_frame(
                                self, object_dict[self.name]['moveset'][self.current_state]['framedata'][-self.frame[0]])
                    if not self.hitstop:
                        if not self.hitstun:
                            self.speed[0] *= self.boxes['boundingbox']['friction']
                        else:
                            self.speed[0] *= 0.85

                    self.pos[1], self.speed[1] = other.pos[1]-bu[1]-bu[3] + \
                        1, 0 if self.speed[1] < 0 else self.speed[1]
            else:
                self.fet, self.air_time = 'airborne', self.air_time+1

        if self.pos[0]+160 > game.pos[0]+game.internal_resolution[0]*0.5:
            if self.wallbounce and 'ummble' in self.current_state:
                    self.frame, self.speed, self.buffer_state['Tummble'], self.face, self.hitstop, game.osc, self.hitstop, self.juggle, self.wallbounce = [
                        0, 0], [-14, 24], 1, 1, 8, [0, 16], 16, 80, False

            if len(self.hurt_coll_hit) and self.speed[0] > 0:
                self.hurt_coll_hit[-1].speed[0] -= self.speed[0]*(
                    1 if self.hurt_coll_hit[-1].fet == 'airborne' else 0.9/self.hurt_coll_hit[-1].boxes['boundingbox']['friction'])
                self.hurt_coll_hit = []

            self.pos[0] = game.pos[0]+game.internal_resolution[0]*0.5-160

        if self.pos[0]-160 < game.pos[0]-game.internal_resolution[0]*0.5:
            if self.wallbounce and 'ummble' in self.current_state:
                    self.frame, self.speed, self.buffer_state['Tummble'], self.face, self.hitstop, game.osc, self.hitstop, self.juggle, self.wallbounce = [
                        0, 0], [14, 24], 1, -1, 8, [0, 16], 16, 80, False

            if len(self.hurt_coll_hit) and self.speed[0] < 0:
                self.hurt_coll_hit[-1].speed[0] -= self.speed[0]*(
                    1 if self.hurt_coll_hit[-1].fet == 'airborne' else 0.9/self.hurt_coll_hit[-1].boxes['boundingbox']['friction'])
                self.hurt_coll_hit = []

            self.pos[0] = game.pos[0]-game.internal_resolution[0]*0.5+160


def pushbox_pushbox_collide(self, other, *args):
    for bi in self.boxes['pushbox'].get('boxes', []):
        for bu in other.boxes['pushbox'].get('boxes', []):
            if box_collide(self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0), self.pos[1]-bi[3]-bi[1], bi[2], bi[3], other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0), other.pos[1]-bu[3]-bu[1], bu[2], bu[3]):
                # f=((self.gnd_friction if self.gnd_friction else object_dict[self.name]['gnd_friction'] if self.fet=='grounded' else object_dict[self.name]['abn_friction'])+(other.gnd_friction if other.gnd_friction else object_dict[other.name]['gnd_friction'] if other.fet=='grounded' else object_dict[other.name]['abn_friction']))/self.gnd_friction if self.gnd_friction else object_dict[self.name]['gnd_friction'] if self.fet=='grounded' else object_dict[self.name]['abn_friction']
                if self.pos[0] == other.pos[0]:
                    self.pos[0], other.pos[0] = self.pos[0] - \
                        self.face, other.pos[0]-other.face
                if self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0)+bi[2] > other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0) and self.pos[0] < other.pos[0]:
                    x = round(((self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0)+bi[2]) +
                               (other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0)))/2, 2)
                    self.pos[0], other.pos[0] = x-bi[0]*self.face+bi[2] * \
                        (self.face < 0)-bi[2], x-bu[0] * \
                        other.face+bu[2]*(other.face < 0)
                elif other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0)+bu[2] > self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0) and other.pos[0] < self.pos[0]:
                    x = round(((other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0)+bu[2]) +
                               (self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0)))/2, 2)
                    other.pos[0], self.pos[0] = x-bu[0]*other.face+bu[2] * \
                        (other.face < 0)-bu[2], x-bi[0] * \
                        self.face+bi[2]*(self.face < 0)


def hitbox_hurtbox_collide(self, other, *args):
    for bi in self.boxes['hitbox'].get('boxes', []):
        for bu in other.boxes['hurtbox'].get('boxes', []):
            if box_collide(self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0), self.pos[1]-bi[3]-bi[1], bi[2], bi[3], other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0), other.pos[1]-bu[3]-bu[1], bu[2], bu[3]) and self.boxes['hitbox'].get('hitset', 0) and (self.hitstop == 0 or other.hitstop == 0) and other.juggle > self.boxes['hitbox'].get('juggle', 1) and self.team != other.team:
                self.hit_coll_hurt.append(
                    other), other.hurt_coll_hit.append(self)
                self.box = [self.pos[0]+bi[0]*self.face-bi[2] *
                            (self.face < 0), self.pos[1]-bi[3]-bi[1], bi[2], bi[3]]
                return


def takebox_grabbox_collide(self, other, *args):
    for bi in self.boxes['takebox'].get('boxes', []):
        for bu in other.boxes['grabbox'].get('boxes', []):
            if box_collide(self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0), self.pos[1]-bi[3]-bi[1], bi[2], bi[3], other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0), other.pos[1]-bu[3]-bu[1], bu[2], bu[3]) and self.team != other.team:
                self.take_coll_grab.append(other)
                return


def trigger_hurtbox_collide(self, other, *args):
    for bi in self.boxes['triggerbox'].get('boxes', []):
        for bu in other.boxes['hurtbox'].get('boxes', []):
            if box_collide(self.pos[0]+bi[0]*self.face-bi[2]*(self.face < 0), self.pos[1]-bi[3]-bi[1], bi[2], bi[3], other.pos[0]+bu[0]*other.face-bu[2]*(other.face < 0), other.pos[1]-bu[3]-bu[1], bu[2], bu[3]) and self.team != other.team:
                self.trigger_coll_hurt.append(other)
                return


def calculate_boxes_collitions(game, *args):
    active_objects = [
        self for self in object_list if self.__class__.__name__ in ('CharacterActiveObject', 'ProjectileActiveObject')]
    main_stage = get_object_per_class('StageActiveObject')

    for self, other in permutations(active_objects, 2):
        trigger_hurtbox_collide(self, other), takebox_grabbox_collide(
            self, other), hitbox_hurtbox_collide(self, other)
    for self, other in combinations(active_objects, 2):
        pushbox_pushbox_collide(self, other)

    for self in active_objects:

        if self.self_main_object == None:
            self.self_main_object = get_object_per_team(self.team, False)
        if self.other_main_object == None:
            self.other_main_object = get_object_per_team(self.team)

        for other in self.take_coll_grab:
            for value in function_dict:
                if self.boxes['takebox'].get(value, None) != None:
                    function_dict[value](
                        self, self.boxes['takebox'][value], other)
        self.take_coll_grab = []

    for self in active_objects:
        for other in self.trigger_coll_hurt:
            for value in function_dict:
                if self.boxes['triggerbox'].get(value, None) != None:
                    function_dict[value](
                        self, self.boxes['triggerbox'][value], other)
        self.trigger_coll_hurt = []

    for self in active_objects:
        for other in self.hit_coll_hurt:
            hitbox = default_hitbox | self.boxes['hitbox']
            tipe, ri, ru = ['hurt'], .8+(self.combo/2)+1 if (
                0 not in other.cancel) else 0, -.8-(self.combo/4)-1 if (0 not in other.cancel) else 0
            if set(other.cancel).intersection(('neutral', 'interruption', "blocking")) and (other.inputdevice.current_input[0] == ('3'if (self.self_main_object.pos[0]-other.pos[0]) < 0 else '1')) and other.fet == 'grounded':
                if set(hitbox['hittipe']).intersection(('low', 'middle')):
                    tipe, ri, ru = ['block', 'crouch'], .1, .3
                else:
                    ri, ru = ri+.4, ru-.3
            elif set(other.cancel).intersection(('neutral', 'interruption', "blocking")) and (other.inputdevice.current_input[0] == ('6'if (self.self_main_object.pos[0]-other.pos[0]) < 0 else '4')) and other.fet == 'grounded':
                if set(hitbox['hittipe']).intersection(('high', 'middle')):
                    tipe, ri, ru = ['block', 'stand'], .1, .3
                else:
                    ri, ru = ri+.4, ru-.3
            elif set(other.cancel).intersection(('neutral', 'interruption', "parry", "blocking")) and (other.parry[0] == ('1'if (self.self_main_object.pos[0]-other.pos[0]) < 0 else '3')):
                if set(hitbox['hittipe']).intersection(('low', 'middle')) and other.parry[1] >= 16:
                    other.parry[1], tipe, ri, ru = 0, [
                        'parry', 'crouch'], -.2, .6
                else:
                    ri, ru = ri+.5, ru-.4
            elif set(other.cancel).intersection(('neutral', 'interruption', "parry", "blocking")) and (other.parry[0] == ('4'if (self.self_main_object.pos[0]-other.pos[0]) < 0 else '6')):
                if set(hitbox['hittipe']).intersection(('high', 'middle')) and other.parry[1] >= 16:
                    other.parry[1], tipe, ri, ru = 0, [
                        'parry', 'stand'], -.2, .6
                else:
                    ri, ru = ri+.5, ru-.4

            #tipe, ri, ru = ['parry', 'stand'], .1, .3
            self.self_main_object.combo, other.current_command, self.current_command = self.self_main_object.combo * \
                bool(other.hitstun)+1, tipe+hitbox['hittipe'], self.current_command+[
                    'parried' if 'parry' in tipe else 'blocked' if 'block' in tipe else 'hited']
            object_list.append(VisualEffectObject('SF3/Sparks', (self.box[0]+self.box[2]/2, self.box[1]+self.box[3]/2), self.face, 0, [
                tipe for tipe in attack_tipe_value if tipe in other.current_command][0]))
            for value in function_dict:
                if hitbox.get(value, None) != None:
                    function_dict[value](self, hitbox[value], other)
        self.hit_coll_hurt = []

    for self in active_objects:
        boundingbox_boundingbox_collide(self, main_stage, game)


def draw_boxes(game, object):
    if object.__class__.__name__ in ('CharacterActiveObject', 'ProjectileActiveObject', 'StageActiveObject'):
        for boxes_tipe in object.boxes:
            for box in object.boxes[boxes_tipe].get('boxes', []):
                game.screen.draw_rect((object.pos[0]+box[0]*object.face-box[2]*(object.face < 0),
                                       object.pos[1]-box[3]-box[1], box[2], box[3]), colors[boxes_tipe], 1, False, -2)
        game.screen.draw_cross(object.pos, 80)
