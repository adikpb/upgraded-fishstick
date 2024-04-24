from typing import Any

from flet import Page, RouteChangeEvent, View


class RouteManager:
    def __init__(self, page: Page, base_view: View = None):
        self.page: Page = page
        self.base_view: View = base_view
        self.routes: dict[str, View] = (
            {base_view.route: base_view} if base_view is not None else {}
        )

    @property
    def base_view(self) -> View:
        return self._base_view

    @base_view.setter
    def base_view(self, value: View):
        if value is not None:
            self.add_route(value.route, value)
            if self.base_view:
                self.remove_route(self.base_view.route)
        self._base_view: View = value

    def add_route(self, route: str, view: View):
        self.routes[route] = view

    def remove_route(self, route: str):
        self.routes.pop(route)

    async def on_route_change(self, route_event: RouteChangeEvent):
        temp: list[View] = [i for i in self.page.views]
        self.page.views.clear()
        self.page.views.append(self.base_view)
        if self.page.route in self.routes and self.page.route != self.base_view.route:
            for i, j in enumerate(self.page.views):
                if j.route == self.page.route:
                    self.page.views.clear()
                    self.page.views.extend(temp[: i + 1])
                    break
            else:
                self.page.views.append(self.routes[self.page.route])
        else:
            self.page.route = self.base_view.route
        self.page.update()

    def on_view_pop(self, view: View):
        self.page.views.pop()
        top_view: View = self.page.views[-1]
        self.page.go(top_view.route)
        self.page.update()

    def as_dict(self) -> dict[str, Any]:
        return {"page": self.page, "base_view": self.base_view, "routes": self.routes}
