import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import db
from datetime import datetime


def refresh_tree():
    for row in tree.get_children():
        tree.delete(row)
    for r in db.list_expenses():
        # r = (id, amount, date, category, notes, payment_method, type)
        tree.insert('', 'end', iid=r[0], values=(r[1], r[2], r[3], r[4], r[5], r[6]))
    # update totals
    cash_total = db.get_total_by_payment_method('cash')
    online_total = db.get_total_by_payment_method('online')
    cash_label_var.set(f"Cash: {cash_total:.2f}")
    online_label_var.set(f"Online: {online_total:.2f}")


def add_expense(entry_type='out'):
    amt = amount_var.get().strip()
    d = date_var.get().strip()
    cat = category_var.get().strip()
    notes = notes_var.get().strip()
    pay = payment_var.get().strip()

    try:
        amt_f = float(amt)
    except Exception:
        messagebox.showerror('Invalid', 'Please enter a valid amount (e.g. 12.50)')
        return

    # very simple date validation (YYYY-MM-DD)
    try:
        datetime.strptime(d, '%Y-%m-%d')
    except Exception:
        messagebox.showerror('Invalid', 'Please enter date as YYYY-MM-DD')
        return

    db.add_expense(amt_f, d, cat, notes, pay, entry_type)
    amount_var.set('')
    notes_var.set('')
    refresh_tree()


def delete_selected():
    sel = tree.selection()
    if not sel:
        messagebox.showinfo('Delete', 'Select an expense to delete')
        return
    eid = int(sel[0])
    if not messagebox.askyesno('Confirm', 'Delete selected expense?'):
        return
    db.delete_expense(eid)
    refresh_tree()


def export_csv():
    path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV', '*.csv')])
    if not path:
        return
    db.export_csv(path)
    messagebox.showinfo('Export', f'Exported to {path}')


def confirm_and_add(amount, date_s, category, notes, payment, entry_type):
    # validate amount
    try:
        amt_f = float(amount)
    except Exception:
        messagebox.showerror('Invalid', 'Please enter a valid amount (e.g. 12.50)')
        return False
    # validate date
    try:
        datetime.strptime(date_s, '%Y-%m-%d')
    except Exception:
        messagebox.showerror('Invalid', 'Please enter date as YYYY-MM-DD')
        return False

    db.add_expense(amt_f, date_s, category, notes, payment, entry_type)
    refresh_tree()
    return True


def open_confirm_dialog(entry_type='out'):
    # create a small modal dialog to review/edit before saving
    dlg = tk.Toplevel()
    dlg.title('Confirm entry')
    dlg.transient()
    dlg.grab_set()

    ttk.Label(dlg, text=f'Type: {entry_type}').grid(row=0, column=0, columnspan=2, pady=(8, 4))

    ttk.Label(dlg, text='Amount').grid(row=1, column=0, sticky='w')
    a_var = tk.StringVar(value=amount_var.get())
    ttk.Entry(dlg, textvariable=a_var).grid(row=1, column=1, sticky='we')

    ttk.Label(dlg, text='Date (YYYY-MM-DD)').grid(row=2, column=0, sticky='w')
    d_var = tk.StringVar(value=date_var.get())
    ttk.Entry(dlg, textvariable=d_var).grid(row=2, column=1, sticky='we')

    ttk.Label(dlg, text='Category').grid(row=3, column=0, sticky='w')
    c_var = tk.StringVar(value=category_var.get())
    ttk.Entry(dlg, textvariable=c_var).grid(row=3, column=1, sticky='we')

    ttk.Label(dlg, text='Notes').grid(row=4, column=0, sticky='w')
    n_var = tk.StringVar(value=notes_var.get())
    ttk.Entry(dlg, textvariable=n_var).grid(row=4, column=1, sticky='we')

    ttk.Label(dlg, text='Payment').grid(row=5, column=0, sticky='w')
    p_var = tk.StringVar(value=payment_var.get())
    p_cb = ttk.Combobox(dlg, textvariable=p_var, values=['cash', 'online', 'card', 'other'], state='readonly')
    p_cb.grid(row=5, column=1, sticky='we')

    btns = ttk.Frame(dlg)
    btns.grid(row=6, column=0, columnspan=2, pady=8)

    def on_confirm():
        ok = confirm_and_add(a_var.get(), d_var.get(), c_var.get(), n_var.get(), p_var.get(), entry_type)
        if ok:
            dlg.grab_release()
            dlg.destroy()

    def on_cancel():
        dlg.grab_release()
        dlg.destroy()

    ttk.Button(btns, text='Confirm', command=on_confirm).grid(row=0, column=0, padx=6)
    ttk.Button(btns, text='Cancel', command=on_cancel).grid(row=0, column=1, padx=6)

    # make the dialog size fit and center
    dlg.columnconfigure(1, weight=1)
    dlg.wait_window()


def show_monthly_summary():
    rows = db.get_monthly_summary()
    s = '\n'.join([f"{r[0]} : {r[1]:.2f}" for r in rows])
    if not s:
        s = '(no data)'
    messagebox.showinfo('Monthly summary', s)


if __name__ == '__main__':
    db.init_db()

    root = tk.Tk()
    root.title('Expense Tracker')

    # top: totals
    top_frame = ttk.Frame(root, padding=8)
    top_frame.grid(row=0, column=0, sticky='we')
    cash_label_var = tk.StringVar(value='Cash: 0.00')
    online_label_var = tk.StringVar(value='Online: 0.00')
    ttk.Label(top_frame, textvariable=cash_label_var, font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=8)
    ttk.Label(top_frame, textvariable=online_label_var, font=('Segoe UI', 12, 'bold')).grid(row=0, column=1, sticky='e', padx=8)

    frm = ttk.Frame(root, padding=10)
    frm.grid(row=1, column=0, sticky='nsew')

    # inputs + calculator
    left = ttk.Frame(frm)
    left.grid(row=0, column=0, sticky='n')

    ttk.Label(left, text='Amount').grid(row=0, column=0, sticky='w')
    amount_var = tk.StringVar()
    amt_entry = ttk.Entry(left, textvariable=amount_var, width=20)
    amt_entry.grid(row=0, column=1, sticky='we')

    ttk.Label(left, text='Date (YYYY-MM-DD)').grid(row=1, column=0, sticky='w')
    date_var = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))
    ttk.Entry(left, textvariable=date_var).grid(row=1, column=1, sticky='we')

    ttk.Label(left, text='Category').grid(row=2, column=0, sticky='w')
    category_var = tk.StringVar()
    ttk.Entry(left, textvariable=category_var).grid(row=2, column=1, sticky='we')

    ttk.Label(left, text='Notes').grid(row=3, column=0, sticky='w')
    notes_var = tk.StringVar()
    ttk.Entry(left, textvariable=notes_var).grid(row=3, column=1, sticky='we')

    ttk.Label(left, text='Payment').grid(row=4, column=0, sticky='w')
    payment_var = tk.StringVar(value='cash')
    payment_cb = ttk.Combobox(left, textvariable=payment_var, values=['cash', 'online', 'card', 'other'], state='readonly')
    payment_cb.grid(row=4, column=1, sticky='we')

    # calculator on the right
    calc = ttk.Frame(frm)
    calc.grid(row=0, column=1, padx=12, sticky='n')
    calc_display = tk.StringVar()

    def calc_btn_press(v):
        if v == 'C':
            calc_display.set('')
            return
        if v == '=':
            try:
                res = str(eval(calc_display.get()))
            except Exception:
                res = 'ERR'
            calc_display.set(res)
            amount_var.set(res if res != 'ERR' else '')
            return
        calc_display.set(calc_display.get() + v)

    ttk.Entry(calc, textvariable=calc_display, width=20, justify='right').grid(row=0, column=0, columnspan=4)
    buttons = [
        ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
        ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
        ('0', 4, 0), ('.', 4, 1), ('C', 4, 2), ('+', 4, 3),
        ('=', 5, 0)
    ]
    for (t, r, c) in buttons:
        ttk.Button(calc, text=t, width=5, command=lambda v=t: calc_btn_press(v)).grid(row=r, column=c, padx=2, pady=2)

    # tree
    tree = ttk.Treeview(root, columns=('amount', 'date', 'category', 'notes', 'payment', 'type'), show='headings')
    tree.heading('amount', text='Amount')
    tree.heading('date', text='Date')
    tree.heading('category', text='Category')
    tree.heading('notes', text='Notes')
    tree.heading('payment', text='Payment')
    tree.heading('type', text='Type')
    tree.grid(row=2, column=0, sticky='nsew', padx=10)

    # bottom quick buttons
    bottom = ttk.Frame(root, padding=8)
    bottom.grid(row=3, column=0, sticky='we')
    ttk.Button(bottom, text='In', command=lambda: open_confirm_dialog('in')).pack(side='left', expand=True, fill='x', padx=8)
    ttk.Button(bottom, text='Out', command=lambda: open_confirm_dialog('out')).pack(side='left', expand=True, fill='x', padx=8)

    # layout expansion
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)
    frm.columnconfigure(1, weight=1)

    # make label vars available to functions
    # (these were referenced earlier in refresh_tree)
    globals()['cash_label_var'] = cash_label_var
    globals()['online_label_var'] = online_label_var

    refresh_tree()
    root.mainloop()
