from pygame import joystick, key
from random import uniform, choice
from Util.Object_functions import RoundSign, object_image


keyboard_mapping = ((79,), (80,), (82,), (81,), (8,), (26,),
                    (20,), (7,), (22,), (4,), (21, 92), (21,), (116,))

joystick_name_mapping = {
    'Nintendo Switch Pro Controller': ((('a', 0), ('b', 14), ('b', 13, 1)), (('a', 1), ('b', 11, 1), ('b', 12)), (('a', 5),), (('b', 0),), (('b', 1),), (('b', 10),), (('b', 2),), (('b', 3),), (('b', 9), ('a', 4),)),
    'Xbox Controller': ((('a', 0),), (('a', 1),), (('b', 4),), (('b', 3),), (('b', 2),), (('b', 5),), (('b', 1),), (('a', 2),), (('a', 3),)), }


class InputDevice():
    def __init__(self, team=1, index=0, mode='none', show=0):
        self.tipe = 'input'
        self.team, self.key, self.mode = team, keyboard_mapping, {
            'keyboard': self.keyboard_mode, 'joystick': self.joystick_mode, 'AI': self.AI_mode, 'record': self.record_mode, 'none': self.none_mode, 'random': self.random_mode}[mode]
        if mode == 'joystick':
            self.controller = joystick.Joystick(index)
            self.con = joystick_name_mapping[self.controller.get_name()]
        self.show, self.press_list_showed = show, [
            ['false', 'false'] for n in range(9)]
        self.current_input, self.raw_input, self.current_input, self.last_input, self.press_charge, self.inter_press = [[0, 0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], ['5'], [[0, 0], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0
        self.mode_name = 'AI'
        self.input_timer = 0
        self.record_timer = 0
        self.recorded_inputs = []
        self.last_input_timer = 0
        self.recorded_inputs_index = 0
        self.draw_shake = [0, 0, 0, 0, 0, 0]
        self.rand_timer = 0

    def axis_button(self, input): return (RoundSign(round(self.controller.get_axis(input[1]))))if input[0] == 'a'else (
        self.controller.get_button(input[1])*(-1 if len(input) > 2 else 1))

    def keyboard_mode(self):
        keyboard = tuple(key.get_pressed())  # index
        self.raw_input = [sum(keyboard[key] for key in self.key[0]), sum(keyboard[key] for key in self.key[1]), sum(keyboard[key] for key in self.key[2]), sum(keyboard[key] for key in self.key[3]), sum(keyboard[key] for key in self.key[4]), sum(
            keyboard[key] for key in self.key[5]), sum(keyboard[key] for key in self.key[6]), sum(keyboard[key] for key in self.key[7]), sum(keyboard[key] for key in self.key[8]), sum(keyboard[key] for key in self.key[9]), sum(keyboard[key] for key in self.key[10])]
        self.get_press([[self.raw_input[0]+self.raw_input[1]*-1, self.raw_input[2]+self.raw_input[3]*-1], self.raw_input[4],
                        self.raw_input[5], self.raw_input[6], self.raw_input[7], self.raw_input[8], self.raw_input[9], self.raw_input[10]])

    def joystick_mode(self):
        self.raw_input = [(sum((self.axis_button(key))for key in self.con[0]), -sum(self.axis_button(key)for key in self.con[1])), sum(self.axis_button(key)for key in self.con[2]), sum(self.axis_button(key)for key in self.con[3]), sum(self.axis_button(key)
                                                                                                                                                                                                                                           for key in self.con[4]), sum(self.axis_button(key)for key in self.con[5]), sum(self.axis_button(key)for key in self.con[6]), sum(self.axis_button(key)for key in self.con[7]), sum(self.axis_button(key)for key in self.con[8])]
        self.get_press(self.raw_input)

    def AI_mode(self):
        self.get_press([[self.raw_input[0]+self.raw_input[1]*-1, self.raw_input[2]+self.raw_input[3]*-1], self.raw_input[4],
                        self.raw_input[5], self.raw_input[6], self.raw_input[7], self.raw_input[8], self.raw_input[9], self.raw_input[10]])

    def record_mode(self):
        pass
        # enemy = get_object_per_team(self.team)

        # if game.record_input:
        #     if enemy.inputdevice.inter_press:
        #         self.recorded_inputs[-1][1] = enemy.inputdevice.last_input_timer

        #         self.recorded_inputs += [[enemy.inputdevice.raw_input, 0]]

        # if game.reproduce_input:
        #     self.record_timer += 1
        #     self.raw_input = self.recorded_inputs[self.recorded_inputs_index][0]

        #     self.get_press([[self.raw_input[0]+self.raw_input[1]*-1, self.raw_input[2]+self.raw_input[3]*-1], self.raw_input[4],
        #                     self.raw_input[5], self.raw_input[6], self.raw_input[7], self.raw_input[8], self.raw_input[9], self.raw_input[10]])

        #     if self.record_timer >= self.recorded_inputs[self.recorded_inputs_index][1]:
        #         self.recorded_inputs_index += 1
        #         self.record_timer = 0
        #         if self.recorded_inputs_index >= len(self.recorded_inputs):
        #             self.recorded_inputs_index = 0
        # else:
        #     self.raw_input = [[0, 0], 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #     self.get_press(self.raw_input)

    def none_mode(self):
        self.raw_input = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.get_press([[0, 0], 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def random_mode(self):
        self.rand_timer -= 1
        if self.rand_timer <= 0:
            self.rand_timer = uniform(*(10, 60))
            self.raw_input = [choice([0, 1]) for _ in range(11)]

        self.get_press([[self.raw_input[0]+self.raw_input[1]*-1, self.raw_input[2]+self.raw_input[3]*-1], self.raw_input[4],
                        self.raw_input[5], self.raw_input[6], self.raw_input[7], self.raw_input[8], self.raw_input[9], self.raw_input[10]])

    def get_press(self, raw_input):
        # ↙↓↘←•→↖↑↗
        self.inter_press = 0
        self.current_input.clear()

        self.current_input = [[['8', '2', '5'], ['9', '3', '6'], ['7', '1', '4']][raw_input[0][0]][raw_input[0][1]-1]] + [('0', 'p_b1', 'p_b2', 'p_b3', 'p_b4', 'p_b5', 'p_b6', "p_b7")[ind]for ind in range(1, len(raw_input))if (raw_input[ind] == 1 and self.last_input[ind] == 0)
                                                                                                                          ] + [('0', 'r_b1', 'r_b2', 'r_b3', 'r_b4', 'r_b5', 'r_b6', "r_b7")[ind]for ind in range(1, len(raw_input))if (raw_input[ind] == 0 and self.last_input[ind] == 1)
                                                                                                                               ] + [('0', 'h_b1', 'h_b2', 'h_b3', 'h_b4', 'h_b5', 'h_b6', "h_b7")[ind]for ind in range(1, len(raw_input))if (raw_input[ind] == 1 and self.last_input[ind] == 1)]

        # for n, c in enumerate(current_input):
        #     self.press_charge[n] = (self.press_charge[n]+1 if self.press_charge[n] <
        #                             255 else 255)if ((c and c != -1) and c == self.last_input[n])else 0

        if raw_input != self.last_input:
            self.inter_press, self.current_input = 1, self.current_input + \
                [str([['8', '2', '5'], ['9', '3', '6'], ['7', '1', '4']][self.last_input[0]
                     [0]][self.last_input[0][1]-1])+str(self.current_input[0])]
            if len(self.press_list_showed) > 20:
                self.press_list_showed.pop(0)
            self.press_list_showed.append(list(self.current_input))
            self.last_input_timer = self.input_timer
            self.input_timer = 0

        self.last_input = raw_input

        self.input_timer += 1

    def update(self, *args):
        self.mode()

    def draw(self, screen, pos, *args):

        for index in range(len(self.press_list_showed)):
            turn = 0
            for input in self.press_list_showed[index]:
                object_image(self, 'reencor/'+input)

                screen.draw_texture(self.image, (pos[0]+(-600 if self.team == 1 else 575)+25*turn*(
                    1 if self.team == 1 else -1), pos[1]+260-25*(index), -10), [self.real_image_size[0]/2, self.real_image_size[1]/2])
                turn += 1

        # self.screen.draw_texture(self.surface,(0 if self.team==1 else 880,0),(20,20))
