"""
Point d'entrée principal de l'application de réservation de cinéma.
Lance l'interface graphique Tkinter.
"""
import tkinter as tk
from ui import CinemaApp


def main():
    """Point d'entrée de l'application GUI."""
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
