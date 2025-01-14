# This Python file uses the following encoding: utf-8
import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os

# Definir nombres de archivos
GOALS_FILE = "goals.csv"
WORKOUT_FILE = "entrenamientos.csv"
WEIGHT_FILE = "peso.csv"

# Pool de ejercicios predefinidos
EXERCISES_POOL = {
    "Pecho-Tríceps": ["Banco Plano", "Banco Inclinado", "Pull Down Tricep", "Copa", "Pull Down Tricep Trenza",
                      "Copa Unilateral"],
    "Espalda-Bíceps": ["Pull Down", "Remo", "Pull Down Maquina", "Remo Maquina", "Curl Biceps", "Curl con Mancuerna",
                       "Pull Down Cerrado", "Dominadas"],
    "Pierna": ["Sentadilla", "Leg Extension Unilateral", "Curl Femoral Unilateral", "Curl Femoral"],
    "Otra": []  # Dejamos vacío para ejercicios personalizados
}


def read_csv_file(file_name):
    try:
        if not os.path.exists(file_name):
            print(f"Error: El archivo {file_name} no existe.")
            return None
        data = pd.read_csv(file_name)
        print(f"Archivo {file_name} leído correctamente.")
        return data
    except Exception as e:
        print(f"Error al leer el archivo {file_name}: {e}")
        return None


def save_to_csv(file_path, data, mode="w"):
    """
    Guarda los datos en un archivo CSV utilizando pandas.

    :param file_path: Ruta del archivo CSV.
    :param data: Datos a guardar, debe ser una lista de diccionarios.
    :param mode: Modo de apertura del archivo, por defecto es 'w' para escritura.
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(file_path, mode=mode, index=False, header=mode == "w")
        print("Datos guardados exitosamente.")
    except Exception as e:
        print(f"Error al guardar los datos en {file_path}: {e}")


def get_numeric_input(prompt):
    while True:
        try:
            value = int(input(prompt))  # Intenta convertir el valor ingresado a un número entero
            return value
        except ValueError:
            print("Por favor, ingresa un número válido.")


# Función para validar fecha
def validate_date(date_input):
    if not date_input:
        return datetime.now()

    try:
        return datetime.strptime(date_input, "%Y-%m-%d")
    except ValueError:
        print("Fecha inválida. Usa el formato AAAA-MM-DD. Usando la fecha actual.")
        return datetime.now()


def main_menu():
    while True:
        print("\n=== Gym Tracker ===")
        print("1. Registrar entrenamiento")
        print("2. Registrar peso corporal")
        print("3. Consultar estadísticas y gráficas")
        print("4. Ver historial de entrenamientos")
        print("5. Establecer o consultar metas")
        print("6. Salir")
        choice = input("Selecciona una opción: ")

        if choice == "1":
            register_workout()
        elif choice == "2":
            register_weight()
        elif choice == "3":
            view_stats()
        elif choice == "4":
            view_history()
        elif choice == "5":
            set_goals_or_delete()
        elif choice == "6":
            print("¡Hasta luego! Sigue entrenando fuerte.")
            sys.exit()
        else:
            print("Opción inválida. Inténtalo de nuevo.")


# Función para registrar el entrenamiento
def get_workout_date():
    """Obtiene la fecha del entrenamiento."""
    date_input = input("Fecha (deja en blanco para usar la fecha actual, formato AAAA-MM-DD): ")
    return validate_date(date_input)


def get_routine_type():
    """Obtiene el tipo de rutina elegido por el usuario."""
    while True:
        print("Selecciona el tipo de rutina:")
        print("1. Pecho-Tríceps")
        print("2. Espalda-Bíceps")
        print("3. Pierna")
        print("4. Otra")
        print("5. Descanso")
        print("6. Enfermo")
        print("0. Regresar al menú anterior")

        routine_map = {
            "1": "Pecho-Tríceps",
            "2": "Espalda-Bíceps",
            "3": "Pierna",
            "4": "Otra",
            "5": "Descanso",
            "6": "Enfermo"
        }

        routine_choice = get_numeric_input("Selecciona una opción (0-6): ")

        if routine_choice == 0:
            print("Regresando al menú anterior...")
            return None

        routine = routine_map.get(str(routine_choice))
        if routine:
            return routine
        else:
            print("Opción no válida. Intenta de nuevo.")


def get_exercises_for_routine(routine):
    """Obtiene la lista de ejercicios basada en la rutina seleccionada."""
    if routine is None:
        return None

    if routine in ["Descanso", "Enfermo"]:  # Si se selecciona descanso o enfermo, no hay ejercicios.
        return []
    elif routine != "Otra":
        return EXERCISES_POOL[routine]
    else:
        return [input("Nombre del ejercicio personalizado: ").strip()]


def select_exercises(exercises_list):
    """Permite seleccionar los ejercicios y sus respectivas series y pesos."""
    if exercises_list is None:
        print("Regresando al menú anterior...")
        return None

    if not exercises_list:  # Si no hay ejercicios, significa que es un día de descanso o enfermedad
        print("No hay ejercicios que registrar para este día.")
        return []

    while True:
        print("Selecciona los ejercicios que realizaste:")
        for idx, exercise in enumerate(exercises_list, start=1):
            print(f"{idx}. {exercise}")
        print("0. Regresar al menú anterior")

        selected_exercises = input("Ejercicios (ejemplo: 1,3): ").split(",")
        if "0" in selected_exercises:
            print("Regresando al menú anterior...")
            return None

        exercises = []

        for idx in selected_exercises:
            try:
                idx = int(idx.strip()) - 1
                exercise_name = exercises_list[idx]
            except (ValueError, IndexError):
                print(f"Error: Entrada no válida para el ejercicio {idx + 1}. Se omitirá.")
                continue

            sets = get_numeric_input(f"Número de series realizadas para {exercise_name}: ")
            set_info = collect_set_info(sets)
            if set_info is None:  # Si collect_set_info devuelve None, regresamos al menú anterior
                return None
            exercises.append({"name": exercise_name, "sets": set_info})

        if exercises:
            return exercises


def collect_set_info(sets):
    """Recoge la información de repeticiones y peso para cada serie."""
    set_info = []

    while True:
        same_weight = input(
            "¿Todas las series tienen el mismo peso? (s/n) o escribe '0' para regresar al menú anterior: ").strip().lower()

        if same_weight == "0":
            print("Regresando al menú anterior...")
            return None  # Regresar al menú anterior

        if same_weight == "s":
            reps = get_numeric_input("Repeticiones por serie: ")
            weight = get_numeric_input("Peso utilizado (kg): ")
            set_info = [{"reps": reps, "weight": weight}] * sets
            break  # Salir del ciclo después de recopilar la información
        elif same_weight == "n":
            for i in range(sets):
                reps = get_numeric_input(f"Repeticiones para la serie {i + 1}: ")
                weight = get_numeric_input(f"Peso para la serie {i + 1} (kg): ")
                set_info.append({"reps": reps, "weight": weight})
            break  # Salir del ciclo después de recopilar la información
        else:
            print("Opción no válida. Por favor, ingresa 's', 'n' o '0' para regresar.")

    return set_info


def display_workout_data(routine, date, exercises):
    """Muestra los datos ingresados del entrenamiento."""
    if routine in ["Descanso", "Enfermo"]:
        print(
            f"\nNo se registrara entrenamiento en la fecha {date.strftime('%Y-%m-%d')}. {routine.lower()}.")
    else:
        print(f"\nDatos ingresados para {routine} en la fecha {date.strftime('%Y-%m-%d')}:")
        for exercise in exercises:
            print(f"Ejercicio: {exercise['name']}")
            for set_item in exercise["sets"]:
                print(f"  Reps: {set_item['reps']} | Peso: {set_item['weight']} kg")


def confirm_and_save_workout_data(date, routine, exercises):
    """Confirma si se deben guardar los datos y los guarda si la respuesta es afirmativa."""
    save_choice = input("\n¿Deseas guardar estos datos? (s/n): ").strip().lower()
    if save_choice == "s":
        if routine in ["Descanso", "Enfermo"]:
            # Guardamos un registro del día de descanso o enfermedad
            print(f"Registrando el día de {routine.lower()} para {date.strftime('%Y-%m-%d')}.")
            save_to_csv(WORKOUT_FILE, [
                {"Fecha": date.strftime("%Y-%m-%d"), "Rutina": routine, "Ejercicio": routine,
                 "Repeticiones": 0, "Peso (kg)": 0}
            ], mode="a")
        else:
            # Guardamos los ejercicios normalmente
            save_to_csv(WORKOUT_FILE, [
                {"Fecha": date.strftime("%Y-%m-%d"), "Rutina": routine, "Ejercicio": exercise["name"],
                 "Repeticiones": set_item["reps"], "Peso (kg)": set_item["weight"]}
                for exercise in exercises for set_item in exercise["sets"]
            ], mode="a")


def register_workout():
    """Función principal para registrar un entrenamiento."""
    date = get_workout_date()

    # Llamada a la selección de rutina
    while True:
        routine = get_routine_type()
        if routine is None:  # Si el usuario decide regresar al menú anterior
            print("No se seleccionó una rutina. Regresando al menú principal.")
            return

        exercises_list = get_exercises_for_routine(routine)

        if exercises_list is None:  # Verificar si no se seleccionaron ejercicios
            print("No se seleccionaron ejercicios. Regresando a la selección de rutina.")
            continue

        print(f"\nEjercicios disponibles para la rutina {routine}:")
        for idx, exercise in enumerate(exercises_list, start=1):
            print(f"{idx}. {exercise}")

        exercises = select_exercises(exercises_list)

        if exercises is None:  # Verificar si no se registraron ejercicios
            print("No se registraron ejercicios. Regresando a la selección de rutina.")
            continue

        display_workout_data(routine, date, exercises)
        confirm_and_save_workout_data(date, routine, exercises)
        break  # Si todo está correcto, salimos del ciclo


# Función para registrar el peso corporal
def register_weight():
    date_input = input("Fecha (deja en blanco para usar la fecha actual, formato AAAA-MM-DD): ")
    date = validate_date(date_input)
    weight = get_numeric_input("Ingresa tu peso corporal (kg): ")

    save_to_csv(WEIGHT_FILE, [{"Fecha": date.strftime("%Y-%m-%d"), "Peso (kg)": weight}], mode="a")


def plot_progression(data, goals, exercise_column, metric_column, metric_name, routine, goal_column):
    """Genera gráficos de progresión de peso o repeticiones."""
    plt.figure(figsize=(12, 6))

    # Filtrar por ejercicio
    for exercise in data[exercise_column].unique():
        exercise_data = data[data[exercise_column] == exercise].sort_values("Fecha")

        # Graficar la progresión
        plt.plot(exercise_data["Fecha"], exercise_data[metric_column], marker="o", label=f"{metric_name} ({exercise})")

        # Línea para la meta
        if exercise in goals[exercise_column].values:
            goal_value = goals.loc[goals[exercise_column] == exercise, goal_column].values[0]
            plt.axhline(y=goal_value, color="green", linestyle="--", label=f"Meta {metric_name} ({exercise})")

        # Etiquetas de los valores
        for x, y in zip(exercise_data["Fecha"], exercise_data[metric_column]):
            plt.text(x, y, f"{y:.1f}", fontsize=8, color="black", ha="center")

    # Configuración del gráfico
    plt.xlabel("Fecha")
    plt.ylabel(metric_name)
    plt.title(f"Progresión de {metric_name} - Rutina: {routine}")
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.show()


def plot_routine_distribution(data):
    unique_sessions = data.groupby(["Fecha", "Rutina"]).size().reset_index(name="Conteo")
    routine_counts = unique_sessions["Rutina"].value_counts()
    routine_counts.plot(kind="bar", color="skyblue", title="Distribución de Rutinas")
    plt.xlabel("Tipo de Rutina")
    plt.ylabel("Número de Sesiones")
    plt.tight_layout()
    plt.show()


def analyze_routine(data, goals):
    while True:
        unique_routines = data["Rutina"].unique()
        print("Rutinas disponibles:")
        for idx, routine in enumerate(unique_routines, start=1):
            print(f"{idx}. {routine}")

        routine_choice = get_numeric_input("Selecciona el número de la rutina para analizar (o 0 para regresar): ")
        if routine_choice == 0:
            print("Regresando al menú anterior...")
            return
        if routine_choice < 1 or routine_choice > len(unique_routines):
            print("Selección no válida. Intenta de nuevo.")
            continue

        routine = unique_routines[routine_choice - 1]
        routine_data = data[data["Rutina"] == routine].copy()

        unique_exercises = routine_data["Ejercicio"].unique()
        print("\nEjercicios disponibles en la rutina:")
        for idx, exercise in enumerate(unique_exercises, start=1):
            print(f"{idx}. {exercise}")

        exercise_choice = get_numeric_input("Selecciona el número del ejercicio para analizar (o 0 para regresar): ")
        if exercise_choice == 0:
            print("Regresando al menú anterior...")
            continue
        if exercise_choice < 1 or exercise_choice > len(unique_exercises):
            print("Selección no válida. Intenta de nuevo.")
            continue

        exercise = unique_exercises[exercise_choice - 1]
        exercise_data = routine_data[routine_data["Ejercicio"] == exercise].copy()
        plot_progression(exercise_data, goals, "Ejercicio", "Repeticiones", "Repeticiones", routine, "Meta Reps")
        plot_progression(exercise_data, goals, "Ejercicio", "Peso (kg)", "Peso", routine, "Meta Peso (kg)")


def view_stats():
    while True:
        data = read_csv_file(WORKOUT_FILE)
        if data is None or data.empty:
            print("No hay datos disponibles para analizar.")
            return

        data["Fecha"] = pd.to_datetime(data["Fecha"], errors="coerce")

        goals = read_csv_file(GOALS_FILE)
        if goals is None:
            goals = pd.DataFrame(columns=["Ejercicio", "Meta Peso (kg)", "Meta Reps", "Fecha Límite"])

        print("\n¿Qué deseas hacer?")
        print("1. Ver distribución de entrenamientos.")
        print("2. Analizar progresión de ejercicios.")
        print("0. Regresar al menú anterior.")

        choice = get_numeric_input("Selecciona una opción (0, 1 o 2): ")
        if choice == 0:
            print("Regresando al menú principal...")
            break
        elif choice == 1:
            plot_routine_distribution(data)
        elif choice == 2:
            analyze_routine(data, goals)
        else:
            print("Opción no válida. Intenta de nuevo.")
            continue

        another_stat = input("¿Deseas realizar otra acción? (s/n): ").strip().lower()
        if another_stat != "s":
            print("Saliendo del análisis de estadísticas.")
            break


def view_history():
    # Leer archivo de entrenamientos
    data = read_csv_file(WORKOUT_FILE)
    if data is None:
        return

    # Asegurar que la columna "Fecha" sea de tipo datetime
    try:
        data["Fecha"] = pd.to_datetime(data["Fecha"])
    except KeyError:
        print("Error: La columna 'Fecha' no está presente en el archivo.")
        return

    # Solicitar la fecha que deseas ver
    date_input = input("Ingresa la fecha que deseas ver (formato AAAA-MM-DD): ")
    selected_date = validate_date(date_input)

    # Filtrar los entrenamientos por la fecha seleccionada
    filtered_data = data[data["Fecha"].dt.date == selected_date.date()]

    if filtered_data.empty:
        print(f"No hay entrenamientos registrados para el día {selected_date.date()}.")
    else:
        print(f"\nHistorial de entrenamientos para el día {selected_date.date()}:")
        print(filtered_data[["Fecha", "Rutina", "Ejercicio", "Repeticiones", "Peso (kg)"]].to_string(index=False))



def set_goals_or_delete():
    while True:  # Cargar las metas cada vez que se entra en el menú
        options = {
            "1": lambda: set_goals(),
            "2": lambda: view_goals(),
            "3": lambda: delete_goals(),
            "4": lambda: print("Volviendo al menú principal...")
        }
        print("\n1. Establecer metas")
        print("2. Consultar metas existentes")
        print("3. Eliminar metas")
        print("4. Volver al menú principal")

        choice = input("Selecciona una opción: ")
        action = options.get(choice)

        if action:
            action()
            if choice == "4":
                break
        else:
            print("Opción no válida. Intenta de nuevo.")


def set_goals():
    goals = load_or_create_goals()  # Cargar las metas antes de establecer una nueva
    exercises = list_exercises()
    if len(exercises) == 0:  # Verifica si no hay ejercicios disponibles
        print("No hay ejercicios disponibles para fijar metas. Registra entrenamientos primero.")
        return

    print("\nEjercicios disponibles:")
    for idx, exercise in enumerate(exercises, 1):
        print(f"{idx}. {exercise}")

    selected_exercise = get_exercise_selection(exercises)
    if not selected_exercise:
        return

    # Verificar si la meta ya existe
    existing_goal = goals[goals["Ejercicio"] == selected_exercise]
    if not existing_goal.empty:
        print(f"Ya existe una meta para {selected_exercise}:\n{existing_goal}")
        update_choice = input("¿Quieres actualizar la meta? (s/n): ").strip().lower()
        if update_choice != "s":
            return

    # Establecer nueva meta
    print("\nEstablece tu meta para el ejercicio seleccionado:")
    goal_weight = get_numeric_input(f"Meta Peso (kg) para {selected_exercise}: ")
    goal_reps = get_numeric_input(f"Meta Repeticiones para {selected_exercise}: ")
    goal_date = input("Fecha límite para la meta (AAAA-MM-DD): ")
    try:
        goal_date = datetime.strptime(goal_date, "%Y-%m-%d")
    except ValueError:
        print("Fecha inválida. Usando la fecha actual.")
        goal_date = datetime.now()

    new_goal = {
        "Ejercicio": selected_exercise,
        "Meta Peso (kg)": goal_weight,
        "Meta Reps": goal_reps,
        "Fecha Límite": goal_date.strftime("%Y-%m-%d")
    }

    # Convertir new_goal a un DataFrame
    new_goal_df = pd.DataFrame([new_goal])

    # Concatenar la nueva meta con las existentes
    goals = pd.concat([goals, new_goal_df], ignore_index=True)

    # Guardar las metas actualizadas
    save_to_csv(GOALS_FILE, goals, mode='w')  # Guardar las metas

    print(f"Meta para {selected_exercise} guardada correctamente.")

    # Recargar metas después de establecer la nueva
    view_goals()


def get_exercise_selection(exercises):
    try:
        selected_exercise = int(input("Selecciona el número del ejercicio para fijar una meta: "))
        return exercises[selected_exercise - 1]  # Ajustar el índice
    except (ValueError, IndexError):
        print("Selección inválida.")
        return None


def view_goals():
    goals = load_or_create_goals()  # Recargar las metas para asegurar que están actualizadas

    if goals.empty:
        print("No hay metas registradas.")
        return

    print("\nMetas establecidas:")
    for idx, (index, goal) in enumerate(goals.iterrows(), 1):  # Usamos enumerate para contar desde 1
        print(
            f"{idx}. {goal['Ejercicio']} | Peso Meta: {goal['Meta Peso (kg)']} kg | Reps Meta: {goal['Meta Reps']} | Fecha Límite: {goal['Fecha Límite']}")

    if input("\n¿Deseas comparar con tus entrenamientos registrados? (s/n): ").lower() == "s":
        track_goals(goals)


def delete_goals():
    goals = load_or_create_goals()  # Recargar las metas antes de eliminar

    if goals.empty:
        print("No hay metas registradas.")
        return

    print("\nMetas establecidas:")
    # Enumerar las metas antes de eliminarlas
    for idx, (index, goal) in enumerate(goals.iterrows(), 1):  # Usamos enumerate para contar desde 1
        print(
            f"{idx}. {goal['Ejercicio']} | Peso Meta: {goal['Meta Peso (kg)']} kg | Reps Meta: {goal['Meta Reps']} | Fecha Límite: {goal['Fecha Límite']}")

    # Selección de la meta a eliminar
    selection = get_numeric_input("Selecciona el número de la meta a eliminar: ") - 1
    if 0 <= selection < len(goals):
        # Eliminar la meta seleccionada
        goals = goals.drop(selection)
        goals = goals.reset_index(drop=True)  # Restablecer el índice de las filas
        save_to_csv(GOALS_FILE, goals, mode='w')  # Guardar los cambios
        print("Meta eliminada y numeración actualizada.")
    else:
        print("Número de meta no válido.")

    # Recargar metas después de la eliminación
    view_goals()


def track_goals(goals):
    try:
        workouts = pd.read_csv(WORKOUT_FILE)
    except FileNotFoundError:
        print("No hay registros de entrenamientos disponibles.")
        return

    print("\nSeguimiento de Metas:")
    for _, goal in goals.iterrows():
        exercise = goal["Ejercicio"]
        weight_goal = goal["Meta Peso (kg)"]
        reps_goal = goal["Meta Reps"]

        exercise_workouts = workouts[workouts["Ejercicio"] == exercise]
        max_weight = exercise_workouts["Peso (kg)"].max()
        max_reps = exercise_workouts["Repeticiones"].max()

        print(f"\nEjercicio: {exercise}")
        print(f"- Meta Peso: {weight_goal} kg | Máximo alcanzado: {max_weight if not pd.isna(max_weight) else 0} kg")
        print(f"- Meta Reps: {reps_goal} | Máximo alcanzado: {max_reps if not pd.isna(max_reps) else 0}")

        if max_weight < weight_goal or max_reps < reps_goal:
            print("Meta aún no alcanzada. Sigue esforzándote.")
        else:
            print("¡Meta alcanzada! 🎉")


def load_or_create_goals():
    try:
        goals = pd.read_csv(GOALS_FILE)
    except FileNotFoundError:
        goals = pd.DataFrame(columns=["Ejercicio", "Meta Peso (kg)", "Meta Reps", "Fecha Límite"])
        save_to_csv(GOALS_FILE, goals, mode='w')
    return goals


def list_exercises():
    exercises = []
    for routine, exercises_list in EXERCISES_POOL.items():
        exercises.extend(exercises_list)
    return exercises


main_menu()
