from decimal import Decimal
from uuid import UUID, uuid4

import flet
from flet.fastapi.flet_fastapi import FastAPI

from .routing import RouteManager


class EditableText(flet.Row):
    def __init__(
        self,
        obj: flet.Control,
        value_attribute: str,
        text_theme_style: flet.TextThemeStyle,
        text_style: flet.TextStyle,
        **kwargs,
    ):
        super().__init__(alignment=flet.MainAxisAlignment.CENTER, spacing=0)

        self.obj: flet.Control = obj
        self.value_attribute: str = value_attribute

        self.label = flet.Text(
            value=getattr(self.obj, self.value_attribute, None),
            theme_style=text_theme_style,
            **kwargs,
        )
        self.entry = flet.TextField(
            value=getattr(self.obj, self.value_attribute, None),
            dense=True,
            on_submit=self.change_text,
            content_padding=0,
            text_style=text_style,
        )
        self.action_button = flet.IconButton(
            icon=flet.icons.EDIT, on_click=self.edit_text
        )
        self.controls = [self.label, self.action_button]

    def edit_text(self, e):
        self.action_button.icon = flet.icons.CHECK
        self.action_button.on_click = self.change_text
        self.controls[0] = self.entry
        self.update()

    def change_text(self, e):
        self.action_button.icon = flet.icons.EDIT
        self.action_button.on_click = self.edit_text
        self.label.value = self.entry.value.strip()
        setattr(self.obj, self.value_attribute, self.entry.value.strip())
        self.controls[0] = self.label
        self.update()


class NameTile(flet.Card):
    def __init__(self, name="Anon"):
        super().__init__()
        self.content = flet.Container(
            flet.ResponsiveRow(
                alignment=flet.MainAxisAlignment.CENTER,
                vertical_alignment=flet.MainAxisAlignment.CENTER,
            ),
            padding=10,
            on_click=self.show_details,
        )

        self.id: UUID = uuid4()

        self.name: str = name
        self.nameText = flet.Container(
            content=flet.Column(
                [
                    EditableText(
                        self,
                        "name",
                        text_theme_style=flet.TextThemeStyle.TITLE_LARGE,
                        text_style=flet.TextStyle(22.5),
                        no_wrap=True,
                    )
                ],
                alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            ),
            alignment=flet.alignment.center,
            border_radius=5,
            col={},
        )

        self.transactionSummary = flet.Container(
            content=flet.Column(
                [
                    flet.Text(
                        "Last Updated:" + str(0),
                        color=flet.colors.ON_SECONDARY_CONTAINER,
                    ),
                    flet.Text(
                        "Last Transaction:" + str(0),
                        color=flet.colors.ON_SECONDARY_CONTAINER,
                    ),
                ],
                alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            ),
            bgcolor=flet.colors.SECONDARY_CONTAINER,
            padding=10,
            border_radius=5,
            col={},
        )

        self.debtSummary = flet.Container(
            content=flet.Column(
                [
                    flet.Text(color=flet.colors.RED_ACCENT),  # You Owe Them
                    flet.Text(color=flet.colors.GREEN_ACCENT),  # They Owe You
                    flet.Text(color=flet.colors.ON_SECONDARY_CONTAINER),  # Net Owed
                ],
                alignment=flet.MainAxisAlignment.CENTER,
                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
            ),
            bgcolor=flet.colors.SECONDARY_CONTAINER,
            padding=10,
            border_radius=5,
            col={},
        )
        self.net_owed: Decimal = Decimal(0)
        # Sets text values in debtSummary too
        self.money_you_owe: Decimal = Decimal(0)
        self.money_they_owe: Decimal = Decimal(0)

        self.deleteButton = flet.ElevatedButton(
            "Delete",
            on_click=lambda e: self.parent.remove_record(self),
            icon=flet.icons.DELETE_FOREVER,
            bgcolor=flet.colors.TERTIARY_CONTAINER,
            color=flet.colors.ON_TERTIARY_CONTAINER,
            icon_color=flet.colors.ON_TERTIARY_CONTAINER,
        )

        self.content.content.controls.extend(
            [
                self.nameText,
                flet.Divider(),
                self.transactionSummary,
                self.debtSummary,
                flet.Divider(),
                self.deleteButton,
            ]
        )

        self.view = flet.View(
            "/" + str(self.id),
            [
                flet.Container(
                    flet.Text(
                        str(self.id), theme_style=flet.TextThemeStyle.TITLE_LARGE
                    ),
                    expand=True,
                    alignment=flet.alignment.center,
                )
            ],
            appbar=flet.AppBar(title=flet.Text("Debt Machine")),
            vertical_alignment=flet.MainAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
        )

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        self._name: str = val

    @property
    def money_you_owe(self) -> Decimal:
        return self._money_you_owe

    @money_you_owe.setter
    def money_you_owe(self, val: Decimal):
        if not hasattr(self, "_money_you_owe"):
            self._money_you_owe = Decimal(0)
        self.net_owed = self.net_owed - (self._money_you_owe - val)
        self._money_you_owe: Decimal = val
        self.debtSummary.content.controls[0].value = "Money You Owe Them: " + str(val)
        self.debtSummary.content.controls[2].value = "Net Amount Owed: " + str(
            self.net_owed
        )

    @property
    def money_they_owe(self) -> Decimal:
        return self._money_they_owe

    @money_they_owe.setter
    def money_they_owe(self, val: Decimal):
        if not hasattr(self, "_money_they_owe"):
            self._money_they_owe = Decimal(0)
        self.net_owed = self.net_owed + (self._money_they_owe - val)
        self._money_they_owe: Decimal = val
        self.debtSummary.content.controls[1].value = "Money They Owe You: " + str(val)
        self.debtSummary.content.controls[2].value = "Net Amount Owed: " + str(
            self.net_owed
        )

    def show_details(self, e):
        if self.page:
            self.page.go(f"/{self.id}")


class NameList(flet.ListView):
    def __init__(self, route_manager: RouteManager):
        super().__init__(expand=True, spacing=20)

        self.route_manager: RouteManager = route_manager

    def add_record(self, name: str):
        self.auto_scroll = True
        tile = NameTile(name)
        self.controls.append(tile)
        self.route_manager.add_route(tile.view.route, tile.view)
        if self.page:
            self.page.update()
        self.auto_scroll = False

    def remove_record(self, tile: NameTile):
        self.page.overlay.append(flet.ProgressRing())
        self.page.update()
        self.controls.remove(tile)
        self.route_manager.remove_route(tile.view.route)
        del tile.view
        del tile
        self.page.overlay.clear()
        self.page.update()


async def main(page: flet.Page):
    page.theme_mode = flet.ThemeMode.DARK
    route_manager = RouteManager(page)
    test = NameList(route_manager)
    testView = flet.View(
        "/",
        [test],
        appbar=flet.AppBar(title=flet.Text("Debt Machine")),
        floating_action_button=flet.FloatingActionButton(
            "add", on_click=lambda e: test.add_record("anon")
        ),
    )
    page.views.clear()
    route_manager.base_view = testView
    page.on_route_change = route_manager.on_route_change
    page.on_view_pop = route_manager.on_view_pop
    page.go(page.route)

    test.add_record("Anon1")


app: FastAPI | None = flet.app(main, export_asgi_app=True)
