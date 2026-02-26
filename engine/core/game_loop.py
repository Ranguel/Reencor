from engine.physics.physic_collisions import physics_collisions
from engine.gameplay.combat_collision import combat_collisions
from engine.action.frame_update import apply_pending_changes
from engine.action.frame_update import apply_frame_data


class GameLoop:
    def __init__(self):
        self.frame_count = 0
        self.triger_freeze = 0
        self.screen_freeze = 0
        self.freeze_actors = set()

    def update_objects(self, scene=None):
        if self.triger_freeze:
            self.screen_freeze = self.triger_freeze
            self.triger_freeze = 0

        for member in scene.objects:
            if member in self.freeze_actors:
                continue

            if hasattr(member, "pending_changes") and member.pending_changes:
                apply_pending_changes(self=member)

            if (
                hasattr(member, "team")
                and member.team.index == 1
                and member.state_current == "Neutral Landing"
                and 0
            ):
                print(
                    "draw: ",
                    member.draw,
                    "f count: ",
                    member.frame_counter,
                    "f ind: ",
                    member.frame_index,
                    "int: ",
                    member.frame_interruption,
                )

            member.update()

            if hasattr(member, "frame_interruption") and member.frame_interruption:
                apply_frame_data(self=member, scene=scene)

            if (
                hasattr(member, "life_time")
                and isinstance(member.life_time, int)
                and not isinstance(member.life_time, bool)
                and member.life_time <= 0
            ):
                if hasattr(member, "parent") and member.parent != None:
                    member.parent.children.remove(member)
                if hasattr(member, "team"):
                    member.team.members.remove(member)
                if member in scene.actors:
                    scene.actors.remove(member)
                if member in scene.bases:
                    scene.bases.remove(member)
                scene.objects.remove(member)

            if hasattr(member, "condition") and member.condition:
                member.condition.clear()
            if (
                hasattr(member, "input")
                and member.input
                and member.input_device is not None
            ):
                member.input.clear()
            if (
                hasattr(member, "command")
                and member.command
                and member.input_device is not None
            ):
                member.command.clear()

        if self.screen_freeze:
            self.screen_freeze -= 1
            if self.screen_freeze == 0:
                self.freeze_actors.clear()

    def handle_combat_collisions(self, scene=None):
        combat_collisions(teams=scene.teams, scene=scene)

    def handle_physics_collisions(self, scene=None):
        physics_collisions(teams=scene.teams, bases=scene.bases, scene=scene)

    def update_camera(self, scene=None):
        scene.camera.update()
        scene.camera.get_focus_point(scene.actors, scene.bases)

    def step(self, scene=None):
        self.frame_count += 1

        self.update_objects(scene=scene)
        self.handle_combat_collisions(scene=scene)
        self.handle_physics_collisions(scene=scene)
        self.update_camera(scene=scene)
