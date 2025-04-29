from pygame import mixer
from Util.Object_functions import image_dict, sound_dict, object_dict, RoundSign, get_command, get_state, next_frame, get_object_per_team, object_kill


class StageActiveObject():
    def __init__(self, game = object, key = 'grid', pos=(280, 200, 0), face=1, palette=0, inicial_state='grounded/n/5'):
        self.tipe = 'stage'
        self.name, self.pos, self.face, self.palette = key, ([pos[0], pos[1], 0] if len(
            pos) == 2 else pos), face, palette
        self.boxes = dict(object_dict[self.name]['boxes'])
        self.mass, self.scale = object_dict[self.name]['mass'], object_dict[self.name]['scale']
        self.frame, self.hitstop, self.draw_shake = [
            0, 0], 0, [0, 0, 0, 0, 0, 0]
        self.current_state, self.buffer_state = 'none', {}
        self.game = game

    def update(self, *args): pass

    def draw(self, screen, *args):
        for layer in object_dict[self.name]['layers']:
            screen.draw_texture(image_dict[object_dict[self.name]['layers'][layer]['image']][0], (object_dict[self.name]['layers'][layer]['pos'][0]+object_dict[self.name]['def_image_offset'][0]*self.face, object_dict[self.name]['layers'][layer]['pos'][1]+object_dict[self.name]['def_image_offset'][1], object_dict[self.name]
                                                                                                  ['layers'][layer]['pos'][2]), object_dict[self.name]['layers'][layer]['image_size'], (False, False), (255, 255, 255, 255), object_dict[self.name]['layers'][layer].get('angle', (0, 0, 0)), object_dict[self.name]['layers'][layer].get('repeat', False), object_dict[self.name]['layers'][layer].get('image_glow', 0))


class CharacterActiveObject():
    def __init__(self, game = object, team=1, inputdevice=object, key='', pos=(280, 200, 0), face=1, palette=0, inicial_state=False):
        self.tipe = 'character'
        self.team, self.inputdevice, self.name, self.pos, self.face, self.palette = team, inputdevice, key, ([
            pos[0], pos[1], 0] if len(pos) == 2 else pos), face, palette
        self.hurt_coll_hit, self.hit_coll_hurt, self.trigger_coll_hurt, self.take_coll_grab = [], [], [], []
        self.frame, self.image, self.image_size, self.image_offset, self.image_mirror, self.draw_shake = [
            0, 0], 'reencor/none', (100, 100), [0, 0], [False, False], [0, 0, 0, 0, 0, 0]
        self.current_command, self.command_index_timer = [5], {move: [[0, 0] for ind in object_dict[self.name]['moveset'][move].get(
            'command', ())] for move in object_dict[self.name]['moveset'] if object_dict[self.name]['moveset'][move].get('command', False)}
        self.mass, self.scale, self.time_kill, self.gauges, self.boxes = object_dict[self.name]['mass'], object_dict[self.name]['scale'], object_dict[self.name]['timekill'], {
            gauge: object_dict[self.name]['gauges'][gauge]['inicial'] for gauge in object_dict[self.name]['gauges']}, object_dict[self.name]['boxes']
        self.cancel, self.ignore_stop, self.hold_on_stun, self.kara, self.hitstun, self.hitstop = [
            0], False, False, 0, 0, 0
        self.speed, self.acceleration, self.con_speed, self.air_time, self.air_max_height = [
            0, 0], [0, 0], [0, 0], 0, 0
        self.fet, self.current_state, self.buffer_state, self.wallbounce = 'grounded', 'Stand', {}, False
        self.combo, self.parry, self.juggle, self.damage_scaling, self.last_damage = 0, [
            '6', 0], 100, [100, 100], [0, 0]
        self.voice_channel, self.sound_channel = mixer.Channel(
            self.team), mixer.Channel(self.team+2)
        self.move_raw_input = {move: [] for move in object_dict[self.name]['moveset']
                               if object_dict[self.name]['moveset'][move].get('command', False)}
        if inicial_state:
            get_state(self, {inicial_state: 2}, 1), next_frame(
                self, object_dict[self.name]['moveset'][self.current_state]['framedata'][0])
        self.self_main_object = None
        self.other_main_object = None
        self.object_influence = None
        self.grabed = None
        self.repeat = 0
        self.guard = ''

        self.image_tint = (255, 255, 255, 255)
        self.image_angle = (0, 0, 0)
        self.image_repeat = False
        self.image_glow = 0

        self.game = game

    def update(self, *args):
        if self.self_main_object == None:
            self.self_main_object = get_object_per_team(self.game.object_list, self.team, False)
        if self.other_main_object == None:
            self.other_main_object = get_object_per_team(self.game.object_list, self.team)
        if ((self.inputdevice.current_input[0] in ['1', '3'] and self.face > 0) or (self.inputdevice.current_input[0] in ['4', '6'] and self.face < 0)) and self.inputdevice.inter_press and self.parry[1] == 0:
            self.parry = [self.inputdevice.current_input[0], 24]
        self.parry[1] = self.parry[1]-1 if self.parry[1] else 0
        for gauge in self.gauges:
            if self.gauges[gauge] < 0:
                self.gauges[gauge] = 0
            if self.gauges[gauge] > object_dict[self.name]['gauges'][gauge]['max']:
                self.gauges[gauge] = object_dict[self.name]['gauges'][gauge]['max']
        for move in self.command_index_timer:
            for ind in range(len(self.command_index_timer[move])):
                self.command_index_timer[move][ind] = [self.command_index_timer[move][ind][0]if self.command_index_timer[move]
                                                       [ind][1] else 0, self.command_index_timer[move][ind][1]-1 if self.command_index_timer[move][ind][1]else 0]
        if (not self.hitstop) and (self.grabed == None):
            if self.hitstun:
                self.hitstun -= 1
            if ((set(self.cancel).intersection(['neutral', 'turn', 'kara']) or self.frame == [0, 0]) and self.fet == 'grounded' and self.face != RoundSign(self.other_main_object.pos[0]-self.pos[0]) and abs(self.other_main_object.pos[0]-self.pos[0]) > 32):
                self.face, self.current_command, self.inputdevice.inter_press = RoundSign(
                    self.other_main_object.pos[0]-self.pos[0]), ['turn']+self.current_command, 1
            self.speed = [self.speed[0]+self.acceleration[0] *
                          self.face, self.speed[1]+self.acceleration[1]]
            self.pos = [self.pos[0]+self.speed[0],
                        self.pos[1]-self.speed[1], self.pos[2]]
            if self.fet == 'airborne':
                self.speed[1] = self.speed[1]+object_dict[self.name]['gravity']
            if self.hitstun == 0:
                self.other_main_object.damage_scaling = [100, 100]
            self.buffer_state = {
                timer: self.buffer_state[timer]-1 for timer in self.buffer_state if self.buffer_state[timer] > 0}
        if self.inputdevice.inter_press or (self.frame[0] <= 0 and self.frame[1] <= 0):
            self.current_command += list(self.inputdevice.current_input)
            get_command(self, self.current_command)
        if ((self.inputdevice.inter_press or self.buffer_state) and (not set(self.cancel).intersection([None]) or self.kara) and (self.hitstop == 0 or self.hitstop and self.ignore_stop)) or (self.frame[0] <= 0 and self.frame[1] <= 0):
            get_state(self, self.buffer_state)
        self.frame[1] -= 1*(((self.hitstop != 0 and self.ignore_stop) or (not self.hitstop))
                            and ((self.hold_on_stun and self.hitstun == 0) or (not self.hold_on_stun)))
        if self.frame[1] <= 0:
            next_frame(self, object_dict[self.name]['moveset']
                       [self.current_state]['framedata'][-self.frame[0]])
        if self.con_speed[0] or self.con_speed[1]:
            self.speed = [self.speed[0]+self.con_speed[0],
                          self.speed[1]+self.con_speed[1]]
        if self.hitstop:
            self.hitstop = self.hitstop-1
        if self.kara:
            self.kara -= 1
        self.current_command = []
        if type(self.time_kill) != bool:
            self.time_kill -= 1
            if self.time_kill == 0:
                object_kill(self)

    def draw(self, screen, *args):
        screen.draw_texture(self.image, (self.draw_shake[0]+self.pos[0]-((self.image_offset[0])*(1 if self.face < 0 else -1))-(0 if self.face < 0 else self.image_size[0]*self.scale),
                                         self.draw_shake[1]+self.pos[1]-(-self.image_offset[1])), self.image_size, ((self.face > 0) and not self.image_mirror[0], self.image_mirror[1]), self.image_tint, self.image_angle, self.image_repeat, self.image_glow)


class ProjectileActiveObject():
    def __init__(self, game = object, team=1, inputdevice=object, key='', pos=(280, 200, 0), face=1, palette=0, inicial_state=False):
        self.tipe = 'character'
        self.team, self.inputdevice, self.name, self.pos, self.face, self.palette = team, inputdevice, key, ([
            pos[0], pos[1], 0] if len(pos) == 2 else pos), face, palette
        self.hurt_coll_hit, self.hit_coll_hurt, self.trigger_coll_hurt, self.take_coll_grab = [], [], [], []
        self.frame, self.image, self.image_size, self.image_offset, self.image_mirror, self.draw_shake = [
            0, 0], 'reencor/none', (100, 100), [0, 0], [False, False], [0, 0, 0, 0, 0, 0]
        self.current_command, self.command_index_timer = [5], {move: [[0, 0] for ind in object_dict[self.name]['moveset'][move].get(
            'command', ())] for move in object_dict[self.name]['moveset'] if object_dict[self.name]['moveset'][move].get('command', False)}
        self.mass, self.scale, self.time_kill, self.gauges, self.boxes = object_dict[self.name]['mass'], object_dict[self.name]['scale'], object_dict[self.name]['timekill'], {
            gauge: object_dict[self.name]['gauges'][gauge]['inicial'] for gauge in object_dict[self.name]['gauges']}, object_dict[self.name]['boxes']
        self.cancel, self.ignore_stop, self.hold_on_stun, self.kara, self.hitstun, self.hitstop = [
            0], False, False, 0, 0, 0
        self.speed, self.acceleration, self.con_speed, self.air_time, self.air_max_height = [
            0, 0], [0, 0], [0, 0], 0, 0
        self.fet, self.current_state, self.buffer_state, self.wallbounce = 'grounded', 'Stand', {}, False
        self.combo, self.parry, self.juggle, self.damage_scaling, self.last_damage = 0, [
            '6', 0], 100, [100, 100], [0, 0]
        self.voice_channel, self.sound_channel = mixer.Channel(
            self.team), mixer.Channel(self.team+2)
        self.move_raw_input = {move: [] for move in object_dict[self.name]['moveset']
                               if object_dict[self.name]['moveset'][move].get('command', False)}
        if inicial_state:
            get_state(self, {inicial_state: 2}, 1), next_frame(
                self, object_dict[self.name]['moveset'][self.current_state]['framedata'][0])
        self.self_main_object = None
        self.other_main_object = None
        self.object_influence = None
        self.grabed = None
        self.repeat = 0
        self.guard = ''

        self.image_tint = (255, 255, 255, 255)
        self.image_angle = (0, 0, 0)
        self.image_repeat = False
        self.image_glow = 0

        self.game = game

    def update(self, *args):
        if self.self_main_object == None:
            self.self_main_object = get_object_per_team(self.game.object_list, self.team, False)
        if self.other_main_object == None:
            self.other_main_object = get_object_per_team(self.game.object_list, self.team)
        if ((self.inputdevice.current_input[0] in ['1', '3'] and self.face > 0) or (self.inputdevice.current_input[0] in ['4', '6'] and self.face < 0)) and self.inputdevice.inter_press and self.parry[1] == 0:
            self.parry = [self.inputdevice.current_input[0], 24]
        self.parry[1] = self.parry[1]-1 if self.parry[1] else 0
        for gauge in self.gauges:
            if self.gauges[gauge] < 0:
                self.gauges[gauge] = 0
            if self.gauges[gauge] > object_dict[self.name]['gauges'][gauge]['max']:
                self.gauges[gauge] = object_dict[self.name]['gauges'][gauge]['max']
        for move in self.command_index_timer:
            for ind in range(len(self.command_index_timer[move])):
                self.command_index_timer[move][ind] = [self.command_index_timer[move][ind][0]if self.command_index_timer[move]
                                                       [ind][1] else 0, self.command_index_timer[move][ind][1]-1 if self.command_index_timer[move][ind][1]else 0]
        if (not self.hitstop) and (self.grabed == None):
            if self.hitstun:
                self.hitstun -= 1
                self.face, self.current_command, self.inputdevice.inter_press = RoundSign(
                    self.other_main_object.pos[0]-self.pos[0]), ['turn']+self.current_command, 1
            self.speed = [self.speed[0]+self.acceleration[0] *
                          self.face, self.speed[1]+self.acceleration[1]]
            self.pos = [self.pos[0]+self.speed[0],
                        self.pos[1]-self.speed[1], self.pos[2]]
            if self.fet == 'airborne':
                self.speed[1] = self.speed[1]+object_dict[self.name]['gravity']
            if self.hitstun == 0:
                self.other_main_object.damage_scaling = [100, 100]
            self.buffer_state = {
                timer: self.buffer_state[timer]-1 for timer in self.buffer_state if self.buffer_state[timer] > 0}
        if self.inputdevice.inter_press or (self.frame[0] <= 0 and self.frame[1] <= 0):
            self.current_command += list(self.inputdevice.current_input)
            get_command(self, self.current_command)
        if ((self.inputdevice.inter_press or self.buffer_state) and (not set(self.cancel).intersection([None])) and (self.hitstop == 0 or self.hitstop and self.ignore_stop)) or (self.frame[0] <= 0 and self.frame[1] <= 0):
            get_state(self, self.buffer_state)
        self.frame[1] -= 1*(((self.hitstop != 0 and self.ignore_stop) or (not self.hitstop))
                            and ((self.hold_on_stun and self.hitstun == 0) or (not self.hold_on_stun)))
        if self.frame[1] <= 0:
            next_frame(self, object_dict[self.name]['moveset']
                       [self.current_state]['framedata'][-self.frame[0]])
        if self.con_speed[0] or self.con_speed[1]:
            self.speed = [self.speed[0]+self.con_speed[0],
                          self.speed[1]+self.con_speed[1]]
        if self.hitstop:
            self.hitstop = self.hitstop-1
        if self.kara:
            self.kara -= 1
        self.current_command = []
        if type(self.time_kill) != bool:
            self.time_kill -= 1
            if self.time_kill == 0:
                object_kill(self)

    def draw(self, screen, *args):
        screen.draw_texture(self.image, (self.draw_shake[0]+self.pos[0]-((self.image_offset[0])*(1 if self.face < 0 else -1))-(0 if self.face < 0 else self.image_size[0]*self.scale),
                                         self.draw_shake[1]+self.pos[1]-(-self.image_offset[1])), self.image_size, ((self.face > 0) and not self.image_mirror[0], self.image_mirror[1]), self.image_tint, self.image_angle, self.image_repeat, self.image_glow)


class VisualEffectObject():
    def __init__(self, game = object, key='', pos=(280, 200, 0), face=1, palette=0, inicial_state=False):
        self.tipe = 'visualeffect'
        self.team, self.name, self.pos, self.face, self.palette = 0, key, ([pos[0], pos[1], 0] if len(
            pos) == 2 else pos), face, palette
        self.frame, self.image, self.image_size, self.image_offset, self.image_mirror, self.draw_shake = [
            0, 0], 'reencor/none', (100, 100), [0, 0], [False, False], [0, 0, 0, 0, 0, 0]
        self.mass, self.scale, self.time_kill, self.gauges, self.boxes = object_dict[self.name]['mass'], object_dict[self.name]['scale'], object_dict[self.name]['timekill'], {
            gauge: object_dict[self.name]['gauges'][gauge]['inicial'] for gauge in object_dict[self.name]['gauges']}, object_dict[self.name]['boxes']
        self.speed, self.acceleration, self.con_speed, self.air_time, self.air_max_height = [
            0, 0], [0, 0], [0, 0], 0, 0
        self.hitstun = 0
        self.fet, self.current_state, self.buffer_state, self.wallbounce = 'grounded', 'none', {}, False
        if inicial_state:
            get_state(self, {inicial_state: 2}, 1), next_frame(
                self, object_dict[self.name]['moveset'][self.current_state]['framedata'][0])
        self.repeat = 0

        self.image_tint = (255, 255, 255, 255)
        self.image_angle = (0, 0, 0)
        self.image_repeat = False
        self.image_glow = 0

        self.game = game

    def update(self, *args):
        if (self.frame[0] <= 0 and self.frame[1] <= 0):
            get_state(self, self.buffer_state)
        self.frame[1] -= 1
        if self.frame[1] <= 0:
            next_frame(self, object_dict[self.name]['moveset']
                       [self.current_state]['framedata'][-self.frame[0]])
        if type(self.time_kill) != bool:
            self.time_kill -= 1
            if self.time_kill == 0:
                object_kill(self)

    def draw(self, screen, pos): screen.draw_texture(self.image, (pos[0] if self.image_offset[0] == 'game'else (self.pos[0]-((self.image_offset[0])*(1 if self.face < 0 else -1))-(0 if self.face < 0 else self.image_size[0]*self.scale)),
                                                                  pos[1] if self.image_offset[1] == 'game'else (self.pos[1]-(-self.image_offset[1]))), self.image_size, ((self.face > 0) and not self.image_mirror[0], self.image_mirror[1]), self.image_tint, self.image_angle, self.image_repeat, self.image_glow)


dummy_json = {
    "tipe": "proyectile",
    "palette": [],
    "scale": [1, 1],
    "gravity": 0,
    "mass": 1,
    "music": "",
    "terminal_velocity": 1,
    "gauges": {},
    "boxes": {"hurtbox": {"boxes": []}, "hitbox": {"boxes": []}, "takebox": {"boxes": []}, "grabbox": {"boxes": []}, "pushbox": {"boxes": []}, "triggerbox": {"boxes": []}, "boundingbox": {"boxes": []}},
    "def_image_offset": [0, 0],
    "timekill": False,
    "trials": [],
    "moveset": {
    }
}


class Dummy_object:
    def __init__(self):
        self.tipe = 'dummy'
        self.team, self.name, self.pos, self.face, self.palette = 1, 'Dummy', [
            0, 0, 0], 1, 0
        self.hurt_coll_hit, self.hit_coll_hurt, self.trigger_coll_hurt = [], [], []
        self.frame, self.image, self.image_offset, self.draw_shake, self.osc, self.path = [
            0], 'reencor/none', [0, 0], [0, 0], [0, 0], [0, 0, 0, 0, 0, 0, 0]
        self.current_command, self.command_index_timer = [5], {move: [
            0 for ind in dummy_json['moveset'][move]['command']] for move in dummy_json['moveset']}
        self.mass, self.scale, self.time_kill, self.gauges, self.boxes = dummy_json['mass'], dummy_json['scale'], dummy_json['timekill'], {
            gauge: dummy_json['gauges'][gauge]['inicial'] for gauge in dummy_json['gauges']}, dummy_json['boxes']
        self.cancel, self.ignore_stop, self.kara, self.hitstun, self.hitstop = [
            0], 0, 0, 0, 0
        self.speed, self.acceleration, self.con_speed, self.air_time, self.air_max_height = [
            0, 0], [0, 0], [0, 0], 0, 0
        self.fet, self.current_state, self.buffer_state, self.wallbounce = 'grounded', 'none', {}, False
        self.combo, self.juggle, self.damage_scaling, self.last_damage = 0, 100, [
            100, 100], [0, 0]
        self.self_main_object = None
        self.other_main_object = None
        self.object_influence = None


def reset_CharacterActiveObject(self, game = object, team=1, inputdevice=object, key='', pos=(280, 200, 0), face=1, palette=0, inicial_state=False):
        self.tipe = 'character'
        self.team, self.inputdevice, self.name, self.pos, self.face, self.palette = team, inputdevice, key, ([
            pos[0], pos[1], 0] if len(pos) == 2 else pos), face, palette
        self.hurt_coll_hit, self.hit_coll_hurt, self.trigger_coll_hurt, self.take_coll_grab = [], [], [], []
        self.frame, self.image, self.image_size, self.image_offset, self.image_mirror, self.draw_shake = [
            0, 0], 'reencor/none', (100, 100), [0, 0], [False, False], [0, 0, 0, 0, 0, 0]
        self.current_command, self.command_index_timer = [5], {move: [[0, 0] for ind in object_dict[self.name]['moveset'][move].get(
            'command', ())] for move in object_dict[self.name]['moveset'] if object_dict[self.name]['moveset'][move].get('command', False)}
        self.mass, self.scale, self.time_kill, self.gauges, self.boxes = object_dict[self.name]['mass'], object_dict[self.name]['scale'], object_dict[self.name]['timekill'], {
            gauge: object_dict[self.name]['gauges'][gauge]['inicial'] for gauge in object_dict[self.name]['gauges']}, object_dict[self.name]['boxes']
        self.cancel, self.ignore_stop, self.hold_on_stun, self.kara, self.hitstun, self.hitstop = [
            0], False, False, 0, 0, 0
        self.speed, self.acceleration, self.con_speed, self.air_time, self.air_max_height = [
            0, 0], [0, 0], [0, 0], 0, 0
        self.fet, self.current_state, self.buffer_state, self.wallbounce = 'grounded', 'Stand', {}, False
        self.combo, self.parry, self.juggle, self.damage_scaling, self.last_damage = 0, [
            '6', 0], 100, [100, 100], [0, 0]
        self.voice_channel, self.sound_channel = mixer.Channel(
            self.team), mixer.Channel(self.team+2)
        self.move_raw_input = {move: [] for move in object_dict[self.name]['moveset']
                               if object_dict[self.name]['moveset'][move].get('command', False)}
        if inicial_state:
            get_state(self, {inicial_state: 2}, 1), next_frame(
                self, object_dict[self.name]['moveset'][self.current_state]['framedata'][0])
  
        self.grabed = None
        self.repeat = 0

        self.image_tint = (255, 255, 255, 255)
        self.image_angle = (0, 0, 0)
        self.image_repeat = False
        self.image_glow = 0

        self.game = game