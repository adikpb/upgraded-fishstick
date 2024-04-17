import flet


class EditableDisplayText(flet.Row):
    def __init__(
        self,
        obj: flet.Control,
        value_attribute: str,
        text_theme_style: flet.TextThemeStyle,
        field_size: float,
        input_filter: flet.InputFilter = None,
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
            autofocus=True,
            content_padding=5,
            text_size=field_size,
            input_filter=input_filter,
        )
        self.action_button = flet.IconButton(
            icon=flet.icons.EDIT,
            icon_size=field_size,
            on_click=self.edit_text,
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
