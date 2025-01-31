import sys
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import List, Dict, Optional

# Configuración de archivos
GOALS_FILE = "goals.csv"
WORKOUT_FILE = "entrenamientos.csv"
WEIGHT_FILE = "peso.csv"

EXERCISE_POOL = {
    "Pecho-Tríceps": ["Banco Plano", "Banco Inclinado", "Pull Down Tricep", "Copa", "Pull Down Tricep Trenza",
                      "Copa Unilateral","Press Pecho Maquina","Press Pecho Maquina Unilateral","Shoulder Press","Fondos Máquina"
                      ,"Press Inclinado Mancuerna","Pec Fly","Pull Down Unilateral"],
    "Espalda-Bíceps": ["Pull Down", "Remo", "Pull Down Maquina", "Remo Maquina", "Curl Biceps", "Curl con Mancuerna",
                       "Pull Down Cerrado", "Dominadas","Pull Over"],
    "Pierna": ["Sentadilla", "Leg Extension Unilateral", "Curl Femoral Unilateral", 
               "Curl Femoral", "Peso Muerto", "Sentadilla Búlgara"],
    "Otros": []
}

class DataManager:
    """Maneja todas las operaciones de lectura/escritura de datos"""
    
    @staticmethod
    def load_data(file_name: str) -> pd.DataFrame:
        try:
            if os.path.exists(file_name):
                return pd.read_csv(file_name, parse_dates=["Fecha"])
            return pd.DataFrame()
        except Exception as e:
            print(f"Error cargando {file_name}: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def save_data(data: List[Dict], file_name: str, mode: str = "w", columns: List[str] = None) -> None:
        try:
            df = pd.DataFrame(data, columns=columns) if columns else pd.DataFrame(data)
            header = not os.path.exists(file_name) or mode == "w"
            df.to_csv(file_name, mode=mode, index=False, header=header)
        except Exception as e:
            print(f"Error guardando en {file_name}: {str(e)}")

class InputHandler:
    """Maneja todas las entradas de usuario y validaciones"""
    
    @staticmethod
    def get_date(prompt: str) -> datetime:
        while True:
            date_str = input(prompt).strip()
            if not date_str:
                return datetime.now()
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print("Formato de fecha inválido. Use YYYY-MM-DD.")

    @staticmethod
    def get_int(prompt: str) -> int:
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Debe ingresar un número entero válido.")

    @staticmethod
    def select_option(options: List[str]) -> int:
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")
        print("0. Regresar")
        
        while True:
            try:
                choice = int(input("Selección: "))
                if 0 <= choice <= len(options):
                    return choice
                print("Opción inválida")
            except ValueError:
                print("Ingrese un número válido")

class WorkoutManager:
    """Maneja toda la lógica de registro de entrenamientos"""
    
    def __init__(self):
        self.workouts = DataManager.load_data(WORKOUT_FILE)
    
    def register_workout(self):
        date = InputHandler.get_date("Fecha (YYYY-MM-DD o enter para hoy): ")
        routine = self._select_routine()
        
        if routine in ["Descanso", "Enfermo"]:
            self._save_rest_day(date, routine)
            return
            
        exercises = self._select_exercises(routine)
        if not exercises:
            return
            
        workout_data = self._prepare_workout_data(date, routine, exercises)
        DataManager.save_data(workout_data, WORKOUT_FILE)
        print("\nEntrenamiento registrado exitosamente!")

    def _select_routine(self) -> str:
        routines = list(EXERCISE_POOL.keys()) + ["Descanso", "Enfermo"]
        print("\nSeleccione tipo de rutina:")
        choice = InputHandler.select_option(routines)
        return routines[choice-1] if choice != 0 else ""

    def _select_exercises(self, routine: str) -> List[Dict]:
        if routine in ["Descanso", "Enfermo"]:
            return []

        base_exercises = EXERCISE_POOL[routine] if routine != "Otros" else []
        custom_exercises = []
        
        if routine == "Otros":
            print("\nIngrese ejercicios personalizados (deje vacío para terminar):")
            while True:
                exercise = input("Nombre del ejercicio: ").strip()
                if not exercise:
                    break
                custom_exercises.append(exercise)
        
        all_exercises = base_exercises + custom_exercises
        
        if not all_exercises:
            print("No hay ejercicios disponibles para esta rutina")
            return []

        print("\nSeleccione ejercicos (ej: 1,3-5,7):")
        for idx, exercise in enumerate(all_exercises, 1):
            print(f"{idx}. {exercise}")
            
        selected = self._parse_selection(input("Selección: "), len(all_exercises))
        if not selected:
            return []
            
        return self._get_sets_info([all_exercises[i-1] for i in selected])

    def _parse_selection(self, input_str: str, max_items: int) -> List[int]:
        selected = set()
        parts = input_str.replace(" ", "").split(",")
        
        for part in parts:
            if "-" in part:
                try:
                    start, end = map(int, part.split("-"))
                    selected.update(range(start, end+1))
                except:
                    print(f"Rango inválido: {part}")
            else:
                try:
                    num = int(part)
                    if 1 <= num <= max_items:
                        selected.add(num)
                    else:
                        print(f"Número fuera de rango: {num}")
                except:
                    print(f"Entrada inválida: {part}")
        
        return sorted(selected)

    def _get_sets_info(self, exercises: List[str]) -> List[Dict]:
        results = []
        for exercise in exercises:
            print(f"\nEjercicio: {exercise}")
            sets = InputHandler.get_int("Número de series: ")
            set_info = self._collect_set_data(sets)
            if not set_info:
                return []
            results.append({"name": exercise, "sets": set_info})
        return results

    def _collect_set_data(self, num_sets: int) -> List[Dict]:
        set_info = []
        same_weight = input("¿Mismo peso para todas las series? (s/n): ").lower()
        
        if same_weight == "s":
            reps = InputHandler.get_int("Repeticiones por serie: ")
            weight = InputHandler.get_int("Peso (kg): ")
            return [{"reps": reps, "weight": weight}] * num_sets
        
        for i in range(num_sets):
            print(f"\nSerie {i+1}:")
            reps = InputHandler.get_int("Repeticiones: ")
            weight = InputHandler.get_int("Peso (kg): ")
            set_info.append({"reps": reps, "weight": weight})
        return set_info

    def _prepare_workout_data(self, date: datetime, routine: str, exercises: List[Dict]) -> List[Dict]:
        return [{
            "Fecha": date.strftime("%Y-%m-%d"),
            "Rutina": routine,
            "Ejercicio": ex["name"],
            "Repeticiones": set_data["reps"],
            "Peso (kg)": set_data["weight"]
        } for ex in exercises for set_data in ex["sets"]]

    def _save_rest_day(self, date: datetime, reason: str):
        DataManager.save_data([{
            "Fecha": date.strftime("%Y-%m-%d"),
            "Rutina": reason,
            "Ejercicio": reason,
            "Repeticiones": 0,
            "Peso (kg)": 0
        }], WORKOUT_FILE)

class GoalManager:
    """Maneja la configuración y seguimiento de metas"""
    def __init__(self):
        self._initialize_goals_file()
        self.goals = self._load_goals()
        self.workouts = DataManager.load_data(WORKOUT_FILE)

    def _initialize_goals_file(self):
        """Crea el archivo con estructura inicial si no existe"""
        if not os.path.exists(GOALS_FILE):
            DataManager.save_data(
                data=[],
                file_name=GOALS_FILE,
                mode="w",
                columns=["Ejercicio", "Meta Peso (kg)", "Meta Reps", "Fecha Límite"]
            )
    
    def _load_goals(self) -> pd.DataFrame:
        """Carga las metas con validación de estructura y tipos"""
        try:
            # Leer CSV sin parsear fechas primero
            goals = pd.read_csv(
                GOALS_FILE,
                dtype={
                    "Ejercicio": "category",
                    "Meta Peso (kg)": "float64",
                    "Meta Reps": "int32",
                    "Fecha Límite": "object"  # Leer como string primero
                }
            )
            
            # Convertir columna de fecha manualmente
            if "Fecha Límite" in goals.columns:
                goals["Fecha Límite"] = pd.to_datetime(
                    goals["Fecha Límite"],
                    format="%Y-%m-%d",
                    errors="coerce"
                )
            
            return goals.dropna(how="all")
        
        except Exception as e:
            print(f"Error cargando metas: {str(e)}")
            return pd.DataFrame(columns=["Ejercicio", "Meta Peso (kg)", "Meta Reps", "Fecha Límite"])
        
    def _save_goals(self):
        """Guarda las metas con formato controlado y manejo de errores"""
        try:
            # Convertir a formato de guardado compatible
            save_data = self.goals.copy()
            save_data["Fecha Límite"] = save_data["Fecha Límite"].dt.strftime("%Y-%m-%d")
            
            DataManager.save_data(
                save_data.to_dict("records"),
                GOALS_FILE,
                mode="w"
            )
        except Exception as e:
            print(f"Error crítico guardando metas: {str(e)}")
            raise
        
    def _initialize_columns(self):
        """Asegura que el DataFrame tenga las columnas necesarias"""
        required_columns = ["Ejercicio", "Meta Peso (kg)", "Meta Reps", "Fecha Límite"]
        for col in required_columns:
            if col not in self.goals.columns:
                self.goals[col] = pd.Series(dtype='object' if col == "Ejercicio" else 'float64')
    
    def manage_goals(self):
        while True:
            print("\nGestión de Metas:")
            options = [
                "Establecer nueva meta", 
                "Ver metas existentes", 
                "Eliminar meta",
                "Volver al menú principal"
            ]
            choice = InputHandler.select_option(options)
            
            if choice == 0 or choice == 4:
                return
            elif choice == 1:
                self.set_goal()
            elif choice == 2:
                self.view_goals()
            elif choice == 3:
                self.delete_goal()

    def set_goal(self):
        unique_exercises = self.workouts["Ejercicio"].unique()
        if len(unique_exercises) == 0:
            print("Primero registre algunos entrenamientos")
            return
            
        print("\nEjercicios disponibles:")
        choice = InputHandler.select_option(list(unique_exercises))
        if choice == 0:
            return
            
        exercise = unique_exercises[choice-1]
        self._update_goal(exercise)

    def _update_goal(self, exercise: str):
        """Actualiza o crea una nueva meta para un ejercicio"""
        print(f"\nEstableciendo meta para {exercise}:")
        
        # Validar existencia de columna
        if not self.goals.empty and "Ejercicio" not in self.goals.columns:
            raise KeyError("Estructura inválida en metas existentes")
        
        # Obtener valores con validación
        target_weight = InputHandler.get_int("Peso objetivo (kg): ")
        target_reps = InputHandler.get_int("Repeticiones objetivo: ")
        deadline = InputHandler.get_date("Fecha límite (YYYY-MM-DD): ")
        
        # Eliminar meta existente si existe
        if not self.goals.empty:
            self.goals = self.goals[self.goals["Ejercicio"] != exercise]
        
        # Crear nueva meta con tipos controlados
        new_goal = pd.DataFrame([{
            "Ejercicio": str(exercise),
            "Meta Peso (kg)": float(target_weight),
            "Meta Reps": int(target_reps),
            "Fecha Límite": pd.to_datetime(deadline)
        }])
        
        # Actualizar DataFrame y guardar
        self.goals = pd.concat([self.goals, new_goal], ignore_index=True)
        self._save_goals()
        print("\n✅ Meta registrada exitosamente!")

    def view_goals(self):
        if self.goals.empty:
            print("No hay metas establecidas")
            return
            
        print("\nMetas actuales:")
        for idx, row in self.goals.iterrows():
            print(f"{idx+1}. {row['Ejercicio']} - "
                  f"Peso: {row['Meta Peso (kg)']}kg | "
                  f"Reps: {row['Meta Reps']} | "
                  f"Límite: {row['Fecha Límite']}")

    def delete_goal(self):
        """Elimina una meta existente con validación robusta"""
        if self.goals.empty:
            print("🚨 No hay metas registradas en el sistema")
            return
            
        self.view_goals()
        
        try:
            choice = InputHandler.get_int("\nSeleccione la meta a eliminar: ")
            if 1 <= choice <= len(self.goals):
                # Eliminar y resetear índice
                self.goals = self.goals.drop(self.goals.index[choice-1]).reset_index(drop=True)
                self._save_goals()
                print("\n🗑️ Meta eliminada exitosamente!")
            else:
                print("⚠️ Número fuera de rango válido")
        except Exception as e:
            print(f"🚨 Error al eliminar meta: {str(e)}")
    
    def compare_goals(self):
        """Compara el progreso actual con las metas establecidas"""
        if self.goals.empty:
            print("\n⚠️ No hay metas registradas")
            return
            
        if self.workouts.empty:
            print("\n⚠️ No hay entrenamientos registrados")
            return
            
        print("\n🔍 Comparación con metas:")
        for _, goal in self.goals.iterrows():
            exercise = goal["Ejercicio"]
            target_weight = goal["Meta Peso (kg)"]
            target_reps = goal["Meta Reps"]
            deadline = pd.to_datetime(goal["Fecha Límite"])
            
            # Filtrar entrenamientos válidos
            exercise_data = self.workouts[
                (self.workouts["Ejercicio"] == exercise) &
                (pd.to_datetime(self.workouts["Fecha"]) <= deadline)
            ]
            
            # Calcular máximos
            max_weight = exercise_data["Peso (kg)"].max()
            max_reps = exercise_data["Repeticiones"].max()
            
            # Mostrar resultados
            self._display_comparison(
                exercise=exercise,
                target_weight=target_weight,
                target_reps=target_reps,
                max_weight=max_weight,
                max_reps=max_reps,
                deadline=deadline
            )
        
        input("\nPresione Enter para continuar...")

    def _display_comparison(self, exercise: str, target_weight: float, target_reps: int,
                          max_weight: float, max_reps: float, deadline: datetime):
        """Muestra los resultados de la comparación de forma estructurada"""
        print(f"\n🏋️ Ejercicio: {exercise}")
        print(f"   Meta: {target_reps} reps @ {target_weight}kg")
        print(f"   Máximo alcanzado: {self._safe_value(max_reps)} reps @ {self._safe_value(max_weight)}kg")
        print(f"   Fecha límite: {deadline.strftime('%Y-%m-%d')}")
        
        weight_ok = max_weight >= target_weight if not pd.isna(max_weight) else False
        reps_ok = max_reps >= target_reps if not pd.isna(max_reps) else False
        
        if weight_ok and reps_ok:
            print("   ✅ Meta cumplida!")
        else:
            self._show_pending(target_weight, max_weight, target_reps, max_reps)

    def _safe_value(self, value):
        """Maneja valores NaN"""
        return value if not pd.isna(value) else 0

    def _show_pending(self, target_weight, max_weight, target_reps, max_reps):
        """Muestra lo que falta para cumplir la meta"""
        missing = []
        if max_weight < target_weight:
            missing.append(f"{(target_weight - max_weight):.1f}kg de peso")
        if max_reps < target_reps:
            missing.append(f"{(target_reps - max_reps)} reps")
        
        if missing:
            print(f"   🚫 Pendiente: {', '.join(missing)}")
        else:
            print("   ⚠️ Sin datos registrados")

class ProgressTracker:
    """Maneja el análisis de progreso y estadísticas"""
    
    def __init__(self, goal_manager: GoalManager):
        self.workouts = DataManager.load_data(WORKOUT_FILE)
        self.goal_manager = goal_manager
    
    def show_stats(self):
        while True:
            print("\nAnálisis de progreso:")
            options = [
                "Distribución de rutinas",
                "Progresión de ejercicios",
                "Comparación con metas"
            ]
            choice = InputHandler.select_option(options)
            
            if choice == 0:
                return
            elif choice == 1:
                self.plot_routine_distribution()
            elif choice == 2:
                self.analyze_exercise_progress()
            elif choice == 3:
                self.goal_manager.compare_goals()

    def plot_routine_distribution(self):
        if self.workouts.empty:
            print("No hay datos de entrenamientos")
            return
        
        try:
            # Obtener días únicos por rutina
            unique_days = self.workouts.groupby('Fecha')['Rutina'].first().reset_index()
            routine_counts = unique_days['Rutina'].value_counts()

            # Crear figura
            plt.figure(figsize=(12, 6))
            ax = routine_counts.plot(kind='bar', 
                                color='#4CAF50', 
                                edgecolor='black',
                                alpha=0.8)
            
            # Personalizar gráfico
            plt.title('Distribución de Rutinas por Día', fontsize=14, pad=20)
            plt.xlabel('Tipo de Rutina', fontsize=12, labelpad=10)
            plt.ylabel('Número de Días', fontsize=12, labelpad=10)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.yticks(fontsize=10)
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            # Añadir etiquetas de datos
            for i, count in enumerate(routine_counts):
                ax.text(i, 
                        count + 0.5, 
                        str(count), 
                        ha='center', 
                        va='bottom',
                        fontsize=10,
                        color='black',
                        fontweight='bold')

            # Añadir línea de promedio
            mean_line = routine_counts.mean()
            plt.axhline(mean_line, 
                    color='red', 
                    linestyle='--', 
                    linewidth=1.5,
                    label=f'Promedio: {mean_line:.1f} días')
            plt.legend()

            plt.tight_layout()
            plt.show()

        except KeyError as e:
            print(f"Error en los datos: {str(e)}")
        except Exception as e:
            print(f"Error al generar el gráfico: {str(e)}")
    
    def _select_exercise(self) -> Optional[str]:
        """Muestra lista de ejercicios y permite seleccionar uno"""
        unique_exercises = self.workouts["Ejercicio"].unique()
        
        if len(unique_exercises) == 0:
            print("No hay ejercicios registrados")
            return None
            
        print("\nEjercicios disponibles:")
        for idx, exercise in enumerate(unique_exercises, 1):
            print(f"{idx}. {exercise}")
            
        while True:
            try:
                choice = int(input("Seleccione el ejercicio (0 para cancelar): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(unique_exercises):
                    return unique_exercises[choice - 1]
                print("Número inválido")
            except ValueError:
                print("Ingrese un número válido")

    def analyze_exercise_progress(self):
        exercise = self._select_exercise()
        if not exercise:
            return
            
        exercise_data = self.workouts[self.workouts["Ejercicio"] == exercise]
        self._plot_progression(exercise_data, "Repeticiones", "Evolución de Repeticiones")
        self._plot_progression(exercise_data, "Peso (kg)", "Evolución de Peso")

    def _plot_progression(self, data: pd.DataFrame, metric: str, title: str):
        dates = pd.to_datetime(data["Fecha"]).dt.date
        plt.figure(figsize=(10, 5))
        plt.plot(dates, data[metric], marker="o")
        plt.title(f"{title} - {data['Ejercicio'].iloc[0]}")
        plt.xlabel("Fecha")
        plt.ylabel(metric)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

class GymTracker:
    """Clase principal que coordina todas las funcionalidades"""
    
    def __init__(self):
        self.goal_manager = GoalManager()  # 1. Crear primero GoalManager
        self.workout_manager = WorkoutManager()  # 2. WorkoutManager
        self.progress_tracker = ProgressTracker(self.goal_manager)  # 3. Inyectar dependencia

    
    def main_menu(self):
        while True:
            print("\n=== GYM TRACKER ===")
            options = [
                "Registrar entrenamiento",
                "Registrar peso corporal",
                "Ver estadísticas",
                "Gestión de metas",
                "Salir"
            ]
            
            choice = InputHandler.select_option(options)
            
            if choice == 1:
                self.workout_manager.register_workout()
            elif choice == 2:
                self.register_weight()
            elif choice == 3:
                self.progress_tracker.show_stats()
            elif choice == 4:
                self.goal_manager.manage_goals()
            elif choice == 5:
                print("¡Hasta luego! 💪")
                sys.exit()

    def register_weight(self):
        date = InputHandler.get_date("Fecha (YYYY-MM-DD o enter para hoy): ")
        weight = InputHandler.get_int("Peso corporal (kg): ")
        DataManager.save_data([{
            "Fecha": date.strftime("%Y-%m-%d"),
            "Peso (kg)": weight
        }], WEIGHT_FILE)

if __name__ == "__main__":
    tracker = GymTracker()
    tracker.main_menu()