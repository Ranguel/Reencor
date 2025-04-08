from Util.Active_Objects import StageActiveObject, CharacterActiveObject, ProjectileActiveObject, reset_CharacterActiveObject
from Util.Object_functions import image_dict, sound_dict, object_dict, object_list, function_dict, get_state, draw_string, update_display_shake
from Util.Interface_objects import Menu_Item, Menu_Item_String, Menu_Selector, Menu_Cursor, Menu_Deck, Combo_Counter, Gauge_Bar
from Util.boxes_collitions import box_collide, calculate_boxes_collitions, draw_boxes


class TitleScreen():
	def __init__(self, game, object_list=[]):
		object_list.append(0)

	def loop(self):
		pass


class ModeSelectionScreen():
	def __init__(self, game):
		pass

	def loop(self):
		pass


class MultiPlayerCharacterSelectionScreen():
	def __init__(self, game):
		self.game = game
		self.selection_timer = 60
		self.character_found = [key for key in object_dict.keys(
		)if object_dict[key]['tipe'] == 'character']*5
		self.menu_character = [Menu_Item(self.character_found[index], (200+(index-int(index/6)*6)*125+(int(int(
			index/6) % 2 == 0)*20), 20+int(index/6)*105, 0), (120, 100))for index in range(len(self.character_found))]
		self.menu_selectors = [Menu_Selector(
			game.input_device_list[ind], self.menu_character, ind) for ind in range(len(game.input_device_list))]
		self.add_object = self.menu_character + self.menu_selectors

		for ob in self.add_object:
			object_list.append(ob)

	def __loop__(self):
		if not (None in [selected.selected_name for selected in self.menu_selectors]):
			self.selection_timer -= 1
			if self.selection_timer == 0:
				self.game.active = False
		else:
			self.selection_timer = 60

	def __dein__(self):
		self.game.selected_characters = [
			selected.selected_name for selected in self.menu_selectors]
		self.game.selected_stage = ['SF3/Castle']


class SinglePlayerCharacterSelectionScreen():
	def __init__(self, game):
		game.camera_focus_point = [0, 0, -400]
		self.game = game

		self.character_found = [key for key in object_dict.keys(
		)if object_dict[key]['tipe'] == 'character']*5
		self.menu_character = [Menu_Item(self.character_found[index], (360+(index-int(index/4)*4)*145+(int(int(
			index/6) % 2 == 0)*20), 40+int(index/4)*115, 0), (140, 110))for index in range(len(self.character_found))]
		self.menu_selectors = [Menu_Selector(
			ind+1, game.input_device_list[ind], self.menu_character, ind) for ind in range(len(game.input_device_list))]
		self.dummy_list = [CharacterActiveObject(
			ind+1, game.input_device_list[-1], self.character_found[0], (0, 0, 0), 1, ind+1) for ind in range(len(game.input_device_list))]
		self.dummy_list[0].other_main_object = self.dummy_list[1]
		self.dummy_list[1].other_main_object = self.dummy_list[0]

		self.selection_timer = 60

	def __loop__(self):
		for character in self.menu_character:
			character.update(self.game.camera_focus_point)
			character.draw(self.game.screen, self.game.camera.pos)
		for selector in self.menu_selectors:
			selector.update(self.game.camera_focus_point)
			selector.draw(self.game.screen, self.game.camera.pos)
			if selector.index_int:
				reset_CharacterActiveObject(self.dummy_list[selector.team-1], selector.team,
											selector.menu[selector.selected_index].name, (0, 0, 0), 1 if selector.team == 1 else -1, 0, 'Stand')
			if selector.selected and selector.select_int == 1:
				get_state(self.dummy_list[selector.team-1], {'Victory': 2})
			if selector.select_int == -1:
				get_state(self.dummy_list[selector.team-1], {'Stand': 2})
		for dummy in self.dummy_list:
			dummy.update(self.game.camera_focus_point)
			dummy.fet = 'grounded'
			dummy.pos = [-500, 140, 50] if dummy.team == 1 else [500, 140, 50]
			dummy.draw(self.game.screen, self.game.camera.pos)

		if self.menu_selectors[0].selected and self.menu_selectors[0].select_int == 1:
			self.menu_selectors[1].inputdevice = self.game.input_device_list[0]
			self.menu_selectors[0].inputdevice = self.game.input_device_list[1]
		if self.menu_selectors[1].selected == False and self.menu_selectors[1].select_int == -1:
			self.menu_selectors[1].inputdevice = self.game.input_device_list[1]
			self.menu_selectors[0].inputdevice = self.game.input_device_list[0]
			self.menu_selectors[0].on_deselection(
			), self.menu_selectors[1].on_deselection()

		if not (None in [selected.selected_name for selected in self.menu_selectors]):
			self.selection_timer -= 1
			if self.selection_timer == 0:
				self.game.active = False
		else:
			self.selection_timer = 120

	def __dein__(self):
		self.game.selected_characters = [
			selected.selected_name for selected in self.menu_selectors]
		self.game.selected_stage = ['Reencor/Training']


class TrainingScreen():
	def __init__(self, game):
		self.game = game
		self.add_object = [StageActiveObject(game.selected_stage[0]), CharacterActiveObject(1, game.input_device_list[0], game.selected_characters[0], (0, 800), 1, 0), CharacterActiveObject(
			2, game.input_device_list[1], game.selected_characters[1], (300, 800), -1, 1), Combo_Counter(1), Combo_Counter(2), Gauge_Bar(1, 'health'), Gauge_Bar(1, 'pressure'), Gauge_Bar(2, 'health'), Gauge_Bar(2, 'pressure')]
		for ob in self.add_object:
			object_list.append(ob)

	def __loop__(self):
		self.game.gameplay()

	def __dein__(self):
		pass


class EditScreen():
	def __init__(self, game):
		self.game = game
		self.game.selected_characters = ['terry SVS', 'ryu SF3']
		self.game.selected_stage = ['grid stage']
		self.game.camera_focus_point = (0, 600, -250)
		self.add_object = [StageActiveObject(game.selected_stage[0]), CharacterActiveObject(1, game.input_device_list[1], game.selected_characters[0], (0, 800), 1, 0), CharacterActiveObject(
			2, game.input_device_list[1], game.selected_characters[1], (300, 800), -1, 1), Combo_Counter(1), Combo_Counter(2), Gauge_Bar(1, 'health'), Gauge_Bar(1, 'pressure'), Gauge_Bar(2, 'health'), Gauge_Bar(2, 'pressure')]
		
		for ob in self.add_object:
			object_list.append(ob)
		for object in object_list:
			object.update(self.game.camera_focus_point)

		self.draw_boxes = True
		self.move_index, self.current_frame = 0, 0
		self.cursor=Menu_Cursor(object_list[2])
		
		box_tipes={'hurtbox':self.cursor.change_box_tipe,'hitbox':self.cursor.change_box_tipe,'takebox':self.cursor.change_box_tipe,'grabox':self.cursor.change_box_tipe,'pushbox':self.cursor.change_box_tipe,'triggerbox':self.cursor.change_box_tipe,'boundingbox':self.cursor.change_box_tipe}
		self.boxes_menu=[Menu_Item_String(tipe,(20,20+index*40, 10),(1, 1),box_tipes[tipe],tipe) for index,tipe in enumerate(box_tipes)]
		
		actions={'New boxes':[self.cursor.new_boxes, None],'Save boxes':[self.cursor.save_boxes, None],'Character':[self.game.next_screen, [SinglePlayerCharacterSelectionScreen]],'Mode':[self.game.next_screen, [ModeSelectionScreen]]}
		self.action_menu=[Menu_Item_String(tipe,(20,20+index*40, 10),(1, 1),actions[tipe][0], actions[tipe][1]) for index,tipe in enumerate(actions)]
		
		self.value_menu=[Menu_Item_String(tipe,(20,20+index*40, 10),(1,1)) for index,tipe in enumerate(function_dict)]
		
	def __loop__(self):
		
		for boxes in self.boxes_menu:
			boxes.update(self.game.camera_focus_point)
			boxes.draw(self.game.screen, self.game.camera.pos)

		for action in self.action_menu:
			action.update(self.game.camera_focus_point)
			action.draw(self.game.screen, self.game.camera.pos)
		
		for value in self.value_menu:
			value.update(self.game.camera_focus_point)
			value.draw(self.game.screen, self.game.camera.pos)


		if self.game.input_device_list[0].current_input[0] == '2' and self.game.input_device_list[0].inter_press:
			self.move_index = self.move_index + \
				1 if self.move_index < len(
					list(object_dict[object_list[1].name]['moveset']))-1 else 0
			get_state(object_list[1], {
					  list(object_dict[object_list[1].name]['moveset'])[self.move_index]: 1}, 1)
			for object in object_list[1:]:
				object.update()
			self.current_frame = 0
		elif self.game.input_device_list[0].current_input[0] == '8' and self.game.input_device_list[0].inter_press:
			self.move_index = len(list(
				object_dict[object_list[1].name]['moveset']))-1 if self.move_index < 1 else self.move_index-1
			get_state(object_list[1], {
					  list(object_dict[object_list[1].name]['moveset'])[self.move_index]: 1}, 1)
			for object in object_list[1:]:
				object.update()
			self.current_frame = 0

		if self.game.input_device_list[0].current_input[0] == '4' and self.game.input_device_list[0].inter_press:
			self.current_frame = self.current_frame+1 if self.current_frame < len(
				object_dict[object_list[1].name]['moveset'][object_list[1].current_state]['framedata'])-1 else 0
			object_list[1].frame = [self.current_frame, 0]
			for object in object_list[1:]:
				object.update()
		elif self.game.input_device_list[0].current_input[0] == '6' and self.game.input_device_list[0].inter_press:
			self.current_frame = len(object_dict[object_list[1].name]['moveset'][object_list[1].current_state]
									 ['framedata'])-1 if self.current_frame < 1 else self.current_frame-1
			object_list[1].frame = [self.current_frame, 0]
			for object in object_list[1:]:
				object.update()

		object_list[1].pos, object_list[1].speed[0], object_list[2].pos = [
			0, 800, 0], 0, [4000, 600, 0]

		draw_string(self.game.screen, 'State: ' +
					str(object_list[1].current_state), (-200, 380, 10), (1, 1), (0, 0, 0, 255))
		draw_string(self.game.screen, 'Substate: ' +
					str(object_list[1].frame[0]), (-200, 400, 10), (1, 1), (0, 0, 0, 255))
		draw_string(self.game.screen, 'Sprite: '+str(object_dict[object_list[1].name]['moveset'][object_list[1].current_state]
					['framedata'][-object_list[1].frame[0]-1].get('sprite', 'NONE')), (-200, 420, 10), (1, 1), (0, 0, 0, 255))

		for object in object_list:
			update_display_shake(object)
			object.draw(self.game.screen, self.game.camera.pos)
			if self.draw_boxes:
				draw_boxes(self.game, object)

	def __dein__(self):
		pass


class DebuggingScreen():
	def __init__(self, game):
		self.game = game

		self.game.selected_characters = ['SF3/Ken', 'SF3/Ryu']
		self.game.selected_stage = ['Reencor/Training']

		self.add_object = [StageActiveObject(game.selected_stage[0]), CharacterActiveObject(1, game.input_device_list[0], game.selected_characters[0], (0, 800), 1, 0), CharacterActiveObject(
			2, game.input_device_list[1], game.selected_characters[1], (300, 800), -1, 1), Combo_Counter(1), Combo_Counter(2), Gauge_Bar(1, 'health'), Gauge_Bar(1, 'pressure'), Gauge_Bar(2, 'health'), Gauge_Bar(2, 'pressure')]
		for ob in self.add_object:
			object_list.append(ob)

	def __loop__(self):
		self.game.gameplay()

	def __dein__(self):
		pass
