import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Callable, Literal
from uuid import UUID, uuid4

import flet
from flet.fastapi.flet_fastapi import FastAPI

from .custom_controls import EditableDisplayText, FixedPane, VerticalSplitter
from .routing import RouteManager

logging.basicConfig(level=logging.DEBUG)

ALPHABETS_WITH_SPACE_RE = r"[a-zA-Z ]"
DECIMALS_RE = r"[0-9.]"


class RecordTile(flet.Stack):
    def __init__(self, type: Literal["Credit", "Debit"], title: str, description: str):
        super().__init__()
        self.type: Literal["Credit"] | Literal["Debit"] = type

        self.title: str = title
        self.titleText = EditableDisplayText(
            self,
            "title",
            text_theme_style=flet.TextThemeStyle.BODY_LARGE,
            field_size=15,
            no_wrap=True,
            input_filter=flet.InputFilter(ALPHABETS_WITH_SPACE_RE),
        )

        self.description: str = description
        self.descriptionText = EditableDisplayText(
            self,
            "description",
            text_theme_style=flet.TextThemeStyle.BODY_MEDIUM,
            field_size=12,
            no_wrap=True,
        )

        self.dateCreated: datetime = datetime.now()
        self.dateCreatedText = flet.Text(str(self.dateCreated))

        self.lastUpdated: datetime = self.dateCreated
        self.lastUpdatedText = flet.Text("Last Updated:" + str(self.lastUpdated))

        self.amount = Decimal(0)
        self.amountText = flet.Text("Amount: " + str(self.amount))

        self.card = flet.Card(
            flet.Column(
                [
                    self.titleText,
                    flet.Container(
                        VerticalSplitter(
                            left_pane=self.descriptionText,
                            right_pane=flet.Column(
                                [self.amountText, self.lastUpdatedText],
                                alignment=flet.MainAxisAlignment.CENTER,
                                horizontal_alignment=flet.CrossAxisAlignment.CENTER,
                                expand=True,
                            ),
                            fixed_pane=FixedPane.RIGHT,
                            height=80,
                            fixed_pane_min_width=80,
                        ),
                        bgcolor=flet.colors.TERTIARY_CONTAINER,
                        padding=10,
                        margin=5,
                        border_radius=10,
                    ),
                ],
                spacing=0,
            ),
            margin=10,
        )

        self.controls = [
            flet.TransparentPointer(self.card),
            flet.TransparentPointer(
                flet.Container(
                    content=flet.FloatingActionButton(
                        icon=flet.icons.DELETE, mini=True
                    ),
                    alignment=flet.alignment.top_left,
                    expand=True,
                    height=170,
                )
            ),
            flet.TransparentPointer(
                flet.Container(
                    content=flet.Container(
                        self.dateCreatedText,
                        bgcolor=flet.colors.PRIMARY_CONTAINER,
                        padding=5,
                        border_radius=10,
                    ),
                    alignment=flet.alignment.bottom_left,
                    expand=True,
                    # bgcolor=flet.colors.YELLOW,
                    height=168,
                )
            ),
        ]

        if self.type == "Credit":
            self.card.color = flet.colors.GREEN_600
        else:
            self.card.color = flet.colors.RED_600


class RecordList(flet.ListView):
    def __init__(self):
        super().__init__(spacing=20, padding=10, expand=True)
        self.controls.append(RecordTile("Credit", "Test", "Another Test"))
        self.controls.append(RecordTile("Debit", "Test", "Another Test"))


class RecordView(flet.View):
    def __init__(
        self,
        route: str | None = None,
        appbar: flet.AppBar | flet.CupertinoAppBar | None = None,
    ):
        super().__init__(
            route=route,
            appbar=appbar,
            vertical_alignment=flet.MainAxisAlignment.END,
            padding=5,
        )

        self.list = RecordList()
        self.credit_button = flet.ElevatedButton(
            "Credit",
            color=flet.colors.BLACK,
            bgcolor=flet.colors.GREEN_ACCENT,
            style=flet.ButtonStyle(shape=flet.RoundedRectangleBorder(radius=10)),
            on_click=self.add_credit,
            expand=True,
        )
        self.debit_button = flet.ElevatedButton(
            "Debit",
            color=flet.colors.BLACK,
            bgcolor=flet.colors.RED_ACCENT,
            style=flet.ButtonStyle(shape=flet.RoundedRectangleBorder(radius=10)),
            expand=True,
        )

        self.controls = [
            self.list,
            flet.Container(
                content=flet.Row(
                    [
                        self.credit_button,
                        self.debit_button,
                    ],
                ),
                bgcolor=flet.colors.PRIMARY_CONTAINER,
                padding=10,
                height=50,
                border_radius=20,
            ),
        ]

    def add_credit(self, e):
        description = flet.TextField(
            autofocus=True,
            input_filter=flet.InputFilter(ALPHABETS_WITH_SPACE_RE),
            label="Record Title",
        )
        amount = flet.TextField(
            autofocus=True, input_filter=flet.InputFilter(DECIMALS_RE), label="Amount"
        )

        def credit(e):
            if description.value.strip() and amount.value.strip():
                self.page.close_dialog()
            # await self.list.add_name(dlg_modal.content.value.strip())

        dlg_modal = flet.AlertDialog(
            title=flet.Text("Enter Details"),
            content=flet.Column([description, amount], tight=True),
            actions=[flet.TextButton("Confirm", on_click=credit)],
            actions_alignment=flet.MainAxisAlignment.END,
            open=True,
        )
        self.page.dialog = dlg_modal
        self.page.update()

    def add_record_debit(self, e): ...


class NameTile(flet.Card):
    def __init__(self, name="Anon"):
        super().__init__()
        self.content = flet.Container(
            flet.ResponsiveRow(
                alignment=flet.MainAxisAlignment.CENTER,
                vertical_alignment=flet.MainAxisAlignment.CENTER,
                spacing=0,
            ),
            on_click=self.show_details,
        )

        self.id: UUID = uuid4()

        self.name: str = name
        self.nameText = flet.Column(
            [
                EditableDisplayText(
                    self,
                    "name",
                    text_theme_style=flet.TextThemeStyle.TITLE_LARGE,
                    field_size=22,
                    no_wrap=True,
                    input_filter=flet.InputFilter(ALPHABETS_WITH_SPACE_RE),
                )
            ],
            alignment=flet.MainAxisAlignment.CENTER,
            horizontal_alignment=flet.CrossAxisAlignment.CENTER,
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
            margin=flet.margin.symmetric(horizontal=15),
            border_radius=5,
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
            margin=flet.margin.symmetric(horizontal=15),
            border_radius=5,
        )
        self.net_owed: Decimal = Decimal(0)
        # Sets text values in debtSummary too
        self.money_you_owe: Decimal = Decimal(0)
        self.money_they_owe: Decimal = Decimal(0)

        self.deleteButton = flet.ElevatedButton(
            "Delete",
            on_click=lambda e: self.page.run_task(self.parent.remove_name, self),
            icon=flet.icons.DELETE_FOREVER,
            bgcolor=flet.colors.TERTIARY_CONTAINER,
            color=flet.colors.ON_TERTIARY_CONTAINER,
            icon_color=flet.colors.ON_TERTIARY_CONTAINER,
            style=flet.ButtonStyle(shape=flet.ContinuousRectangleBorder(radius=10)),
        )

        self.content.content.controls.extend(
            [
                self.nameText,
                flet.Divider(leading_indent=10, trailing_indent=10),
                self.transactionSummary,
                self.debtSummary,
                flet.Divider(leading_indent=10, trailing_indent=10),
                self.deleteButton,
            ]
        )

        self.view = RecordView(
            "/" + str(self.id),
            appbar=flet.AppBar(title=flet.Text(self.name)),
        )

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        self._name: str = val
        if hasattr(self, "view"):
            self.view.appbar.title = flet.Text(val)

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
        self.page.go(f"/{self.id}")


class NameList(flet.ListView):
    def __init__(self, route_manager: RouteManager):
        super().__init__(expand=True, spacing=20)

        self.route_manager: RouteManager = route_manager

        tile = NameTile("HehE")
        self.controls.append(tile)
        self.route_manager.add_route(tile.view.route, tile.view)

    def loading_animation(func: Callable):
        async def add_loading(self, *args, **kwargs):
            self.page.overlay.append(
                flet.Container(
                    content=flet.ProgressRing(),
                    bgcolor=flet.colors.with_opacity(
                        color=flet.colors.BLACK, opacity=0.5
                    ),
                    expand=True,
                    alignment=flet.alignment.center,
                )
            )
            self.page.update()

            await func(self, *args, **kwargs)

            self.page.overlay.clear()
            self.page.update()

        return add_loading

    @loading_animation
    async def add_name(self, name: str):
        self.auto_scroll = True
        tile = NameTile(name)
        self.controls.append(tile)
        self.route_manager.add_route(tile.view.route, tile.view)
        self.parent.update()
        self.auto_scroll = False
        await asyncio.sleep(0.25)

    @loading_animation
    async def remove_name(self, tile: NameTile):
        self.controls.remove(tile)
        self.route_manager.remove_route(tile.view.route)
        del tile.view
        del tile
        self.parent.update()
        await asyncio.sleep(0.25)


class NameView(flet.View):
    def __init__(self, route: str, route_manager: RouteManager, appbar_title: str):
        super().__init__(route=route, appbar=flet.AppBar(title=flet.Text(appbar_title)))

        self.floating_action_button = flet.FloatingActionButton(
            icon=flet.icons.ADD, on_click=self.add_name
        )

        self.route_manager: RouteManager = route_manager
        self.route_manager.base_view = self
        self.list = NameList(self.route_manager)

        self.controls.append(self.list)

    async def add_name(self, e):
        async def close_dialog(e):
            if dlg_modal.content.value.strip():
                self.page.close_dialog()
                await self.list.add_name(dlg_modal.content.value.strip())

        dlg_modal = flet.AlertDialog(
            title=flet.Text("Enter Name"),
            content=flet.TextField(
                input_filter=flet.InputFilter(ALPHABETS_WITH_SPACE_RE),
                text_style=flet.TextStyle(22),
                on_submit=close_dialog,
                autofocus=True,
            ),
            actions=[flet.TextButton("Confirm", on_click=close_dialog)],
            actions_alignment=flet.MainAxisAlignment.END,
            open=True,
        )
        self.page.dialog = dlg_modal
        self.page.update()


async def main(page: flet.Page):
    page.theme_mode = flet.ThemeMode.DARK
    route_manager = RouteManager(page)
    test_view = NameView("/", route_manager, "Debt Machine")
    page.views.clear()
    page.on_route_change = test_view.route_manager.on_route_change
    page.on_view_pop = test_view.route_manager.on_view_pop
    page.go(page.route)


app: FastAPI | None = flet.app(main)
