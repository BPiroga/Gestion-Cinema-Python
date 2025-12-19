"""
Point d'entrée principal de l'application de réservation de cinéma.
Lance l'interface d'administration.
"""
import tkinter as tk
from administration import AdminApp


def main():
    """Point d'entrée de l'application - Lance l'interface admin."""
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
