import os,json
from pygame import mouse

from Util.Object_functions import color, colors, image_dict, sound_dict, object_dict, draw_string, gradient_color, nomatch, RoundSign, get_command, get_state, next_frame, get_object_per_class_ev, get_object_per_team, object_image, object_kill
from Util.boxes_collitions import box_collide

current_dir = os.path.dirname(os.path.realpath(__file__))


class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, dict):
            formatted_items = []
            for key, value in obj.items():
                if isinstance(value, dict) and key == "moveset":
                    # Serializar moveset asegurando que cada clave-valor esté en una línea
                    formatted_moveset = ",\n    ".join(
                        f'"{k}": {json.dumps(v)}' for k, v in value.items())
                    # Ajustar indentación
                    formatted_value = "{\n    " + formatted_moveset + "\n}"
                elif isinstance(value, dict):
                    # Mantener otros diccionarios en una sola línea
                    formatted_value = json.dumps(value, separators=(',', ': '))
                else:
                    formatted_value = json.dumps(
                        value, separators=(',', ': '))  # Mantener inline
                formatted_items.append(f'"{key}": {formatted_value}')
            return "{\n  " + ",\n  ".join(formatted_items) + "\n}"
        return super().encode(obj)


class Menu_Item():
    def __init__(self, name='dummy', pos=(0, 0, 0), size=(100, 100), func=nomatch, param=None):
        self.name, self.pos, self.size, self.func, self.param, self.timer = name, pos, size, func, param, 0
        self.image, self.image_size, self.image_offset, self.image_mirror, self.draw_shake = None, (100, 100), [
            0, 0], [False, False], [0, 0, 0, 0, 0, 0]
        self.image_tint, self.image_angle, self.image_repeat, self.image_glow = (
            255, 255, 255, 255), (0, 0, 0), False, 1
        self.scale = [1, 1]
        object_image(self, object_dict[name].get('portrait', 'reencor/none'))

    def selected(self): self.timer = 8

    def update(self, *args):
        if self.timer:
            self.timer -= 1

    def draw(self, screen, pos, *args):
        screen.draw_texture(self.image, (pos[0]+self.draw_shake[0]-screen.size[0]/2+self.pos[0], pos[1]+self.draw_shake[1]-screen.size[1]/2+self.pos[1], self.pos[2]-self.timer),
                            self.size, self.image_mirror, self.image_tint, self.image_angle, self.image_repeat, self.image_glow)


class Menu_Item_String():
    def __init__(self, name = '', pos: list = (0, 0, 0), scale: list = (1, 1), func: callable = nomatch, param: any = None, alignment: str = 'right', color: list = (255, 255, 255, 255), gradient_timer: int = 0):
        self.name, self.pos, self.size, self.func, self.param, self.timer = name, pos, scale(
            name, scale), func, param, 0
        self.image, self.image_size, self.image_offset, self.image_mirror, self.draw_shake = None, (100, 100), [
            0, 0], [False, False], [0, 0, 0, 0, 0, 0]
        self.image_tint, self.image_angle, self.image_repeat, self.image_glow = (
            255, 255, 255, 255), (0, 0, 0), False, 1
        self.scale = scale
        self.alignment = alignment
        self.color = color
        self.gradient_timer = 0

    def selected(self): self.timer = 8

    def update(self, *args):
        if self.timer:
            self.timer -= 1

    def draw(self, screen, *args):
        draw_string(screen, self.name, (self.draw_shake[0] + self.pos[0], self.draw_shake[1] +
                    self.pos[1], self.pos[2]-self.timer), self.scale, self.color, self.alignment)


class Menu_Selector():
    def __init__(self, team, inputdevice=object, menu=(Menu_Item), index=0):
        self.inputdevice, self.selected_index, self.last_index, self.timer, self.selected, self.selected_name, self.current_input, self.last_input, self.pos, self. size = inputdevice, index, 0, 0, 0, None, inputdevice.raw_input, inputdevice.raw_input, (
            0, 0), (100, 100)
        self.menu = menu
        self.color = color[team]
        self.image, self.image_size, self.image_offset, self.image_mirror, self.draw_shake = None, (100, 100), [
            0, 0], [False, False], [0, 0, 0, 0, 0, 0]
        self.image_tint, self.image_angle, self.image_repeat, self.image_glow = (
            255, 255, 255, 255), (0, 0, 0), False, 0
        self.scale = [1, 1]
        self.team = team
        self.select_int = 0
        self.index_int = 1

    def on_selection(self, *args):
        self.menu[self.selected_index].selected(
        ), self.menu[self.selected_index].func()
        self.selected, self.selected_name, self.select_int = 1, self.menu[
            self.selected_index].name, 1

    def on_deselection(
        self, *args): self.selected, self.selected_name, self.select_int = 0, None, -1

    def change_index(self, best_option, *args):
        self.selected_index, self.timer, self.last_index, self.index_int = best_option, 6, self.selected_index, 1

    def update(self, *args):
        self.select_int, self.index_int = 0, 0
        best_option, best_score, self.timer = None, float(
            'inf'), self.timer-1
        if self.timer < 0:
            self.timer, self.last_index = 30, self.selected_index
        if self.inputdevice.inter_press:
            if 'short' in self.inputdevice.current_press:
                self.on_selection()
            if 'forward' in self.inputdevice.current_press:
                self.on_deselection()
            if self.selected == 0:
                if self.inputdevice.current_input[0] != '5' and self.inputdevice.current_input[0] != self.last_input[0]:
                    for ind in range(len(self.menu)):
                        if ind == self.selected_index:
                            continue
                        dx, dy = (self.menu[self.selected_index].pos[0]+self.menu[self.selected_index].size[0]/2)-(self.menu[ind].pos[0]+self.menu[ind].size[0] /
                                                                                                                   2), (self.menu[ind].pos[1]+self.menu[ind].size[1]/2)-(self.menu[self.selected_index].pos[1]+self.menu[self.selected_index].size[1]/2)
                        if (self.inputdevice.current_input[0] == '6' and dx >= 0) or (self.inputdevice.current_input[0] == '4' and dx <= 0) or (self.inputdevice.current_input[0] == '8' and dy >= 0) or (self.inputdevice.current_input[0] == '2' and dy <= 0):
                            continue
                        score = (abs(dx)*(3 if self.inputdevice.current_input[0] in ('1', '3', '4', '6', '7', '9') else 1))+(
                            abs(dy)*(3 if self.inputdevice.current_input[0] in ('1', '2', '3', '7', '8', '9') else 1))
                        if score < best_score:
                            best_score, best_option = score, ind
                    if best_option != None:
                        self.change_index(best_option)

        self.last_input = self.inputdevice.current_input

    def draw(self, screen, pos, *args):
        screen.draw_rect((pos[0]+self.draw_shake[0]-screen.size[0]/2+self.menu[self.selected_index].pos[0]+(self.menu[self.last_index].pos[0]-self.menu[self.selected_index].pos[0])/6*self.timer, pos[1]+self.draw_shake[1]-screen.size[1]/2 + + self.menu[self.selected_index].pos[1]+(self.menu[self.last_index].pos[1] -
                                                                                                                                                                                                                                                                                         self.menu[self.selected_index].pos[1])/6*self.timer, self.menu[self.selected_index].size[0], self.menu[self.selected_index].size[1]), gradient_color(0 if self.selected else self.timer, 30, self.color, (255, 255, 255, 255)), 5, False, -self.menu[self.selected_index].timer if self.selected else 0)


class Menu_Deck():
    def __init__(self, name: str = '', pos=(0, 0, 0), size=(200, 200), items: list = [Menu_Item], selectors: list = (Menu_Selector)):
        self.name, self.pos, self.size, self.items, self.selectors = name, pos, size, items, selectors
        self.top_bar = (pos[0], pos[1], size[0], size[1]*0.1)
        self.image, self.image_size, self.image_offset, self.image_mirror, self.draw_shake = None, (100, 100), [
            0, 0], [False, False], [0, 0, 0, 0, 0, 0]
        self.image_tint, self.image_angle, self.image_repeat, self.image_glow = (
            255, 255, 255, 255), (0, 0, 0), False, 0
        self.scale = [1, 1]

    def show_window(self):
        0

    def hide_window(self):
        0

    def update(self, *args):
        for item in self.items:
            item.update(self.surface)

        for selector in self.selectors:
            selector.update(self.surface, self.items)

    def draw(self, screen, pos, *args):
        for item in self.items:
            item.draw(screen, pos)

        for selector in self.selectors:
            selector.draw(screen, pos)


class Menu_Cursor():
    def __init__(self, player):
        self.player, self.rect, self.current_input, self.last_input, self.inter_press, self.selected, self.over, self.timer = player, (
            0, 0, 20, 20), (0, 0), (0, 0), 0, None, None, 0
        self.edge_list, self.edge_edit, self.box_list, self.box_tipe = ((-20, -20, 10, 10), (
            -20, -20, 10, 10), (-20, -20, 10, 10), (-20, -20, 10, 10)), [False, 0], [], ''
        self.box_addition = False
        self.box_edit = False
        self.selected_box_tipe = 'hurtbox'
        global game
        game = get_object_per_class_ev("GameObject")

    def change_box_tipe(
        self, selected_box_tipe): self.selected_box_tipe = selected_box_tipe

    def new_boxes(
        self, *args): self.box_edit, self.box_list, self.box_addition = True, [], True

    def save_boxes(self, *args):
        new_json = dict(object_dict[self.player.name])
        if self.box_addition:
            new_json['moveset'][self.player.current_state]['framedata'][-self.player.frame[0] -
                                                                        1][self.box_tipe] = {'boxes': self.box_list}
        else:
            for index in range(self.player.frame[0], len(new_json['moveset'][self.player.current_state]['framedata'])):
                if new_json['moveset'][self.player.current_state]['framedata'][-index].get(self.box_tipe, None) != None:
                    new_json['moveset'][self.player.current_state]['framedata'][-index][self.box_tipe]['boxes'] = self.box_list
                    break

        with open(current_dir + '/objects/' + str(self.player.name) + '.json', 'w') as outfile:
            outfile.write(CustomJSONEncoder().encode(new_json))

        object_dict[self.player.name] = new_json

        self.box_edit, self.box_list, self.box_addition = False, [], False

    def Box_specific(self, screen, boxes, tipe='hurtbox', *args):
        if self.edge_edit[0] == False:
            coll_any = 0
            for index, box in enumerate(boxes):
                if box_collide(-game.pos[0]+self.player.rect.centerx+box[0]*self.player.face-box[2]*(self.player.face < 0), -game.pos[1]+self.player.rect.centery-box[3]-box[1], box[2], box[3], self.rect[0], self.rect[1], self.rect[2], self.rect[3]):
                    self.over, coll_any = index, coll_any+1
                    if self.inter_press and 1 in self.current_input:
                        if index == self.selected:
                            if not self.box_addition:
                                self.box_list = []
                            self.selected, self.edge_list, self.edge_edit = None, ((-20, -20, 10, 10), (
                                -20, -20, 10, 10), (-20, -20, 10, 10), (-20, -20, 10, 10)), [False, 0]
                        else:
                            if not self.box_addition:
                                self.box_list = self.player.boxes[tipe]['boxes']
                            self.box_edit = True
                            self.selected, self.edge_list, self.box_tipe = index, [(-game.pos[0]+self.player.rect.centerx+box[0]*self.player.face-box[2]*(self.player.face < 0)-10, -game.pos[1]+self.player.rect.centery-box[1]-10, 20, 20), (-game.pos[0]+self.player.rect.centerx+box[0]*self.player.face-box[2]*(self.player.face < 0)+box[2]-10, -game.pos[1]+self.player.rect.centery-box[1]-10, 20, 20), (
                                -game.pos[0]+self.player.rect.centerx+box[0]*self.player.face-box[2]*(self.player.face < 0)+box[2]-10, -game.pos[1]+self.player.rect.centery-box[3]-box[1]-10, 20, 20), (-game.pos[0]+self.player.rect.centerx+box[0]*self.player.face-box[2]*(self.player.face < 0)-10, -game.pos[1]+self.player.rect.centery-box[3]-box[1]-10, 20, 20),], tipe
                        break
            if coll_any == 0:
                self.over = None
                if self.inter_press and self.current_input[0]:
                    if not self.box_edit:
                        self.box_list, self.box_addition = [], False
                    self.selected, self.edge_list, self.edge_edit = None, ((-20, -20, 10, 10), (
                        -20, -20, 10, 10), (-20, -20, 10, 10), (-20, -20, 10, 10)), [False, 0]
                if self.inter_press and self.current_input[2]:
                    self.box_edit, self.box_tipe, self.box_addition, self.box_list = True, tipe, True, self.box_list + \
                        [(60, 60, -self.player.rect.centerx+self.rect.centerx-game.pos[0],
                          self.player.rect.centery-self.rect.centery-game.pos[1])]

        for boxes_tipe in self.player.boxes:
            if boxes_tipe != tipe:
                for box in self.player.boxes[boxes_tipe].get('boxes', []):
                    screen.draw_rect(gradient_color(5, 10, colors[boxes_tipe], (0, 0, 0)), (-game.pos[0]+self.player.rect.centerx+box[0]*self.player.face-box[2]*(
                        self.player.face < 0), -game.pos[1]+self.player.rect.centery-box[3]-box[1], box[2], box[3]), 3)
        for boxes_tipe in self.player.boxes:
            if boxes_tipe == tipe:
                for box in self.player.boxes[boxes_tipe].get('boxes', []):
                    screen.draw_rect(colors[boxes_tipe], (-game.pos[0]+self.player.rect.centerx+box[0]*self.player.face-box[2]*(
                        self.player.face < 0), -game.pos[1]+self.player.rect.centery-box[3]-box[1], box[2], box[3]), 3)
        screen.draw_rect((0, 0, 0), (-game.pos[0]+self.player.rect.centerx-16, -game.pos[1] +
                                             self.player.rect.centery), (-game.pos[0]+self.player.rect.centerx+16, -game.pos[1]+self.player.rect.centery), 3)
        screen.draw_rect((0, 0, 0), (-game.pos[0]+self.player.rect.centerx, -game.pos[1]+self.player.rect.centery-16),
                         (-game.pos[0]+self.player.rect.centerx, -game.pos[1]+self.player.rect.centery+16), 3)

        if self.over != None and self.selected == None:
            screen.draw_rect(gradient_color(self.timer, 30, (120, 120, 255), (255, 255, 255)), (-game.pos[0]+self.player.rect.centerx+boxes[self.over][0]*self.player.face-boxes[self.over][2]*(
                self.player.face < 0), -game.pos[1]+self.player.rect.centery-boxes[self.over][3]-boxes[self.over][1], boxes[self.over][2], boxes[self.over][3]), 4)

    def menu_specific(self, menus, *args):
        for menu in menus:
            for item in menu.items:
                if box_collide(menu.rect[0]+item.rect[0], menu.rect[1]+item.rect[1], item.rect[2], item.rect[3], self.rect[0], self.rect[1], self.rect[2], self.rect[3]) and self.inter_press and self.current_input[0]:
                    item.selected()
                    item.func(item.param)
                    return

    def update(self, menus: list = (Menu_Deck), *args):
        self.current_input, self.rect.center, self.timer = mouse.get_pressed(
        ), mouse.get_pos(), 0 if self.timer > 30 else self.timer+1
        self.inter_press = 1 if self.current_input != self.last_input else 0

        self.menu_specific(menus)

        if self.selected != None:
            for index, rect in enumerate(self.edge_list):
                if box_collide(rect[0], rect[1], rect[2], rect[3], self.rect[0], self.rect[1], self.rect[2], self.rect[3]):
                    if self.inter_press and self.current_input[2]:
                        self.box_list.pop(self.selected)
                        self.selected, self.edge_list, self.edge_edit = None, ((-20, -20, 10, 10), (
                            -20, -20, 10, 10), (-20, -20, 10, 10), (-20, -20, 10, 10)), [False, 0]
                        break
                    if self.inter_press and self.current_input[0]:
                        self.edge_edit = [True, index]
                        break
            if not self.current_input[0]:
                self.edge_edit = [False, 0]
            if self.edge_edit[0]:
                self.edge_list[self.edge_edit[1]].center = self.rect.center
                if self.edge_edit[1] == 0:
                    self.edge_list[3].centerx, self.edge_list[1].centery = self.edge_list[self.edge_edit[1]
                                                                                          ].centerx, self.edge_list[self.edge_edit[1]].centery
                elif self.edge_edit[1] == 1:
                    self.edge_list[2].centerx, self.edge_list[0].centery = self.edge_list[self.edge_edit[1]
                                                                                          ].centerx, self.edge_list[self.edge_edit[1]].centery
                elif self.edge_edit[1] == 2:
                    self.edge_list[1].centerx, self.edge_list[3].centery = self.edge_list[self.edge_edit[1]
                                                                                          ].centerx, self.edge_list[self.edge_edit[1]].centery
                else:
                    self.edge_list[0].centerx, self.edge_list[2].centery = self.edge_list[self.edge_edit[1]
                                                                                          ].centerx, self.edge_list[self.edge_edit[1]].centery

                point_list_x, point_list_y = [self.edge_list[0].centerx, self.edge_list[1].centerx, self.edge_list[2].centerx, self.edge_list[3].centerx], [
                    self.edge_list[0].centery, self.edge_list[1].centery, self.edge_list[2].centery, self.edge_list[3].centery]
                self.box_list[self.selected] = [-self.player.rect.centerx+min(point_list_x)-game.pos[0], self.player.rect.centery-max(
                    point_list_y)-game.pos[1], abs(max(point_list_x)-min(point_list_x)), abs(max(point_list_y)-min(point_list_y))]

    def draw(self, screen):

        if self.box_edit:
            self.Box_specific(screen, self.box_list, self.selected_box_tipe)
        else:
            self.Box_specific(screen, self.player.boxes[self.selected_box_tipe].get(
                'boxes', []), self.selected_box_tipe)
        self.last_input = self.current_input

        if self.selected != None:
            screen.draw_rect(screen, (0, 0, 0), (self.edge_list[0].centerx, self.edge_list[0].centery), (self.edge_list[1].centerx, self.edge_list[1].centery), 3), screen.draw_rect((0, 0, 0), (self.edge_list[1].centerx, self.edge_list[1].centery), (self.edge_list[2].centerx, self.edge_list[2].centery), 3), screen.draw_rect(
                (0, 0, 0), (self.edge_list[2].centerx, self.edge_list[2].centery), (self.edge_list[3].centerx, self.edge_list[3].centery), 3), screen.draw_rect((0, 0, 0), (self.edge_list[3].centerx, self.edge_list[3].centery), (self.edge_list[0].centerx, self.edge_list[0].centery), 3)
        for rect in self.edge_list:
            screen.draw_rect(screen, (255, 255, 255), rect)
        screen.draw_rect(screen, (20, 20, 20), 0, ((
            self.rect.centerx+8, self.rect.centery+20), self.rect.center, (self.rect.centerx+20, self.rect.centery+8)), 8)


class Combo_Counter():
    def __init__(self, team=1):
        self.team = team
        self.image, self.image_size = '2', (1000, 200)
        self.scale = [1.5, 1.5]
        self.pos, self.timer, self.gradient_timer = (40, 150, 0), 0, 0
        self.combo = 0
        self.self_main_object = None
        self.other_main_object = None
        self.draw_shake = [0, 0, 0, 0, 0, 0]

    def update(self, *args):
        if self.self_main_object == None:
            self.self_main_object = get_object_per_team(self.team, False)

        if self.other_main_object == None:
            self.other_main_object = get_object_per_team(self.team)

        if self.self_main_object.combo != self.combo:
            self.combo, self.timer, self.gradient_timer = self.self_main_object.combo, (150)*(
                self.self_main_object.combo > 1), (90)*(self.self_main_object.combo > 1)
        self.timer = self.timer-1 if self.timer else 0
        self.gradient_timer = self.gradient_timer-1 if self.gradient_timer else 6

    def draw(self, screen, pos, *args):
        if self.timer:
            draw_string(screen, 'COMBO '+str(self.combo), (self.draw_shake[0] + (pos[0]-((screen.size[0]*0.5)*abs(pos[2]/400))+40 if self.team == 1 else pos[0]+((screen.size[0]*0.5)*abs(pos[2]/400))-40), self.draw_shake[1] + pos[1]-(
                (screen.size[1]*0.5)*abs(pos[2]/400))+self.pos[1], self.pos[2]), self.scale, gradient_color(self.gradient_timer, 6, (160, 160, 160, 0), (160, 160, 160, 255)), 'right' if self.team == 1 else 'left')


class Gauge_Bar():
    def __init__(self, team, tipe):
        self.team = team
        self.image, self.image_size = '2', (1000, 200)
        self.pos, self.timer, self.gradient_timer = (40, 150, 0), 0, 0
        self.tipe = tipe
        self.self_main_object = None
        self.texture_dict = {}
        self.draw_shake = [0, 0, 0, 0, 0, 0]

    def get_texture_dict(self):
        for n in range(len(object_dict[self.self_main_object.name]['gauges'][self.tipe]['images'])):
            object_image(
                self, object_dict[self.self_main_object.name]['gauges'][self.tipe]['images'][n]['name'])
            self.texture_dict[n] = self.image, object_dict[self.self_main_object.name]['gauges'][self.tipe]['images'][
                n]['pos'], object_dict[self.self_main_object.name]['gauges'][self.tipe]['images'][n]['size']
        self.gauge = object_dict[self.self_main_object.name]['gauges'][self.tipe]

    def update(self, *args):
        if self.self_main_object == None:
            self.self_main_object = get_object_per_team(self.team, False)
            self.get_texture_dict()

        self.timer = self.timer-1 if self.timer else 0
        if self.timer < 0:
            self.timer = self.gauge.get('blink', 0)

    def draw(self, screen, pos, *args):

        # color_grad = gradient_color(self.timer, self.gauge.get('blink', 0), self.gauge['color'][0], self.gauge['color'][1])if self.gauge.get(
        #     'blink', 0)else gradient_color(self.self_main_object.gauges[self.tipe], self.gauge['max'], self.gauge['color'][0], self.gauge['color'][1])

        # pygame.draw.line(self.surface, color_grad, (self.gauge['start'][0]-round((self.gauge['start'][0]-self.gauge['end'][0])*(((self.self_main_object.gauges[self.tipe]/self.gauge['max'])
        #                  * self.gauge['level']) % 1+int(self.self_main_object.gauges[self.tipe] >= self.gauge['max']))), self.gauge['start'][1]), self.gauge['start'], self.gauge['thickness'])

        for image in self.texture_dict:
            screen.draw_texture(self.texture_dict[image][0], (pos[0]+((-screen.size[0]*0.5+self.texture_dict[image][1][0]) if self.team == 1 else (screen.size[0]*0.5-self.texture_dict[image]
                                                                                                                                                   [1][0]-self.texture_dict[image][2][0])), pos[1]-screen.size[1]*0.5+self.texture_dict[image][1][1], -2), self.texture_dict[image][2], (self.team == 1, False), (255, 255, 255, 255), [0, 0, 0], False, 1)

        # if self.gauge.get('level_indicator', False):
        #     screen.draw_texture(menu_font.render(str(int(
        #         (self.self_main_object.gauges[self.tipe]/self.gauge['max'])*self.gauge['level'])), True, color_grad), self.gauge['level_indicator'])
