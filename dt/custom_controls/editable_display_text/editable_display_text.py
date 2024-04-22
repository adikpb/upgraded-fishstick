from typing import Any, Dict, Tuple

import flet


class EditableDisplayText(flet.Row):
    def __init__(
        self,
        obj: flet.Control,
        value_attribute: str,
        field_size: float,
        text: flet.Text,
        field: flet.TextField,
        wrapper: flet.Container,
        alignment: flet.MainAxisAlignment | None = flet.MainAxisAlignment.CENTER,
        vertical_alignment: flet.CrossAxisAlignment
        | None = flet.CrossAxisAlignment.CENTER,
        spacing: None | int | float = 0,
        tight: bool | None = None,
        wrap: bool | None = None,
        run_spacing: None | int | float = None,
        scroll: flet.ScrollMode | None = None,
        auto_scroll: bool | None = None,
        on_scroll_interval: None | int | float = None,
        on_scroll: Any = None,
        ref: flet.Ref | None = None,
        key: str | None = None,
        width: None | int | float = None,
        height: None | int | float = None,
        left: None | int | float = None,
        top: None | int | float = None,
        right: None | int | float = None,
        bottom: None | int | float = None,
        expand: None | bool | int = None,
        expand_loose: bool | None = None,
        col: Dict[str, int | float] | int | float | None = None,
        opacity: None | int | float = None,
        rotate: None | int | float | flet.Rotate = None,
        scale: None | int | float | flet.Scale = None,
        offset: None | flet.Offset | Tuple[float | int, float | int] = None,
        aspect_ratio: None | int | float = None,
        animate_opacity: None | bool | int | flet.Animation = None,
        animate_size: None | bool | int | flet.Animation = None,
        animate_position: None | bool | int | flet.Animation = None,
        animate_rotation: None | bool | int | flet.Animation = None,
        animate_scale: None | bool | int | flet.Animation = None,
        animate_offset: None | bool | int | flet.Animation = None,
        on_animation_end=None,
        visible: bool | None = None,
        disabled: bool | None = None,
        data: Any = None,
        rtl: bool | None = None,
        adaptive: bool | None = None,
    ):
        super().__init__(
            alignment=alignment,
            vertical_alignment=vertical_alignment,
            spacing=spacing,
            tight=tight,
            wrap=wrap,
            run_spacing=run_spacing,
            scroll=scroll,
            auto_scroll=auto_scroll,
            on_scroll_interval=on_scroll_interval,
            on_scroll=on_scroll,
            ref=ref,
            key=key,
            width=width,
            height=height,
            left=left,
            top=top,
            right=right,
            bottom=bottom,
            expand=expand,
            expand_loose=expand_loose,
            col=col,
            opacity=opacity,
            rotate=rotate,
            scale=scale,
            offset=offset,
            aspect_ratio=aspect_ratio,
            animate_opacity=animate_opacity,
            animate_size=animate_size,
            animate_position=animate_position,
            animate_rotation=animate_rotation,
            animate_scale=animate_scale,
            animate_offset=animate_offset,
            on_animation_end=on_animation_end,
            visible=visible,
            disabled=disabled,
            data=data,
            rtl=rtl,
            adaptive=adaptive,
        )

        self.obj: flet.Control = obj
        self.value_attribute: str = value_attribute

        self.text: flet.Text = text
        self.text.value: str | None = getattr(self.obj, self.value_attribute, None)

        self.wrapper: flet.Container = wrapper
        self.wrapper.content = self.text

        self.field: flet.TextField = field
        self.also_call = self.field.on_submit
        self.field.value = getattr(self.obj, self.value_attribute, None)
        self.field.on_submit = self.change_text
        if not self.field.content_padding:
            self.field.content_padding = 5
        if self.field.dense is None:
            self.field.dense = True
        self.field.text_size = field_size

        self.action_button = flet.IconButton(
            icon=flet.icons.EDIT,
            icon_size=self.field.text_size,
            on_click=self.edit_text,
        )
        self.controls = [self.wrapper, self.action_button]

    def edit_text(self, e):
        self.action_button.icon = flet.icons.CHECK
        self.action_button.on_click = self.change_text
        self.wrapper.content = self.field
        self.update()

    def change_text(self, e):
        self.action_button.icon = flet.icons.EDIT
        self.action_button.on_click = self.edit_text
        self.text.value = self.field.value.strip()
        setattr(self.obj, self.value_attribute, self.field.value.strip())
        self.wrapper.content = self.text
        # Call user given on_submit too
        if self.also_call is not None:
            self.also_call()
        self.update()
