from engine.render.camera import Camera
from engine.render.light import Light
from engine.render.shadow import ShadowMap

from engine.gameplay.team import Team
from engine.entity.base import Base
from engine.constant.entity import *
from engine.constant.ui import *
from engine.entity.actor import Actor
from engine.ui.card import Card
from engine.ui.label import Label
from engine.ui.selector import Selector
from engine.math.vector import round_sign
from engine.math.probability import weighted_choice
from engine.gameplay.object_query import get_actor_per_team


class BaseScene:
    def __init__(
        self, input=None, loop=None, renderer=None, audio=None, assets=None, **kwargs
    ):
        self.active = True
        self.events = []

        self.input = input
        self.loop = loop
        self.renderer = renderer
        self.audio = audio
        self.assets = assets
        self.prefabs = self.assets.objects

        self.selected_bases = ["Reencor/Training"]
        self.selected_actors = ["SF3/Ryu", "SF3/Ryu"]

        self.objects: list[Base, Actor, Card] = []

        self.teams: list[Team] = []

        self.actors: list[Actor] = []
        self.bases: list[Base] = []
        self.ui: list[Card] = []

        self.show_boxes = False
        self.show_inputs = False
        self.show_ui = True

        self.in_output = kwargs
        self.out_params = None

    def __loop__(self, **kwargs):
        return

    def __dein__(self, **kwargs):
        return self.out_params


class MenuScene(BaseScene):
    def __init__(
        self, input=None, loop=None, renderer=None, audio=None, assets=None, **kwargs
    ):
        super().__init__(
            input=input,
            loop=loop,
            renderer=renderer,
            audio=audio,
            assets=assets,
            **kwargs
        )

        self.load_objects(ui=self.show_ui)

    def load_objects(self, ui=False, **kwargs):
        """Load all objects for the scene."""

        self.camera = Camera(aspect=self.renderer.aspect_ratio, smoothness=0.1)
        self.light = Light(size=14)
        self.shadow = ShadowMap(ctx=self.renderer.ctx, size=1024)


class FightScene(BaseScene):
    def __init__(
        self, input=None, loop=None, renderer=None, audio=None, assets=None, **kwargs
    ):
        super().__init__(
            input=input,
            loop=loop,
            renderer=renderer,
            audio=audio,
            assets=assets,
            **kwargs
        )

        self.load_objects(ui=self.show_ui)

    def load_objects(self, ui=False, **kwargs):
        """Load all objects for the scene, including bases, actors, and UI elements."""

        self.camera = Camera(aspect=self.renderer.aspect_ratio, smoothness=0.1)
        self.light = Light(size=14)
        self.shadow = ShadowMap(ctx=self.renderer.ctx, size=1024)

        # Load static objects first, as they may be needed for actor initialization

        for name in self.selected_bases:
            base = Base(
                dict=self.prefabs[name],
                state="idle",
            )

            self.objects.append(base)
            self.bases.append(base)

        self.wall = Base(
            dict=self.prefabs["Reencor/Walls"],
            state="idle",
        )
        self.objects.append(self.wall)
        self.bases.append(self.wall)

        # Load Teams and Actors next, as they may be needed for UI initialization

        for index, name in enumerate(self.selected_actors):
            side = ScreenSide.LEFT if index == 0 else ScreenSide.RIGHT
            actor = Actor(
                dict=self.prefabs[name],
                position=[-3 if side == ScreenSide.LEFT else 3, 0, 0],
                rotation=[0, 0 if side == ScreenSide.LEFT else 180, 0],
            )

            if index < len(self.input.devices):
                self.input.devices[index].target.append(actor)
                actor.input_device = self.input.devices[index]

            team = Team(index=index + 1, main=actor, side=side)
            actor.team = team

            self.teams.append(team)
            self.objects.append(actor)
            self.actors.append(actor)

        if not ui:
            return

        # Load UI elements last, as they may depend on teams and actors

        for team in self.teams:

            # Create combo label for each team

            label = Label(
                text="COMBO",
                font="font",
                color=(0, 0, 0, 1),
                side=team.side,
                size=0.14,
                position=[-0.9, 0.5],
                show=False,
            )

            team.labels.append(label)
            self.objects.append(label)
            self.ui.append(label)

            # Create indicator cards for each team

            for dict in team.main.dict.get("indicator", []):
                ui = Card(
                    dict=self.prefabs[dict["file"]],
                    state="idle",
                    side=team.side,
                    parent=team.main,
                )

                self.objects.append(ui)
                self.ui.append(ui)

    def face_actor_towards_update(self):
        if len(self.actors) < 2:
            return
        for team in self.teams:
            actor = team.main
            if (
                (
                    ("left" in actor.input and actor.rotation[1] == 180)
                    or ("right" in actor.input and actor.rotation[1] == 0)
                    or "down" in actor.input
                )
                and actor.input_interruption
                and actor.guard[1] == 0
            ):
                actor.guard = ["", 24]

            if actor.guard[1]:
                actor.guard[1] -= 1

            actor.rival = get_actor_per_team(self.teams, team)
            if (not actor.hitstop) and (actor.grabed is None):
                if actor.rival is not None and actor.type is EntityType.ACTOR:
                    new_face = round_sign(actor.rival.position[0] - actor.position[0])
                    if (
                        actor.grounded
                        and (
                            set(actor.cancel).intersection(["neutral"])
                            or (
                                actor.frame_index >= actor.frame_total
                                and actor.frame_counter >= actor.frame_duration
                            )
                        )
                        and new_face
                        != round_sign(-1 if actor.rotation[1] == 180 else 1)
                        and abs(actor.rival.position[0] - actor.position[0]) > 0.3
                    ):
                        actor.rotation[1] = 180 if new_face == -1 else 0
                        actor.condition.update(["turn"])
                        actor.input_interruption = 1

    def walls_update(self):
        self.wall.position = [
            self.camera.position[0],
            0,
            0,
        ]

    def __loop__(self, **kwargs):
        self.walls_update()
        self.face_actor_towards_update()


class NotALoadingScene(MenuScene):
    def __init__(self, go_to_scene=None, **kwargs):
        self.loading_time = 180
        self.messages = {
            "Fun fact: This is not a loading screen": {"chance": 1},
            "Tip: Multi-hit attacks shouldn’t always scale the combo per hit — usually per attack.": {
                "chance": 1
            },
            "Fun fact: In many classic fighting games, input is processed before animation.": {
                "chance": 1
            },
            "Tip: A good cancel system makes combat feel responsive, even with slow animations.": {
                "chance": 1
            },
            "Fun fact: Retro game text isn’t text — it’s just sprites.": {"chance": 1},
            "Tip: Separating gameplay logic from visuals prevents most hard-to-track bugs.": {
                "chance": 1
            },
            "Fun fact: Menus are scenes too.": {"chance": 1},
            "Fun fact: An AI that only reacts to hits quickly becomes predictable.": {
                "chance": 1
            },
            "Tip: Rewarding the AI only for landing hits doesn’t always lead to better decisions.": {
                "chance": 1
            },
            "Tip: Event-based logic (did_hit, did_press) is often more reliable than state polling.": {
                "chance": 1
            },
        }

        self.labels: list[Label] = []
        self.indicators: list[Card] = []

        super().__init__(**kwargs)

        self.out_params = {"next_scene": go_to_scene}

    def load_objects(self, ui=False, **kwargs):
        super().load_objects(ui, **kwargs)

        string = weighted_choice(self.messages)
        tip = Label(
            text=string,
            font="font",
            color=(1, 1, 1, 1),
            indent=Textindent.CENTER,
            size=0.1,
            position=[0, 0.7],
            max_lenght=30,
        )
        self.labels.append(tip)

        loading_indicator = Card(
            dict=self.prefabs["Reencor/Selector"], state="idle", position=[0.8, -0.8]
        )
        self.indicators.append(loading_indicator)

        self.objects.extend(self.labels)
        self.objects.extend(self.indicators)

    def __loop__(self, **kwargs):
        super().__loop__(**kwargs)
        if self.loading_time:
            self.loading_time -= 1

        if self.loading_time == 0:
            self.active = False


class ModeSelectionScene(MenuScene):
    def __init__(self, **kwargs):
        self.modes = {
            "CAMPAIGN": VersusScene,
            "VERSUS": VersusScene,
            "TRIAL": TrainingScene,
            "TRAINING": TrainingScene,
            "DEBUG": DebuggingScene,
        }

        self.items: list[Label] = []
        self.selectors: list[Selector] = []

        super().__init__(**kwargs)

    def load_objects(self, ui=False, **kwargs):
        super().load_objects(ui, **kwargs)

        for index, mode in enumerate(self.modes):
            label = Label(
                text=str(mode),
                font="font",
                color=(1, 1, 1, 1),
                size=0.16,
                position=[-0.9, 0.5 - 0.1 * index],
                function=self.modes[mode],
            )
            self.items.append(label)
            self.objects.append(label)

        for device in self.input.devices:
            selector = Selector(
                dict=self.prefabs["Reencor/Selector"],
                state="idle",
                color=[0, 0, 0, 1],
                items=self.items,
            )
            self.selectors.append(selector)
            self.objects.append(selector)
            selector.input_device = device
            device.target.append(selector)

    def __loop__(self, **kwargs):
        super().__loop__(**kwargs)

        for selector in self.selectors:
            if selector.selected != None and selector.selected_timer == 0:
                self.active = False
                self.out_params = {
                    "next_scene": NotALoadingScene,
                    "go_to_scene": selector.selected.function,
                    "last_scene": self.__class__,
                    "params": None,
                }


class VersusScene(FightScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_inputs = True

    def __loop__(self, **kwargs):
        super().__loop__(**kwargs)


class TrainingScene(FightScene):
    def __init__(self, **kwargs):
        self.values = {
            UISubtype.DAMAGE,
            UISubtype.SCALING,
            UISubtype.COMBO_DAMAGE,
        }

        super().__init__(**kwargs)

        self.show_inputs = True
        self.last_hitstun = {active_object: 0 for active_object in self.actors}
        self.recover_life = {active_object: False for active_object in self.actors}

    def load_objects(self, ui=False, **kwargs):
        super().load_objects(ui, **kwargs)

        self.camera = Camera(
            aspect=self.renderer.aspect_ratio, position=(0, 5, 0), smoothness=0.1
        )

        for team in self.teams:
            side = team.side

            for index, value in enumerate(self.values):
                label = Label(
                    text="------",
                    font="font",
                    color=(1, 1, 1, 1),
                    background=(0, 0, 0, 1),
                    size=0.06,
                    position=[0.1, 0.7 - 0.1 * index],
                    side=side,
                    subtype=value,
                )

                team.labels.append(label)
                self.objects.append(label)

    def __loop__(self, **kwargs):
        super().__loop__(**kwargs)

        for actor in self.actors:
            if actor.hitstun != 0:
                self.recover_life[actor] = False

            if self.last_hitstun[actor] != 0 and actor.hitstun == 0:
                self.recover_life[actor] = True

            if self.recover_life[actor] == True:
                actor.meters["health"] += 10
                if actor.meters["health"] >= actor.dict["meters"]["health"]["max"]:
                    actor.meters["health"] = actor.dict["meters"]["health"]["max"]
                    self.recover_life[actor] = False

            self.last_hitstun[actor] = actor.hitstun

        if 1:
            for team in self.teams:
                for label in team.labels:
                    if label.subtype == UISubtype.DAMAGE:
                        label.string_update("Damage: " + str(round(team.last_damage)))

                    if label.subtype == UISubtype.SCALING:
                        label.string_update(
                            "Scaling: " + str(round(team.damage_scaling * 100))
                        )

                    if label.subtype == UISubtype.COMBO_DAMAGE:
                        label.string_update(
                            "Combo damage: " + str(round(team.combo_damage))
                        )


class DebuggingScene(FightScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_boxes = True
        self.show_inputs = True
        self.last_hitstun = {active_object: 0 for active_object in self.actors}

    def __loop__(self, **kwargs):
        super().__loop__(**kwargs)

        for actor in self.actors:
            if self.last_hitstun[actor] != 0 and actor.hitstun == 0:
                actor.meters["health"] = actor.dict["meters"]["health"]["max"]
            self.last_hitstun[actor] = actor.hitstun
