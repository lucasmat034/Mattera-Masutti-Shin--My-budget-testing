"""Fenêtre principale de l'application MyBudget."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional

from src.database.db_manager import DatabaseManager
from src.services.transaction_service import TransactionService
from src.services.budget_service import BudgetService
from src.services.statistics_service import StatisticsService
from src.services.export_service import ExportService


class MyBudgetApp:
    """Application graphique MyBudget."""
    
    def __init__(self, root: tk.Tk):
        """Initialise l'application."""
        self.root = root
        self.root.title("💰 MyBudget - Gestionnaire de Budget")
        self.root.geometry("1200x700")
        
        # Services
        self.db_manager = DatabaseManager()
        self.transaction_service = TransactionService(self.db_manager)
        self.budget_service = BudgetService(self.db_manager, self.transaction_service)
        self.stats_service = StatisticsService(self.db_manager, self.transaction_service)
        self.export_service = ExportService(self.transaction_service, self.db_manager)
        
        # Maps pour les catégories
        self.categories_map = {}
        self.budget_categories_map = {}
        
        # Configuration du style
        self.setup_style()
        
        # Création de l'interface
        self.create_menu()
        self.create_notebook()
        
        # Rafraîchir les données
        self.refresh_all()
    
    def setup_style(self):
        """Configure le style de l'application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Warning.TLabel', foreground='orange')
        style.configure('Danger.TLabel', foreground='red')
    
    def create_menu(self):
        """Crée la barre de menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Exporter CSV", command=self.export_csv)
        file_menu.add_command(label="Exporter JSON", command=self.export_json)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
    
    def create_notebook(self):
        """Crée les onglets principaux."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet Tableau de bord
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="📊 Tableau de bord")
        self.create_dashboard()
        
        # Onglet Transactions
        self.transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_frame, text="💸 Transactions")
        self.create_transactions_tab()
        
        # Onglet Budgets
        self.budgets_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.budgets_frame, text="💰 Budgets")
        self.create_budgets_tab()
        
        # Onglet Statistiques
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📈 Statistiques")
        self.create_stats_tab()
    
    def create_dashboard(self):
        """Crée le tableau de bord."""
        # Titre
        title = ttk.Label(self.dashboard_frame, text="Tableau de bord", style='Title.TLabel')
        title.pack(pady=20)
        
        # Frame pour les cartes de résumé
        cards_frame = ttk.Frame(self.dashboard_frame)
        cards_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Carte Revenus
        self.revenue_card = self.create_card(cards_frame, "💵 Revenus", "0.00 €", "Success.TLabel")
        self.revenue_card.pack(side=tk.LEFT, expand=True, padx=10)
        
        # Carte Dépenses
        self.expense_card = self.create_card(cards_frame, "💸 Dépenses", "0.00 €", "Danger.TLabel")
        self.expense_card.pack(side=tk.LEFT, expand=True, padx=10)
        
        # Carte Balance
        self.balance_card = self.create_card(cards_frame, "💰 Balance", "0.00 €", "Header.TLabel")
        self.balance_card.pack(side=tk.LEFT, expand=True, padx=10)
        
        # Liste des budgets
        budgets_label = ttk.Label(self.dashboard_frame, text="État des budgets", style='Header.TLabel')
        budgets_label.pack(pady=(20, 10))
        
        # Tableau des budgets
        self.dashboard_budgets_tree = self.create_budgets_tree(self.dashboard_frame)
        self.dashboard_budgets_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def create_card(self, parent, title: str, value: str, value_style: str) -> ttk.Frame:
        """Crée une carte de résumé."""
        card = ttk.LabelFrame(parent, text=title, padding=20)
        
        value_label = ttk.Label(card, text=value, style=value_style, font=('Helvetica', 24, 'bold'))
        value_label.pack()
        
        # Stocker le label pour mise à jour
        card.value_label = value_label
        
        return card
    
    def create_transactions_tab(self):
        """Crée l'onglet des transactions."""
        # Frame supérieur pour le formulaire
        form_frame = ttk.LabelFrame(self.transactions_frame, text="Ajouter une transaction", padding=10)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Formulaire
        row = 0
        
        # Montant
        ttk.Label(form_frame, text="Montant (€):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.amount_var, width=15).grid(row=row, column=1, padx=5, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.description_var, width=30).grid(row=row, column=3, padx=5, pady=5)
        
        row += 1
        
        # Type
        ttk.Label(form_frame, text="Type:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.type_var = tk.StringVar(value="dépense")
        type_combo = ttk.Combobox(form_frame, textvariable=self.type_var, values=["dépense", "revenu"], width=13, state='readonly')
        type_combo.grid(row=row, column=1, padx=5, pady=5)
        
        # Catégorie
        ttk.Label(form_frame, text="Catégorie:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, width=28, state='readonly')
        self.category_combo.grid(row=row, column=3, padx=5, pady=5)
        
        row += 1
        
        # Date
        ttk.Label(form_frame, text="Date (AAAA-MM-JJ):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(form_frame, textvariable=self.date_var, width=15).grid(row=row, column=1, padx=5, pady=5)
        
        # Bouton Ajouter
        ttk.Button(form_frame, text="➕ Ajouter", command=self.add_transaction).grid(row=row, column=3, padx=5, pady=5, sticky=tk.E)
        
        # Frame pour les filtres
        filter_frame = ttk.LabelFrame(self.transactions_frame, text="Filtres", padding=10)
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(filter_frame, text="Catégorie:").pack(side=tk.LEFT, padx=5)
        self.filter_category_var = tk.StringVar(value="Toutes")
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, width=20, state='readonly')
        self.filter_category_combo.pack(side=tk.LEFT, padx=5)
        self.filter_category_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_transactions())
        
        ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.filter_type_var = tk.StringVar(value="Tous")
        filter_type = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, values=["Tous", "dépense", "revenu"], width=15, state='readonly')
        filter_type.pack(side=tk.LEFT, padx=5)
        filter_type.bind('<<ComboboxSelected>>', lambda e: self.refresh_transactions())
        
        ttk.Button(filter_frame, text="🔄 Actualiser", command=self.refresh_transactions).pack(side=tk.LEFT, padx=20)
        ttk.Button(filter_frame, text="🗑️ Supprimer", command=self.delete_transaction).pack(side=tk.LEFT, padx=5)
        
        # Tableau des transactions
        self.transactions_tree = self.create_transactions_tree(self.transactions_frame)
        self.transactions_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Charger les catégories
        self.update_categories()
    
    def create_budgets_tab(self):
        """Crée l'onglet des budgets."""
        # Formulaire
        form_frame = ttk.LabelFrame(self.budgets_frame, text="Créer un budget", padding=10)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        row = 0
        
        # Catégorie
        ttk.Label(form_frame, text="Catégorie:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.budget_category_var = tk.StringVar()
        self.budget_category_combo = ttk.Combobox(form_frame, textvariable=self.budget_category_var, width=20, state='readonly')
        self.budget_category_combo.grid(row=row, column=1, padx=5, pady=5)
        
        # Montant
        ttk.Label(form_frame, text="Montant (€):").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        self.budget_amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.budget_amount_var, width=15).grid(row=row, column=3, padx=5, pady=5)
        
        row += 1
        
        # Date début
        ttk.Label(form_frame, text="Début (AAAA-MM-JJ):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.budget_start_var = tk.StringVar(value=date.today().replace(day=1).isoformat())
        ttk.Entry(form_frame, textvariable=self.budget_start_var, width=20).grid(row=row, column=1, padx=5, pady=5)
        
        # Date fin
        ttk.Label(form_frame, text="Fin (AAAA-MM-JJ):").grid(row=row, column=2, sticky=tk.W, padx=5, pady=5)
        last_day = date.today().replace(day=28)
        self.budget_end_var = tk.StringVar(value=last_day.isoformat())
        ttk.Entry(form_frame, textvariable=self.budget_end_var, width=15).grid(row=row, column=3, padx=5, pady=5)
        
        # Bouton Créer
        ttk.Button(form_frame, text="➕ Créer Budget", command=self.create_budget).grid(row=row, column=4, padx=5, pady=5)
        
        # Tableau des budgets
        self.budgets_tree = self.create_budgets_tree(self.budgets_frame)
        self.budgets_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Charger les catégories
        self.update_budget_categories()
    
    def create_stats_tab(self):
        """Crée l'onglet des statistiques."""
        # Sélection de période
        period_frame = ttk.LabelFrame(self.stats_frame, text="Période", padding=10)
        period_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(period_frame, text="Année:").pack(side=tk.LEFT, padx=5)
        self.stats_year_var = tk.StringVar(value=str(date.today().year))
        ttk.Entry(period_frame, textvariable=self.stats_year_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(period_frame, text="Mois:").pack(side=tk.LEFT, padx=5)
        self.stats_month_var = tk.StringVar(value=str(date.today().month))
        ttk.Entry(period_frame, textvariable=self.stats_month_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(period_frame, text="📊 Calculer", command=self.refresh_stats).pack(side=tk.LEFT, padx=20)
        
        # Résultats
        self.stats_text = tk.Text(self.stats_frame, height=25, wrap=tk.WORD, font=('Courier', 11))
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(self.stats_text, command=self.stats_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stats_text.config(yscrollcommand=scrollbar.set)
    
    def create_transactions_tree(self, parent) -> ttk.Treeview:
        """Crée un tableau pour les transactions."""
        columns = ('ID', 'Date', 'Type', 'Catégorie', 'Description', 'Montant')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        # En-têtes
        tree.heading('ID', text='ID')
        tree.heading('Date', text='Date')
        tree.heading('Type', text='Type')
        tree.heading('Catégorie', text='Catégorie')
        tree.heading('Description', text='Description')
        tree.heading('Montant', text='Montant')
        
        # Largeurs
        tree.column('ID', width=50)
        tree.column('Date', width=100)
        tree.column('Type', width=100)
        tree.column('Catégorie', width=120)
        tree.column('Description', width=250)
        tree.column('Montant', width=120)
        
        return tree
    
    def create_budgets_tree(self, parent) -> ttk.Treeview:
        """Crée un tableau pour les budgets."""
        columns = ('Catégorie', 'Budget', 'Dépensé', 'Restant', 'Pourcentage', 'Statut')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        # En-têtes
        tree.heading('Catégorie', text='Catégorie')
        tree.heading('Budget', text='Budget')
        tree.heading('Dépensé', text='Dépensé')
        tree.heading('Restant', text='Restant')
        tree.heading('Pourcentage', text='%')
        tree.heading('Statut', text='Statut')
        
        # Largeurs
        tree.column('Catégorie', width=150)
        tree.column('Budget', width=120)
        tree.column('Dépensé', width=120)
        tree.column('Restant', width=120)
        tree.column('Pourcentage', width=100)
        tree.column('Statut', width=150)
        
        return tree
    
    def update_categories(self):
        """Met à jour la liste des catégories disponibles."""
        query = "SELECT id, name FROM categories ORDER BY name"
        results = self.db_manager.execute_query(query)
        
        self.categories_map = {row['name']: row['id'] for row in results}
        categories = list(self.categories_map.keys())
        
        if categories:
            self.category_combo['values'] = categories
            self.category_combo.current(0)
            
            filter_categories = ["Toutes"] + categories
            self.filter_category_combo['values'] = filter_categories
            self.filter_category_combo.current(0)
    
    def update_budget_categories(self):
        """Met à jour la liste des catégories pour les budgets."""
        query = "SELECT id, name FROM categories ORDER BY name"
        results = self.db_manager.execute_query(query)
        
        self.budget_categories_map = {row['name']: row['id'] for row in results}
        categories = list(self.budget_categories_map.keys())
        
        if categories:
            self.budget_category_combo['values'] = categories
            self.budget_category_combo.current(0)
    
    def add_transaction(self):
        """Ajoute une nouvelle transaction."""
        try:
            amount = float(self.amount_var.get())
            description = self.description_var.get().strip()
            transaction_type = self.type_var.get()
            category_name = self.category_var.get()
            transaction_date = datetime.strptime(self.date_var.get(), '%Y-%m-%d').date()
            
            if not description:
                messagebox.showerror("Erreur", "La description est obligatoire")
                return
            
            category_id = self.categories_map.get(category_name)
            if not category_id:
                messagebox.showerror("Erreur", "Catégorie invalide")
                return
            
            from src.models.transaction import Transaction
            transaction = Transaction(
                amount=amount,
                description=description,
                type=transaction_type,
                category_id=category_id,
                date=transaction_date
            )
            
            transaction_id = self.transaction_service.add_transaction(transaction)
            
            messagebox.showinfo("Succès", f"Transaction ajoutée (ID: {transaction_id})")
            
            # Réinitialiser le formulaire
            self.amount_var.set("")
            self.description_var.set("")
            self.date_var.set(date.today().isoformat())
            
            # Rafraîchir
            self.refresh_all()
            
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
    
    def delete_transaction(self):
        """Supprime la transaction sélectionnée."""
        selection = self.transactions_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une transaction")
            return
        
        item = self.transactions_tree.item(selection[0])
        transaction_id = int(item['values'][0])
        
        if messagebox.askyesno("Confirmation", f"Supprimer la transaction {transaction_id} ?"):
            try:
                self.transaction_service.delete_transaction(transaction_id)
                messagebox.showinfo("Succès", "Transaction supprimée")
                self.refresh_all()
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))
    
    def create_budget(self):
        """Crée un nouveau budget."""
        try:
            category_name = self.budget_category_var.get()
            amount = float(self.budget_amount_var.get())
            start_date = datetime.strptime(self.budget_start_var.get(), '%Y-%m-%d').date()
            end_date = datetime.strptime(self.budget_end_var.get(), '%Y-%m-%d').date()
            
            category_id = self.budget_categories_map.get(category_name)
            if not category_id:
                messagebox.showerror("Erreur", "Catégorie invalide")
                return
            
            from src.models.budget import Budget
            budget = Budget(
                category_id=category_id,
                amount=amount,
                period_start=start_date,
                period_end=end_date
            )
            
            budget_id = self.budget_service.create_budget(budget)
            
            messagebox.showinfo("Succès", f"Budget créé (ID: {budget_id})")
            
            # Réinitialiser
            self.budget_amount_var.set("")
            
            # Rafraîchir
            self.refresh_all()
            
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
    
    def refresh_transactions(self):
        """Rafraîchit la liste des transactions."""
        # Vider le tableau
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Récupérer le mapping des catégories
        query = "SELECT id, name FROM categories"
        results = self.db_manager.execute_query(query)
        categories_map = {row['id']: row['name'] for row in results}
        
        # Filtres
        category_filter = self.filter_category_var.get()
        type_filter = self.filter_type_var.get()
        
        # Récupérer les transactions
        transactions = self.transaction_service.list_transactions()
        
        # Appliquer les filtres
        if category_filter != "Toutes":
            category_id = self.categories_map.get(category_filter)
            if category_id:
                transactions = [t for t in transactions if t.category_id == category_id]
        
        if type_filter != "Tous":
            transactions = [t for t in transactions if t.type == type_filter]
        
        # Remplir le tableau
        for t in reversed(transactions):
            category_name = categories_map.get(t.category_id, "inconnu")
            montant = f"{t.amount:.2f} €"
            if t.type == "revenu":
                montant = f"+{montant}"
            else:
                montant = f"-{montant}"
            
            self.transactions_tree.insert('', tk.END, values=(
                t.id,
                t.date,
                t.type,
                category_name,
                t.description,
                montant
            ))
    
    def refresh_budgets(self, tree: ttk.Treeview):
        """Rafraîchit le tableau des budgets."""
        # Vider
        for item in tree.get_children():
            tree.delete(item)
        
        # Récupérer les budgets actifs
        budgets = self.budget_service.list_budgets()
        
        # Récupérer les catégories
        categories_query = "SELECT id, name FROM categories"
        categories_results = self.db_manager.execute_query(categories_query)
        categories_map = {row['id']: row['name'] for row in categories_results}
        
        for budget in budgets:
            category_name = categories_map.get(budget.category_id, "inconnu")
            
            status = self.budget_service.get_budget_status(
                budget.category_id,
                budget.period_start,
                budget.period_end
            )
            
            if status:
                percentage = status['percentage']
                
                # Déterminer le statut
                if percentage >= 100:
                    statut = "🔴 Dépassé"
                elif percentage >= 90:
                    statut = "⚠️ Attention"
                else:
                    statut = "✅ OK"
                
                tree.insert('', tk.END, values=(
                    category_name.capitalize(),
                    f"{budget.amount:.2f} €",
                    f"{status['spent']:.2f} €",
                    f"{status['remaining']:.2f} €",
                    f"{percentage:.1f}%",
                    statut
                ))
    
    def refresh_dashboard(self):
        """Rafraîchit le tableau de bord."""
        # Calculer les totaux
        all_transactions = self.transaction_service.list_transactions()
        
        total_revenue = sum(t.amount for t in all_transactions if t.type == "revenu")
        total_expense = sum(t.amount for t in all_transactions if t.type == "dépense")
        balance = total_revenue - total_expense
        
        # Mettre à jour les cartes
        self.revenue_card.value_label.config(text=f"{total_revenue:.2f} €")
        self.expense_card.value_label.config(text=f"{total_expense:.2f} €")
        self.balance_card.value_label.config(text=f"{balance:.2f} €")
        
        # Mettre à jour les budgets
        self.refresh_budgets(self.dashboard_budgets_tree)
    
    def refresh_stats(self):
        """Rafraîchit les statistiques."""
        try:
            year = int(self.stats_year_var.get())
            month = int(self.stats_month_var.get())
            
            # Effacer le texte
            self.stats_text.delete('1.0', tk.END)
            
            # Résumé mensuel
            summary = self.stats_service.get_monthly_summary(year, month)
            self.stats_text.insert(tk.END, "📊 RÉSUMÉ MENSUEL\n")
            self.stats_text.insert(tk.END, "=" * 60 + "\n\n")
            self.stats_text.insert(tk.END, f"Revenus:     {summary['total_income']:.2f} €\n")
            self.stats_text.insert(tk.END, f"Dépenses:    {summary['total_expenses']:.2f} €\n")
            self.stats_text.insert(tk.END, f"Balance:     {summary['balance']:.2f} €\n")
            self.stats_text.insert(tk.END, f"Transactions: {summary['transaction_count']}\n\n")
            
            # Par catégorie
            self.stats_text.insert(tk.END, "📂 PAR CATÉGORIE\n")
            self.stats_text.insert(tk.END, "=" * 60 + "\n\n")
            for cat, amount in summary['by_category'].items():
                self.stats_text.insert(tk.END, f"{cat.capitalize():20s} {amount:>10.2f} €\n")
            
            # Moyenne quotidienne
            self.stats_text.insert(tk.END, f"\n\n📅 MOYENNE QUOTIDIENNE\n")
            self.stats_text.insert(tk.END, "=" * 60 + "\n\n")
            avg = self.stats_service.get_average_daily_spending(year, month)
            self.stats_text.insert(tk.END, f"Dépenses moyennes par jour: {avg:.2f} €\n")
            
            # Prédiction
            self.stats_text.insert(tk.END, f"\n\n🔮 PRÉDICTION FIN DE MOIS\n")
            self.stats_text.insert(tk.END, "=" * 60 + "\n\n")
            prediction = self.stats_service.predict_end_of_month_spending(year, month)
            self.stats_text.insert(tk.END, f"Dépenses prévues: {prediction:.2f} €\n")
            
        except Exception as e:
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert(tk.END, f"Erreur: {str(e)}")
    
    def refresh_all(self):
        """Rafraîchit toutes les données."""
        self.refresh_dashboard()
        self.refresh_transactions()
        self.refresh_budgets(self.budgets_tree)
    
    def export_csv(self):
        """Exporte les transactions en CSV."""
        try:
            filename = f"transactions_{date.today().isoformat()}.csv"
            self.export_service.export_transactions_to_csv(filename)
            messagebox.showinfo("Succès", f"Exporté vers {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def export_json(self):
        """Exporte les transactions en JSON."""
        try:
            filename = f"transactions_{date.today().isoformat()}.json"
            self.export_service.export_transactions_to_json(filename)
            messagebox.showinfo("Succès", f"Exporté vers {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def show_about(self):
        """Affiche la boîte À propos."""
        messagebox.showinfo(
            "À propos",
            "MyBudget v1.0\n\n"
            "Gestionnaire de budget personnel\n\n"
            "Développé par:\n"
            "Mattera, Masutti, Shin\n\n"
            "© 2026 - MIT License"
        )


def main():
    """Point d'entrée de l'application."""
    root = tk.Tk()
    app = MyBudgetApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
