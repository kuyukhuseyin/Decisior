import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math

class Decisior:
    def __init__(self, root):
        self.root = root
        self.root.title("Decisior")
        self.root.geometry("500x400")
        self.root.resizable(True, True)

        # Variables
        self.criteriaList = []
        self.alternativeList = []
        self.matrix = []
        self.priority_vector = []
        self.decision_matrix = []

        # Creating a main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Criteria page
        self.criteria_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.criteria_frame, text="Criteria")

        # Comparison matrix page
        self.comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.comparison_frame, text="Criteria Comparison")

        # Alternatives page
        self.alternatives_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alternatives_frame, text="Alternatives")

        # Decision matrix page
        self.decision_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.decision_frame, text="Decision Matrix")

        # Results page
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")

        # Set criteria
        self.setup_criteria_page()

    def setup_criteria_page(self):
        frame = ttk.LabelFrame(self.criteria_frame, text="Enter Number and Names of Criteria")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Number of Criteria:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.criteria_count = ttk.Spinbox(frame, from_=2, to=10, width=5)
        self.criteria_count.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.criteria_count.set(3)

        ttk.Button(frame, text="Create Criteria", command=self.create_criteria_fields).grid(row=0, column=2, padx=5,
                                                                                               pady=5)

        self.criteria_container = ttk.Frame(frame)
        self.criteria_container.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

        info_text = "Saaty 1-9 Scale Information:\n1: Equal importance\n3: Medium importance\n5: Strong importance\n7: Very strong importance\n9: Extreme importance\n2,4,6,8: Intermediate values"
        ttk.Label(frame, text=info_text).grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

    def create_criteria_fields(self):
        # Clear current content
        for widget in self.criteria_container.winfo_children():
            widget.destroy()

        try:
            count = int(self.criteria_count.get())
            if count < 2 or count > 10:
                messagebox.showerror("Error", "The number of criteria must be between 2 and 10.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        self.criteria_entries = []

        for i in range(count):
            ttk.Label(self.criteria_container, text=f"Criteria {i + 1}:").grid(row=i, column=0, padx=5, pady=2,
                                                                             sticky=tk.W)
            entry = ttk.Entry(self.criteria_container, width=20)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky=tk.W)
            self.criteria_entries.append(entry)

        # Create a frame for the button
        button_frame = ttk.Frame(self.criteria_container)
        button_frame.grid(row=count, column=0, columnspan=2, padx=5, pady=10)

        # Create Comparison Matrix button
        karsilastirma_btn = ttk.Button(button_frame, text="Create Comparison Matrix",
                   command=lambda: self.create_comparison_matrix_and_switch())
        karsilastirma_btn.pack(side=tk.LEFT, padx=5)

    def create_comparison_matrix_and_switch(self):
        """Create the comparison matrix and move on to the next tab"""
        self.create_comparison_matrix()

        self.notebook.select(1)

    def create_comparison_matrix(self):
        # Save criteria
        self.criteriaList = []
        for entry in self.criteria_entries:
            text = entry.get().strip()
            if not text:
                messagebox.showerror("Error", "Enter the names of all criteria.")
                return
            self.criteriaList.append(text)

        # Clear comparison page
        for widget in self.comparison_frame.winfo_children():
            widget.destroy()

        frame = ttk.LabelFrame(self.comparison_frame, text="Criteria Comparison Matrix")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        criteriaPcs = len(self.criteriaList)
        self.comparison_entries = []

        # Header line
        ttk.Label(frame, text="", width=10).grid(row=0, column=0)
        for j in range(criteriaPcs):
            ttk.Label(frame, text=self.criteriaList[j], width=10).grid(row=0, column=j + 1, padx=2, pady=2)

        # Main matrix
        for i in range(criteriaPcs):
            ttk.Label(frame, text=self.criteriaList[i], width=10).grid(row=i + 1, column=0, padx=2, pady=2)
            row_entries = []
            for j in range(criteriaPcs):
                entry = ttk.Entry(frame, width=8)
                entry.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                if i == j:  # Diagonal
                    entry.insert(0, "1")
                    entry.config(state="readonly")
                elif i > j:  # Bottom triangle
                    entry.insert(0, "")
                    # Update upper triangle when lower triangle changes
                    entry.bind("<FocusOut>", lambda event, row=i, col=j: self.update_upper_triangle(event, row, col))
                else:  # Upper triangle
                    entry.insert(0, "")
                    # Update lower triangle when upper triangle changes
                    entry.bind("<FocusOut>", lambda event, row=i, col=j: self.update_lower_triangle(event, row, col))
                row_entries.append(entry)
            self.comparison_entries.append(row_entries)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=criteriaPcs + 1, column=0, columnspan=criteriaPcs + 1, padx=5, pady=10)

        ttk.Button(button_frame, text="Calculate and Next",
                   command=self.calculate_priorities).pack(side=tk.LEFT, padx=5)

    def update_upper_triangle(self, event, row, col):
        """Update the upper triangle with changes in the lower triangle"""
        try:
            value = float(self.comparison_entries[row][col].get())
            if value <= 0:
                messagebox.showerror("Error", "The value must be positive.")
                return
            # Reciprocal value for upper triangle
            reciprocal = 1 / value
            # Update upper triangle entry
            self.comparison_entries[col][row].config(state="normal")
            self.comparison_entries[col][row].delete(0, tk.END)
            self.comparison_entries[col][row].insert(0, f"{reciprocal:.3f}")
            self.comparison_entries[col][row].config(state="normal")
        except ValueError:
            # Clear the upper element if lower is empty or invalid
            self.comparison_entries[col][row].config(state="normal")
            self.comparison_entries[col][row].delete(0, tk.END)
            self.comparison_entries[col][row].config(state="normal")

    def update_lower_triangle(self, event, row, col):
        """Update the lower triangle with changes in the upper triangle"""
        try:
            value = float(self.comparison_entries[row][col].get())
            if value <= 0:
                messagebox.showerror("Error", "The value must be positive.")
                return
            # Reciprocal value for lower triangle
            reciprocal = 1 / value
            # Update lower triangle entry
            self.comparison_entries[col][row].config(state="normal")
            self.comparison_entries[col][row].delete(0, tk.END)
            self.comparison_entries[col][row].insert(0, f"{reciprocal:.3f}")
            self.comparison_entries[col][row].config(state="normal")
        except ValueError:
            # Clear the lower element if upper is empty or invalid
            self.comparison_entries[col][row].config(state="normal")
            self.comparison_entries[col][row].delete(0, tk.END)
            self.comparison_entries[col][row].config(state="normal")

    def calculate_priorities(self):
        criteriaPcs = len(self.criteriaList)

        # Create the matrix
        self.matrix = [[1 if i == j else None for j in range(criteriaPcs)] for i in range(criteriaPcs)]

        # Fill the lower triangle
        for i in range(1, criteriaPcs):
            for j in range(i):
                try:
                    value = float(self.comparison_entries[i][j].get())
                    if value <= 0:
                        messagebox.showerror("Error", "All values must be positive.")
                        return
                    self.matrix[i][j] = value
                    self.matrix[j][i] = 1 / value
                except ValueError:
                    messagebox.showerror("Error", "Enter all comparison values.")
                    return

        # Column totals
        col_sums = [sum(self.matrix[i][j] for i in range(criteriaPcs)) for j in range(criteriaPcs)]

        # Normalized matrix
        normalized_matrix = [[self.matrix[i][j] / col_sums[j] for j in range(criteriaPcs)] for i in range(criteriaPcs)]

        # Eigenvector (priority vector)
        self.priority_vector = [sum(row) / criteriaPcs for row in normalized_matrix]

        # Calculate lambda max
        weighted_sum_vector = []
        for i in range(criteriaPcs):
            weighted_sum = sum(self.matrix[i][j] * self.priority_vector[j] for j in range(criteriaPcs))
            weighted_sum_vector.append(weighted_sum)

        lambda_max = sum(weighted_sum_vector[i] / self.priority_vector[i] for i in range(criteriaPcs)) / criteriaPcs

        # Calculate CI and CR
        CI = (lambda_max - criteriaPcs) / (criteriaPcs - 1) if criteriaPcs > 1 else 0

        RI_table = {
            1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
        }
        RI = RI_table.get(criteriaPcs, 1.49)

        CR = CI / RI if RI > 0 else 0

        # Show results
        result_frame = ttk.LabelFrame(self.comparison_frame, text="AHP Results")
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        results_text = scrolledtext.ScrolledText(result_frame, width=80, height=15)
        results_text.pack(fill="both", expand=True, padx=5, pady=5)

        results_text.insert(tk.END, "AHP Comparison Matrix:\n")
        header = "        " + "  ".join(f"{c:^7}" for c in self.criteriaList) + "\n"
        results_text.insert(tk.END, header)

        for i, row in enumerate(self.matrix):
            row_str = "  ".join(f"{val:^7.3f}" for val in row)
            results_text.insert(tk.END, f"{self.criteriaList[i]:<7} {row_str}\n")

        results_text.insert(tk.END, f"\nPriority vector : {self.priority_vector}\n")
        results_text.insert(tk.END, f"\nλ max : {lambda_max:.3f}\n")
        results_text.insert(tk.END, f"Consistency Index (CI): {CI:.3f}\n")
        results_text.insert(tk.END, f"Consistency Ratio (CR): {CR:.3f}\n")

        # Show consistency status
        if CR >= 0.10:
            results_text.insert(tk.END, "Consistency status: ❌ INCONSISTENT (CR >= 0.10)")
            messagebox.showwarning("Inconsistency Warning",
                                   "Comparison matrix is inconsistent (CR >= 0.10). It is recommended that you review the values.")
        else:
            results_text.insert(tk.END, "Consistency status: ✅ CONSISTENT (CR < 0.10)\n")


        for widget in self.comparison_frame.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                for inner_widget in widget.winfo_children():
                    if isinstance(inner_widget, ttk.Frame):
                        ttk.Button(inner_widget, text="Go to alternatives",
                                  command=lambda: self.setup_alternatives_page_and_switch()).pack(side=tk.LEFT, padx=5)
                        break
                break

    def setup_alternatives_page_and_switch(self):
        """Set the alternatives page and move on to the next tab"""
        self.setup_alternatives_page()
        self.notebook.select(2)

    def setup_alternatives_page(self):
        for widget in self.alternatives_frame.winfo_children():
            widget.destroy()

        frame = ttk.LabelFrame(self.alternatives_frame, text="Enter Alternatives")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Number of Alternatives:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.alternative_count = ttk.Spinbox(frame, from_=2, to=10, width=5)
        self.alternative_count.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.alternative_count.set(3)

        ttk.Button(frame, text="Create Alternatives",
                   command=self.create_alternative_fields).grid(row=0, column=2, padx=5, pady=5)

        self.alternative_container = ttk.Frame(frame)
        self.alternative_container.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W + tk.E)

    def create_alternative_fields(self):
        for widget in self.alternative_container.winfo_children():
            widget.destroy()

        try:
            count = int(self.alternative_count.get())
            if count < 2 or count > 10:
                messagebox.showerror("Error", "The number of alternatives must be between 2 and 10.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        self.alternative_entries = []

        for i in range(count):
            ttk.Label(self.alternative_container, text=f"Alternative {i + 1}:").grid(row=i, column=0, padx=5, pady=2,
                                                                                    sticky=tk.W)
            entry = ttk.Entry(self.alternative_container, width=20)
            entry.grid(row=i, column=1, padx=5, pady=2, sticky=tk.W)
            self.alternative_entries.append(entry)

        ttk.Button(self.alternative_container, text="Create Decision Matrix",
                   command=lambda: self.create_decision_matrix_and_switch()).grid(row=count, column=0, columnspan=2, padx=5, pady=10)

    def create_decision_matrix_and_switch(self):
        """Create the decision matrix and move on to the next tab"""
        self.create_decision_matrix()
        self.notebook.select(3)

    def create_decision_matrix(self):
        self.alternativeList = []
        for entry in self.alternative_entries:
            text = entry.get().strip()
            if not text:
                messagebox.showerror("Error", "Enter the names of all alternatives.")
                return
            self.alternativeList.append(text)

        for widget in self.decision_frame.winfo_children():
            widget.destroy()

        frame = ttk.LabelFrame(self.decision_frame, text="Decision Matrix")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        alternativePcs = len(self.alternativeList)
        criteriaPcs = len(self.criteriaList)

        ttk.Label(frame, text="", width=10).grid(row=0, column=0)
        for j in range(criteriaPcs):
            ttk.Label(frame, text=self.criteriaList[j], width=10).grid(row=0, column=j + 1, padx=2, pady=2)

        self.decision_entries = []
        for i in range(alternativePcs):
            ttk.Label(frame, text=self.alternativeList[i], width=10).grid(row=i + 1, column=0, padx=2, pady=2)
            row_entries = []
            for j in range(criteriaPcs):
                entry = ttk.Entry(frame, width=8)
                entry.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                row_entries.append(entry)
            self.decision_entries.append(row_entries)

        ttk.Label(frame, text="Enter a value between 0-10 for each criterion.").grid(
            row=alternativePcs + 1, column=0, columnspan=criteriaPcs + 1, pady=5)

        ttk.Button(frame, text="Perform TOPSIS Analysis",
                   command=lambda: self.run_topsis_and_switch()).grid(row=alternativePcs + 2, column=0, columnspan=criteriaPcs + 1, padx=5,
                                                 pady=10)

    def run_topsis_and_switch(self):
        """Perform TOPSIS analysis and move on to the next tab"""
        self.run_topsis()
        self.notebook.select(4)

    def run_topsis(self):
        alternativePcs = len(self.alternativeList)
        criteriaPcs = len(self.criteriaList)

        self.decision_matrix = []
        for i in range(alternativePcs):
            row = []
            for j in range(criteriaPcs):
                try:
                    value = float(self.decision_entries[i][j].get())
                    if value < 0 or value > 10:
                        messagebox.showerror("Error", "All values must be between 0-10.")
                        return
                    row.append(value)
                except ValueError:
                    messagebox.showerror("Error", "Enter all decision matrix values.")
                    return
            self.decision_matrix.append(row)

        # Perform TOPSIS calculations and display results
        self.calculate_topsis_results()

    def calculate_topsis_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        frame = ttk.LabelFrame(self.results_frame, text="TOPSIS Analysis Results")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        results_text = scrolledtext.ScrolledText(frame, width=80, height=25)
        results_text.pack(fill="both", expand=True, padx=5, pady=5)

        alternativePcs = len(self.alternativeList)
        criteriaPcs = len(self.criteriaList)

        results_text.insert(tk.END, "Decision Matrix:\n")
        header = "        " + "  ".join(f"{c:^7}" for c in self.criteriaList) + "\n"
        results_text.insert(tk.END, header)

        for i, row in enumerate(self.decision_matrix):
            row_str = "  ".join(f"{val:^7.2f}" for val in row)
            results_text.insert(tk.END, f"{self.alternativeList[i]:<7} {row_str}\n")

        normalized_decision_matrix = []
        for i in range(alternativePcs):
            normalized_row = []
            for j in range(criteriaPcs):
                col_sum_squares = sum(self.decision_matrix[k][j] ** 2 for k in range(alternativePcs))
                normalized_value = self.decision_matrix[i][j] / math.sqrt(col_sum_squares)
                normalized_row.append(normalized_value)
            normalized_decision_matrix.append(normalized_row)

        results_text.insert(tk.END, "\nNormalized Decision Matrix:\n")
        results_text.insert(tk.END, header)

        for i, row in enumerate(normalized_decision_matrix):
            row_str = "  ".join(f"{val:^7.3f}" for val in row)
            results_text.insert(tk.END, f"{self.alternativeList[i]:<7} {row_str}\n")

        weighted_decision_matrix = []
        for i in range(alternativePcs):
            weighted_row = [normalized_decision_matrix[i][j] * self.priority_vector[j] for j in range(criteriaPcs)]
            weighted_decision_matrix.append(weighted_row)

        results_text.insert(tk.END, "\nWeighted Normalized Decision Matrix:\n")
        results_text.insert(tk.END, header)

        for i, row in enumerate(weighted_decision_matrix):
            row_str = "  ".join(f"{val:^7.3f}" for val in row)
            results_text.insert(tk.END, f"{self.alternativeList[i]:<7} {row_str}\n")

        # Ideal solutions
        ideal_positive = [max(weighted_decision_matrix[i][j] for i in range(alternativePcs)) for j in
                          range(criteriaPcs)]
        ideal_negative = [min(weighted_decision_matrix[i][j] for i in range(alternativePcs)) for j in
                          range(criteriaPcs)]

        results_text.insert(tk.END, "\nPositive Ideal Solution (A+):\n")
        results_text.insert(tk.END, "        " + "  ".join(f"{val:^7.3f}" for val in ideal_positive) + "\n")

        results_text.insert(tk.END, "\nNegative Ideal Solution (A-):\n")
        results_text.insert(tk.END, "        " + "  ".join(f"{val:^7.3f}" for val in ideal_negative) + "\n")

        distance_positive = []
        distance_negative = []

        for i in range(alternativePcs):
            dist_pos = math.sqrt(
                sum((weighted_decision_matrix[i][j] - ideal_positive[j]) ** 2 for j in range(criteriaPcs)))
            dist_neg = math.sqrt(
                sum((weighted_decision_matrix[i][j] - ideal_negative[j]) ** 2 for j in range(criteriaPcs)))
            distance_positive.append(dist_pos)
            distance_negative.append(dist_neg)

        results_text.insert(tk.END, "\nDistances to Ideal Solutions:\n")
        for i in range(alternativePcs):
            results_text.insert(tk.END,
                                f"{self.alternativeList[i]:<7} S+ = {distance_positive[i]:.3f}, S- = {distance_negative[i]:.3f}\n")

        # Scores and ranks
        preference_scores = [distance_negative[i] / (distance_positive[i] + distance_negative[i]) for i in
                             range(alternativePcs)]

        results_text.insert(tk.END, "\nScores (C+) and Ranking:\n")
        sorted_alternatives = sorted(zip(self.alternativeList, preference_scores), key=lambda x: x[1], reverse=True)

        for rank, (alt, score) in enumerate(sorted_alternatives, start=1):
            results_text.insert(tk.END, f"{rank}. {alt:<7} - Puan: {score:.3f}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = Decisior(root)
    root.mainloop()