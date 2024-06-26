import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from typing import Callable, Literal
from uuid import UUID, uuid4

import flet
from flet.fastapi.flet_fastapi import FastAPI

from .custom_controls import EditableDisplayText
from .routing import RouteManager

logging.basicConfig(level=logging.INFO)

ALPHABETS_WITH_SPACE_RE = r"[a-zA-Z ]"
DECIMALS_RE = r"[0-9.]"


class RecordTile(flet.Stack):
    def __init__(
        self,
        view,
        type: Literal["Credit", "Debit"],
        title: str,
        description: str,
        amount: Decimal,
    ):
        super().__init__()
        self.view = view
        self._type: Literal["Credit"] | Literal["Debit"] = type

        self.title: str = title
        self._titleText = flet.Text(
            value=self.title,
            theme_style=flet.TextThemeStyle.BODY_LARGE,
            no_wrap=True,
        )
        self.titleText = EditableDisplayText(
            obj=self,
            value_attribute="title",
            field_size=15,
            text=self._titleText,
            field=flet.TextField(
                autofocus=True,
                input_filter=flet.InputFilter(ALPHABETS_WITH_SPACE_RE),
            ),
            wrapper=flet.Container(
                padding=5,
                border_radius=5,
                bgcolor=flet.colors.SECONDARY_CONTAINER,
                expand=False,
            ),
        )

        self.description: str = description
        self._descriptionText = flet.Text(
            theme_style=flet.TextThemeStyle.BODY_MEDIUM,
            no_wrap=False,
            color=flet.colors.ON_TERTIARY_CONTAINER,
        )
        self.descriptionText = EditableDisplayText(
            obj=self,
            value_attribute="description",
            field_size=12,
            text=self._descriptionText,
            field=flet.TextField(multiline=True, autofocus=True),
            wrapper=flet.Container(expand=True),
        )

        self.dateCreated: datetime = datetime.now()
        self.dateCreatedText = flet.Text(str(self.dateCreated))

        self.amountText = flet.Text("Amount: ", color=flet.colors.ON_TERTIARY_CONTAINER)
        self.amount: Decimal = amount

        self.lastUpdated: datetime = self.dateCreated
        self.lastUpdatedText = flet.Text(
            "Last Updated:" + str(self.lastUpdated),
            color=flet.colors.ON_TERTIARY_CONTAINER,
        )

        self.card = flet.Card(
            flet.Column(
                [
                    flet.Column([self.titleText], tight=True),
                    flet.Container(
                        flet.Row(
                            [
                                flet.Column(
                                    [self.descriptionText],
                                    alignment=flet.MainAxisAlignment.CENTER,
                                    horizontal_alignment=flet.CrossAxisAlignment.CENTER,
                                    scroll=flet.ScrollMode.ALWAYS,
                                    expand=True,
                                ),
                                flet.VerticalDivider(),
                                flet.Column(
                                    [self.amountText],  # , self.lastUpdatedText],
                                    alignment=flet.MainAxisAlignment.CENTER,
                                    horizontal_alignment=flet.CrossAxisAlignment.CENTER,
                                    expand=True,
                                ),
                            ]
                        ),
                        bgcolor=flet.colors.TERTIARY_CONTAINER,
                        padding=10,
                        margin=5,
                        height=80,
                        border_radius=10,
                    ),
                ],
                spacing=0,
            ),
            margin=10,
            height=165,
        )

        self.controls = [
            flet.TransparentPointer(self.card),
            flet.TransparentPointer(
                flet.Container(
                    content=flet.FloatingActionButton(
                        icon=flet.icons.DELETE,
                        mini=True,
                        on_click=lambda e: self.page.run_task(self.remove_self, e),
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
                    height=168,
                )
            ),
        ]

        if self._type == "Credit":
            self.card.color = "#78d679"
        else:
            self.card.color = "#ff8597"

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, val: Decimal):
        if not hasattr(self, "_amount"):
            self._amount = Decimal(0)
        if self._type == "Credit":
            self.view.parent_tile.money_they_owe -= self._amount
            self.view.parent_tile.money_they_owe += val
        elif self._type == "Debit":
            self.view.parent_tile.money_you_owe -= self._amount
            self.view.parent_tile.money_you_owe += val
        self._amount: Decimal = val
        self.amountText.value = "Amount: " + str(self._amount)
        if self.page:
            self.view.parent_tile.update()
            self.page.update()

    @property
    def dateCreated(self):
        return self._dateCreated

    @dateCreated.setter
    def dateCreated(self, val: datetime):
        self._dateCreated = val
        if hasattr(self, "dateCreatedText"):
            self.dateCreatedTex.valuet = str(val)
        self.view.parent_tile.lastTransaction = val

    async def remove_self(self, e):
        self.amount = 0
        await self.parent.remove_record(self)


class RecordList(flet.ListView):
    def __init__(self, parent):
        super().__init__(spacing=20, padding=10, expand=True)
        self.parent = parent
        # self.controls.append(
        #     RecordTile(
        #         self.parent,
        #         "Credit",
        #         "Test",
        #         "Another TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother TestAnother Test",
        #         Decimal("69.69"),
        #     )
        # )
        # self.controls.append(
        #     RecordTile(self.parent, "Debit", "Test", "Another Test", Decimal("69.69"))
        # )

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
    async def add_record(
        self,
        type: Literal["Credit", "Debit"],
        title: str,
        description: str,
        amount: Decimal,
    ):
        self.auto_scroll = True
        tile = RecordTile(self.parent, type, title, description, amount)
        self.controls.append(tile)
        self.parent.update()
        self.auto_scroll = False
        await asyncio.sleep(0.25)

    @loading_animation
    async def remove_record(self, tile: RecordTile):
        self.controls.remove(tile)
        del tile
        self.parent.update()
        await asyncio.sleep(0.25)


class RecordView(flet.View):
    def __init__(
        self,
        parent_tile,
        route: str | None = None,
        appbar: flet.AppBar | flet.CupertinoAppBar | None = None,
        **kwargs,
    ):
        super().__init__(
            route=route,
            appbar=appbar,
            vertical_alignment=flet.MainAxisAlignment.END,
            padding=5,
            **kwargs,
        )

        self.parent_tile = parent_tile

        self.records = RecordList(self)
        self.credit_button = flet.ElevatedButton(
            "Credit",
            color=flet.colors.BLACK,
            bgcolor="#78d679",
            style=flet.ButtonStyle(shape=flet.RoundedRectangleBorder(radius=10)),
            on_click=self.add_credit,
            expand=True,
        )
        self.debit_button = flet.ElevatedButton(
            "Debit",
            color=flet.colors.BLACK,
            bgcolor="#ff8597",
            style=flet.ButtonStyle(shape=flet.RoundedRectangleBorder(radius=10)),
            on_click=self.add_debit,
            expand=True,
        )

        self.controls = [
            self.records,
            flet.Container(
                content=flet.Row(
                    [
                        self.credit_button,
                        self.debit_button,
                    ],
                ),
                bgcolor=flet.colors.SECONDARY_CONTAINER,
                padding=10,
                height=50,
                border_radius=20,
            ),
        ]

    def add_credit(self, e):
        title = flet.TextField(
            autofocus=True,
            input_filter=flet.InputFilter(ALPHABETS_WITH_SPACE_RE),
            label="Title",
        )
        description = flet.TextField(
            autofocus=True,
            multiline=True,
            label="Description",
        )
        amount = flet.TextField(
            autofocus=True, input_filter=flet.InputFilter(DECIMALS_RE), label="Amount"
        )

        async def credit(e):
            if all(
                (
                    i := title.value.strip(),
                    j := description.value.strip(),
                    k := amount.value.strip(),
                )
            ):
                self.page.close_dialog()
                await self.records.add_record(
                    type="Credit", title=i, description=j, amount=Decimal(k)
                )

        dlg_modal = flet.AlertDialog(
            title=flet.Text("Enter Details for Credit"),
            content=flet.Column([title, description, amount], tight=True),
            actions=[flet.TextButton("Confirm", on_click=credit)],
            actions_alignment=flet.MainAxisAlignment.END,
            open=True,
        )
        self.page.dialog = dlg_modal
        self.page.update()

    def add_debit(self, e):
        title = flet.TextField(
            autofocus=True,
            input_filter=flet.InputFilter(ALPHABETS_WITH_SPACE_RE),
            label="Title",
        )
        description = flet.TextField(
            autofocus=True,
            multiline=True,
            label="Description",
        )
        amount = flet.TextField(
            autofocus=True, input_filter=flet.InputFilter(DECIMALS_RE), label="Amount"
        )

        async def debit(e):
            if all(
                (
                    i := title.value.strip(),
                    j := description.value.strip(),
                    k := amount.value.strip(),
                )
            ):
                self.page.close_dialog()
                await self.records.add_record(
                    type="Debit", title=i, description=j, amount=Decimal(k)
                )

        dlg_modal = flet.AlertDialog(
            title=flet.Text("Enter Details for Debit"),
            content=flet.Column([title, description, amount], tight=True),
            actions=[flet.TextButton("Confirm", on_click=debit)],
            actions_alignment=flet.MainAxisAlignment.END,
            open=True,
        )
        self.page.dialog = dlg_modal
        self.page.update()


class NameTile(flet.Card):
    def __init__(self, name="Anon"):
        super().__init__(color=flet.colors.ON_INVERSE_SURFACE)
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
        self._nameTitle = flet.Text(
            value=self.name,
            theme_style=flet.TextThemeStyle.TITLE_LARGE,
            no_wrap=True,
        )
        self.nameText = EditableDisplayText(
            obj=self,
            value_attribute="name",
            field_size=22,
            text=self._nameTitle,
            field=flet.TextField(
                autofocus=True,
                input_filter=flet.InputFilter(ALPHABETS_WITH_SPACE_RE),
            ),
            wrapper=flet.Container(
                padding=flet.padding.only(left=35), alignment=flet.alignment.center
            ),
        )

        self.lastTransaction: datetime | int = 0
        self.lastTransactionText = flet.Text(
            "Last Transaction: " + str(self.lastTransaction),
            color=flet.colors.ON_SECONDARY_CONTAINER,
        )

        self.transactionSummary = flet.Container(
            content=flet.Column(
                [
                    # flet.Text(
                    #     "Last Updated:" + str(0),
                    #     color=flet.colors.ON_SECONDARY_CONTAINER,
                    # ),
                    self.lastTransactionText,
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
                    flet.Text(color="#ff8597", italic=True),  # You Owe Them
                    flet.Text(color="#78d679", italic=True),  # They Owe You
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
                flet.Divider(
                    color=flet.colors.WHITE, leading_indent=10, trailing_indent=10
                ),
                self.transactionSummary,
                self.debtSummary,
                flet.Divider(
                    color=flet.colors.WHITE, leading_indent=10, trailing_indent=10
                ),
                self.deleteButton,
            ]
        )

        self.view = RecordView(
            self,
            "/" + str(self.id),
            appbar=flet.AppBar(
                title=flet.Text(self.name, weight=flet.FontWeight.BOLD),
                color=flet.colors.BLACK,
                bgcolor=flet.colors.SECONDARY_CONTAINER,
            ),
            bgcolor=flet.colors.BACKGROUND,
        )

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        self._name: str = val
        if hasattr(self, "view"):
            self.view.appbar.title.value = val

    @property
    def lastTransaction(self) -> datetime | int:
        return self._lastTransaction

    @lastTransaction.setter
    def lastTransaction(self, val: datetime | int):
        self._lastTransaction = val
        if hasattr(self, "lastTransactionText"):
            self.lastTransactionText.value = "Last Transaction: " + str(val)

    @property
    def money_you_owe(self) -> Decimal:
        return self._money_you_owe

    @money_you_owe.setter
    def money_you_owe(self, val: Decimal):
        if not hasattr(self, "_money_you_owe"):
            self._money_you_owe = Decimal(0)
        if not hasattr(self, "_money_they_owe"):
            self._money_they_owe = Decimal(0)
        self._money_you_owe: Decimal = val
        self.net_owed = self._money_you_owe - self._money_they_owe
        self.debtSummary.content.controls[0].value = "Money You Owe Them: " + str(val)
        self.debtSummary.content.controls[2].value = "Net Amount Owed: " + str(
            self.net_owed
        )

    @property
    def money_they_owe(self) -> Decimal:
        return self._money_they_owe

    @money_they_owe.setter
    def money_they_owe(self, val: Decimal):
        if not hasattr(self, "_money_you_owe"):
            self._money_you_owe = Decimal(0)
        if not hasattr(self, "_money_they_owe"):
            self._money_they_owe = Decimal(0)
        self._money_they_owe: Decimal = val
        self.net_owed = self._money_you_owe - self._money_they_owe
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

        # tile = NameTile("HehE")
        # self.controls.append(tile)
        # self.route_manager.add_route(tile.view.route, tile.view)

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
    def __init__(
        self, route: str, route_manager: RouteManager, appbar: flet.AppBar, **kwargs
    ):
        super().__init__(route=route, appbar=appbar, **kwargs)

        self.floating_action_button = flet.FloatingActionButton(
            icon=flet.icons.ADD,
            on_click=self.add_name,
            bgcolor=flet.colors.SECONDARY_CONTAINER,
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
    custom_color_scheme = flet.ColorScheme(
        primary_container="#9290c3",
        secondary_container="#535c91",
        tertiary_container="#2c2a45",
        background="#070f2b",
        on_inverse_surface="#1b1a55",
    )
    page.theme = flet.Theme(color_scheme=custom_color_scheme)
    test_view = NameView(
        "/",
        route_manager,
        flet.AppBar(
            leading=flet.Image(
                "icon.png",
                fit=flet.ImageFit.SCALE_DOWN,
                filter_quality=flet.FilterQuality.HIGH,
            ),
            title=flet.Text("SettleUp", weight=flet.FontWeight.BOLD),
            center_title=True,
            color=flet.colors.BLACK,
            bgcolor=flet.colors.SECONDARY_CONTAINER,
        ),
        bgcolor=flet.colors.BACKGROUND,
    )
    page.views.clear()
    page.on_route_change = test_view.route_manager.on_route_change
    page.on_view_pop = test_view.route_manager.on_view_pop
    page.go(page.route)


app: FastAPI | None = flet.app(main, assets_dir="dt/assets")
