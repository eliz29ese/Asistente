class RobotTasks:
    def __init__(self, robot):
        self.robot = robot

    def buscar_objeto(self, objeto):
        print(f"Buscando {objeto}")
        print(f"{objeto} localizado")

    def recoger_objeto(self, objeto):
        print(f"Recogiendo {objeto}")
        self.robot.abrir_pinza()
        self.robot.cerrar_pinza()
        print(f"{objeto} recogido")

    def llevar_objeto(self, destino):
        print(f"Llevando objeto hacia {destino}")
        print(f"Objeto llevado a {destino}")

    def entregar_objeto(self):
        print("Entregando objeto")
        self.robot.abrir_pinza()
        print("Objeto entregado")

    def buscar_y_entregar(self, objeto):
        self.buscar_objeto(objeto)
        self.recoger_objeto(objeto)
        self.llevar_objeto("usuario")
        self.entregar_objeto()
