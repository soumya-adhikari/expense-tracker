"""
Minimal Kivy-based Android app for the Expense Tracker.

This is a simple port of the desktop app using Kivy so it can be packaged
for Android. It re-uses `db.py` (SQLite) and provides basic add/list/delete
and In/Out functionality. This file is a starting point and intentionally
keeps the UI minimal.

To build an APK you'll typically use Buildozer on Linux (WSL recommended
on Windows) — instructions are added to README.md.
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
import db
from datetime import datetime


class ExpensesView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh()

    def refresh(self):
        rows = db.list_expenses()
        data = []
        for r in rows:
            # r: (id, amount, date, category, notes, payment_method, type)
            data.append({'text': f"{r[1]:.2f} | {r[2]} | {r[3]} | {r[6]} | {r[0]}", 'id': r[0]})
        self.data = data


class ConfirmPopup(Popup):
    def __init__(self, amount, date_s, category, notes, payment, entry_type, on_confirm, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Confirm entry'
        self.size_hint = (0.9, 0.7)
        layout = GridLayout(cols=2, spacing=6, padding=6)
        self.amount_input = TextInput(text=str(amount), multiline=False)
        self.date_input = TextInput(text=date_s, multiline=False)
        self.cat_input = TextInput(text=category or '', multiline=False)
        self.notes_input = TextInput(text=notes or '', multiline=False)
        self.pay_spinner = Spinner(text=payment or 'cash', values=['cash', 'online', 'card', 'other'])

        layout.add_widget(Label(text='Amount'))
        layout.add_widget(self.amount_input)
        layout.add_widget(Label(text='Date (YYYY-MM-DD)'))
        layout.add_widget(self.date_input)
        layout.add_widget(Label(text='Category'))
        layout.add_widget(self.cat_input)
        layout.add_widget(Label(text='Notes'))
        layout.add_widget(self.notes_input)
        layout.add_widget(Label(text='Payment'))
        layout.add_widget(self.pay_spinner)

        btn_layout = BoxLayout(size_hint_y=None, height='48dp')
        confirm_btn = Button(text='Confirm')
        cancel_btn = Button(text='Cancel')
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)

        root = BoxLayout(orientation='vertical')
        root.add_widget(layout)
        root.add_widget(btn_layout)
        self.add_widget(root)

        def _on_confirm(instance):
            # validate
            try:
                amt = float(self.amount_input.text)
            except Exception:
                self._show_error('Invalid amount')
                return
            try:
                datetime.strptime(self.date_input.text, '%Y-%m-%d')
            except Exception:
                self._show_error('Invalid date format (YYYY-MM-DD)')
                return
            db.add_expense(amt, self.date_input.text, self.cat_input.text, self.notes_input.text, self.pay_spinner.text, entry_type)
            on_confirm()
            self.dismiss()

        def _on_cancel(instance):
            self.dismiss()

        confirm_btn.bind(on_release=_on_confirm)
        cancel_btn.bind(on_release=_on_cancel)

    def _show_error(self, txt):
        p = Popup(title='Error', content=Label(text=txt), size_hint=(0.8, 0.3))
        p.open()


class ExpenseAppRoot(BoxLayout):
    status = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=6, padding=6, **kwargs)
        db.init_db()

        # top inputs
        top = GridLayout(cols=2, size_hint_y=None, height='160dp')
        self.amount = TextInput(text='', multiline=False, input_filter='float')
        self.date = TextInput(text=datetime.today().strftime('%Y-%m-%d'), multiline=False)
        self.category = TextInput(text='', multiline=False)
        self.notes = TextInput(text='', multiline=False)
        self.payment = Spinner(text='cash', values=['cash', 'online', 'card', 'other'])

        top.add_widget(Label(text='Amount'))
        top.add_widget(self.amount)
        top.add_widget(Label(text='Date'))
        top.add_widget(self.date)
        top.add_widget(Label(text='Category'))
        top.add_widget(self.category)
        top.add_widget(Label(text='Notes'))
        top.add_widget(self.notes)
        top.add_widget(Label(text='Payment'))
        top.add_widget(self.payment)

        self.add_widget(top)

        # quick buttons
        btns = BoxLayout(size_hint_y=None, height='48dp')
        btn_in = Button(text='In')
        btn_out = Button(text='Out')
        btn_refresh = Button(text='Refresh')
        btns.add_widget(btn_in)
        btns.add_widget(btn_out)
        btns.add_widget(btn_refresh)
        self.add_widget(btns)

        # list area
        self.rv = ExpensesView(size_hint=(1, 1))
        self.add_widget(self.rv)

        # status
        self.status_label = Label(text='')
        self.add_widget(self.status_label)

        btn_in.bind(on_release=lambda x: self.open_confirm('in'))
        btn_out.bind(on_release=lambda x: self.open_confirm('out'))
        btn_refresh.bind(on_release=lambda x: self.rv.refresh())

    def open_confirm(self, entry_type):
        def on_confirmed():
            self.status_label.text = 'Saved.'
            self.rv.refresh()

        p = ConfirmPopup(self.amount.text, self.date.text, self.category.text, self.notes.text, self.payment.text, entry_type, on_confirmed)
        p.open()


class ExpenseApp(App):
    def build(self):
        return ExpenseAppRoot()


if __name__ == '__main__':
    ExpenseApp().run()
