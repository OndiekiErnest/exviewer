"""Custom PyQt6 widget classes."""

from qtawesome import IconWidget

from .utils import qicon, qpulsing_animation


class AnimatedIconWidget(IconWidget):
    """
    Icon widget with built in animation.

    Args:
        name (str): name of the icon to use from qtawesome
        **kwargs: additional keyword arguments to pass to qtawesome icon function
    """

    def __init__(self, name: str, **kwargs):
        super().__init__()
        self.animation = qpulsing_animation(self, autostart=False)
        self.icon = qicon(name, animation=self.animation, **kwargs)

        self.setIcon(self.icon)

    def show(self):
        """start animation and show widget"""
        self.animation.start()
        super().show()

    def hide(self):
        """stop animation and hide widget"""
        self.animation.stop()
        super().hide()
