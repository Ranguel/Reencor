from engine.physics.box_collisions import calculate_boxes_collisions


class GameLoop:
    def __init__(self, app):
        self.app = app
        self.frame_count = 0

    def process_input(self):
        for device in self.app.input_device_list:
            device.update()

    def update_objects(self):
        for obj in self.app.object_list:
            obj.update(self.app.renderer.camera.next_position)

    def handle_collisions(self):
        calculate_boxes_collisions(self.app)

    def handle_logic_events(self):
        for event in self.app.logic_events:
            self.process_logic_event(event)
        self.app.logic_events.clear()

    def process_logic_event(self, event):
        if event["tipe"] == "attack":
            for agent in event["agents"]:
                device = agent["object"].input_device
                if device:
                    parent = agent["object"].parent
                    target = parent if parent else agent["object"]
                    reward = agent["reward"]
                    # device.give_reward(reward, label="hitbox " + str(event["result"]))

    def update_camera(self):
        self.app.renderer.camera.update()
        self.app.renderer.camera.get_focus_point(
            self.app.active_players, self.app.active_stages
        )

    def step(self):
        self.frame_count += 1

        self.process_input()
        self.update_objects()
        self.handle_collisions()
        self.update_camera()
        self.handle_logic_events()
