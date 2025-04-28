import ttkbootstrap as ttk
import logging

logger = logging.getLogger(__name__)

class CreateToolTip:
    """
    Clase para crear un tooltip (popup informativo) para un widget.
    Aparece después de un breve retraso al posicionar el mouse.
    """
    def __init__(self, widget, text="Información", delay=500):
        """
        Inicializa el tooltip.
        :param widget: Widget asociado.
        :param text: Texto que se mostrará en el tooltip.
        :param delay: Tiempo (en milisegundos) antes de que el tooltip aparezca.
        """
        self.widget = widget
        self.text = text
        self.delay = delay  # milisegundos
        self.tooltip = None
        self.after_id = None

        # Vincular eventos al widget.
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        """
        Maneja el evento de entrada del mouse en el widget.
        """
        self.after_id = self.widget.after(self.delay, self.show_tooltip)

    def show_tooltip(self):
        """
        Crea y muestra el tooltip.
        """
        try:
            x = self.widget.winfo_pointerx() + 10
            y = self.widget.winfo_pointery() + 10
            self.tooltip = ttk.Toplevel(self.widget)
            self.tooltip.overrideredirect(True)
            self.tooltip.geometry(f"+{x}+{y}")
            label = ttk.Label(
                self.tooltip,
                text=self.text,
                background="lightyellow",
                relief="solid",
                borderwidth=1,
                font=("tahoma", 8),
            )
            label.pack(ipadx=1)
        except Exception as e:
            logger.exception("Error al mostrar tooltip: %s", e)

    def leave(self, event=None):
        """
        Maneja el evento de salida del mouse del widget.
        """
        if self.after_id:
            try:
                self.widget.after_cancel(self.after_id)
            except Exception as e:
                logger.error("Error al cancelar el after del tooltip: %s", e)
            self.after_id = None
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
