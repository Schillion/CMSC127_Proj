import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from mysql.connector import Error
from datetime import date
import re
import sys

_FONT = "Helvetica Neue" if sys.platform == "darwin" else ("Segoe UI" if sys.platform == "win32" else "DejaVu Sans")

_LIC_RE   = re.compile(r'^[A-Z]\d{2}-\d{2}-\d{6}$')
_PLATE_RE = re.compile(r'^[A-Z]{2,3}\s?\d{3,4}$')

def _valid_license(val):
    return bool(_LIC_RE.match(val.upper()))

def _valid_plate(val):
    return bool(_PLATE_RE.match(val.upper()))

def _valid_date(val):
    try:
        parts = val.split('-')
        if len(parts) != 3 or len(parts[0]) != 4:
            return False
        date(int(parts[0]), int(parts[1]), int(parts[2]))
        return True
    except (ValueError, IndexError):
        return False

def _valid_year(val):
    return val.isdigit() and 1886 <= int(val) <= date.today().year + 10

def _valid_fine(val):
    try:
        return float(val) >= 0
    except ValueError:
        return False


def get_connection():
    return mysql.connector.connect(
        host="localhost", user="lto", password="lto", database="trafficdb"
    )


LICENSE_TYPES      = ["Student Permit", "Non-Professional", "Professional"]
LICENSE_STATUSES   = ["Valid", "Expired", "Suspended", "Revoked"]
SEX_OPTIONS        = ["Male", "Female"]
VEHICLE_TYPES      = ["Car", "SUV", "Motorcycle", "Truck", "Van", "Jeepney", "Tricycle"]
REG_STATUSES       = ["Active", "Expired", "Suspended"]
VIOLATION_STATUSES = ["Unpaid", "Paid"]
VIOLATION_TYPES    = [
    "Overspeeding", "Reckless Driving", "Beating Red Light", "Illegal Parking",
    "No Seatbelt", "No Helmet", "Driving Without Valid License",
    "Driving with Expired License", "Illegal Counterflow", "Unregistered Vehicle",
    "Drunk Driving", "Overloading", "Swerving", "Disregarding Traffic Sign",
]

ROW_COLORS = {
    "Valid":     ("valid",     "#e8f5e9", "#1b5e20"),
    "Active":    ("active",    "#e8f5e9", "#1b5e20"),
    "Paid":      ("paid",      "#e8f5e9", "#1b5e20"),
    "Expired":   ("expired",   "#fff9c4", "#6d4c00"),
    "Suspended": ("suspended", "#ffe0b2", "#7c3900"),
    "Revoked":   ("revoked",   "#ffcdd2", "#7f0000"),
    "Unpaid":    ("unpaid",    "#ffcdd2", "#7f0000"),
}


class FormDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.result = None
        self._row = 0
        self._widgets = {}
        self._indicators = {}
        self._field_validators = {}

        self.frame = ttk.Frame(self, padding=16)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self._build_form()

        ttk.Separator(self.frame, orient=tk.HORIZONTAL).grid(
            row=self._row, column=0, columnspan=3, sticky=tk.EW, pady=(10, 6))
        self._row += 1

        bf = ttk.Frame(self.frame)
        bf.grid(row=self._row, column=0, columnspan=3, sticky=tk.E)
        ttk.Button(bf, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(bf, text="Save",   command=self._on_save).pack(side=tk.LEFT)

        self.bind("<Return>", lambda _: self._on_save())
        self.bind("<Escape>", lambda _: self.destroy())

        self.update_idletasks()
        for _, (_, w) in self._widgets.items():
            if isinstance(w, ttk.Entry) and str(w.cget("state")) not in ("disabled", "readonly"):
                w.focus_set()
                break

        self.update_idletasks()
        rx = parent.winfo_rootx() + parent.winfo_width()  // 2
        ry = parent.winfo_rooty() + parent.winfo_height() // 2
        self.geometry(f"+{rx - self.winfo_width()//2}+{ry - self.winfo_height()//2}")

        self.wait_window()

    def _add_field(self, label, widget_type="entry", options=None, default=""):
        r = self._row; self._row += 1
        ttk.Label(self.frame, text=label + ":").grid(
            row=r, column=0, sticky=tk.W, pady=3, padx=(0, 14))
        if widget_type == "combo":
            var = tk.StringVar(value=default if default else (options[0] if options else ""))
            w = ttk.Combobox(self.frame, textvariable=var, values=options,
                             state="readonly", width=29)
        else:
            var = tk.StringVar(value=str(default) if default is not None else "")
            w = ttk.Entry(self.frame, textvariable=var, width=31)
        w.grid(row=r, column=1, sticky=tk.W, pady=3)

        ind = ttk.Label(self.frame, text="", width=2, anchor=tk.W)
        ind.grid(row=r, column=2, sticky=tk.W, padx=(6, 0))
        self._indicators[label] = ind

        if widget_type == "entry":
            w.bind("<FocusOut>",   lambda _, l=label: self._check_field(l))
            w.bind("<KeyRelease>", lambda _, l=label: self._check_field(l))
            w.bind("<FocusIn>",    lambda e: e.widget.select_range(0, tk.END))

        self._widgets[label] = (var, w)
        return var

    def _set_validator(self, label, fn):
        self._field_validators[label] = fn

    def _check_field(self, label):
        if label not in self._field_validators:
            return
        val = self._get(label)
        ind = self._indicators[label]
        if not val:
            ind.config(text="")
            return
        ok = self._field_validators[label](val)
        ind.config(text="✓" if ok else "✗",
                   foreground="#2e7d32" if ok else "#c62828")

    def _get(self, label):
        return self._widgets[label][0].get().strip()

    def _disable(self, label):
        self._widgets[label][1].config(state="disabled")

    def _auto_upper(self, label):
        var, w = self._widgets[label]
        def _do(*_):
            v = var.get()
            u = v.upper()
            if v != u:
                pos = w.index(tk.INSERT) if isinstance(w, ttk.Entry) else 0
                var.set(u)
                if isinstance(w, ttk.Entry):
                    w.icursor(pos)
        var.trace_add("write", _do)

    def _build_form(self): raise NotImplementedError
    def _on_save(self):    raise NotImplementedError


class DriverForm(FormDialog):
    def __init__(self, parent, existing=None):
        self._ex = existing or {}
        super().__init__(parent, "Edit Driver" if existing else "Add Driver")

    def _build_form(self):
        ex = self._ex
        self._add_field("License Number",          default=ex.get("license_number", ""))
        self._add_field("Full Name",               default=ex.get("full_name", ""))
        self._add_field("Birthdate (YYYY-MM-DD)",  default=ex.get("birthdate", ""))
        self._add_field("Sex",          "combo",   options=SEX_OPTIONS,      default=ex.get("sex", "Male"))
        self._add_field("Address",                 default=ex.get("address", ""))
        self._add_field("License Type", "combo",   options=LICENSE_TYPES,    default=ex.get("license_type", "Non-Professional"))
        self._add_field("License Status", "combo", options=LICENSE_STATUSES, default=ex.get("license_status", "Valid"))
        self._add_field("Issuance Date (YYYY-MM-DD)", default=ex.get("license_issuance", ""))
        self._add_field("Expiry Date (YYYY-MM-DD)",   default=ex.get("license_expiry", ""))
        self._set_validator("License Number",           _valid_license)
        self._set_validator("Birthdate (YYYY-MM-DD)",   _valid_date)
        self._set_validator("Issuance Date (YYYY-MM-DD)", _valid_date)
        self._set_validator("Expiry Date (YYYY-MM-DD)",   _valid_date)
        if self._ex:
            self._disable("License Number")
        else:
            self._auto_upper("License Number")

    def _on_save(self):
        vals = {k: self._get(k) for k in [
            "License Number", "Full Name", "Birthdate (YYYY-MM-DD)", "Sex", "Address",
            "License Type", "License Status",
            "Issuance Date (YYYY-MM-DD)", "Expiry Date (YYYY-MM-DD)"]}
        if not all(vals.values()):
            messagebox.showerror("Validation", "All fields are required.", parent=self); return
        if not _valid_license(vals["License Number"]):
            messagebox.showerror("Validation", "License number must be in format X##-##-###### (e.g. N01-22-123456).", parent=self); return
        if not _valid_date(vals["Birthdate (YYYY-MM-DD)"]):
            messagebox.showerror("Validation", "Birthdate is not a valid date.", parent=self); return
        if not _valid_date(vals["Issuance Date (YYYY-MM-DD)"]):
            messagebox.showerror("Validation", "Issuance date is not a valid date.", parent=self); return
        if not _valid_date(vals["Expiry Date (YYYY-MM-DD)"]):
            messagebox.showerror("Validation", "Expiry date is not a valid date.", parent=self); return
        if vals["Birthdate (YYYY-MM-DD)"] >= str(date.today()):
            messagebox.showerror("Validation", "Birthdate must be in the past.", parent=self); return
        if vals["Issuance Date (YYYY-MM-DD)"] > vals["Expiry Date (YYYY-MM-DD)"]:
            messagebox.showerror("Validation", "Issuance date cannot be after expiry date.", parent=self); return
        self.result = {
            "license_number":   vals["License Number"].upper(),
            "full_name":        vals["Full Name"],
            "birthdate":        vals["Birthdate (YYYY-MM-DD)"],
            "sex":              vals["Sex"],
            "address":          vals["Address"],
            "license_type":     vals["License Type"],
            "license_status":   vals["License Status"],
            "license_issuance": vals["Issuance Date (YYYY-MM-DD)"],
            "license_expiry":   vals["Expiry Date (YYYY-MM-DD)"],
        }
        self.destroy()


class VehicleForm(FormDialog):
    def __init__(self, parent, existing=None):
        self._ex = existing or {}
        super().__init__(parent, "Edit Vehicle" if existing else "Add Vehicle")

    def _build_form(self):
        ex = self._ex
        self._add_field("Plate Number",      default=ex.get("plate_number", ""))
        self._add_field("Engine Number",     default=ex.get("engine_number", ""))
        self._add_field("Chassis Number",    default=ex.get("chassis_number", ""))
        self._add_field("Vehicle Type", "combo", options=VEHICLE_TYPES, default=ex.get("vehicle_type", "Car"))
        self._add_field("Make",              default=ex.get("make", ""))
        self._add_field("Model",             default=ex.get("model", ""))
        self._add_field("Year",              default=ex.get("year", ""))
        self._add_field("Color",             default=ex.get("color", ""))
        self._add_field("Owner License No.", default=ex.get("license_number", ""))
        self._set_validator("Plate Number",      _valid_plate)
        self._set_validator("Year",              _valid_year)
        self._set_validator("Owner License No.", lambda v: _valid_license(v) if v else True)
        self._auto_upper("Plate Number")
        self._auto_upper("Owner License No.")
        if self._ex:
            self._disable("Plate Number")
            self._disable("Chassis Number")

    def _on_save(self):
        year      = self._get("Year")
        owner_lic = self._get("Owner License No.")
        required  = ["Plate Number", "Engine Number", "Chassis Number", "Make", "Model", "Year", "Color"]
        if not all(self._get(f) for f in required):
            messagebox.showerror("Validation", "All fields except Owner License No. are required.", parent=self); return
        plate = self._get("Plate Number")
        if plate and not _valid_plate(plate):
            messagebox.showerror("Validation", "Plate number must be in format AAA 1234 or AA 123 (e.g. ABC 1234).", parent=self); return
        if not _valid_year(year):
            messagebox.showerror("Validation", f"Year must be a number between 1886 and {date.today().year + 10}.", parent=self); return
        if owner_lic and not _valid_license(owner_lic):
            messagebox.showerror("Validation", "Owner license number must be in format X##-##-###### (e.g. N01-22-123456).", parent=self); return
        self.result = {
            "plate_number":   " ".join(self._get("Plate Number").upper().split()),
            "engine_number":  " ".join(self._get("Engine Number").split()),
            "chassis_number": self._get("Chassis Number"),
            "vehicle_type":   self._get("Vehicle Type"),
            "make":           self._get("Make"),
            "model":          self._get("Model"),
            "year":           int(year),
            "color":          self._get("Color"),
            "license_number": owner_lic.upper() if owner_lic else None,
        }
        self.destroy()


class RegistrationForm(FormDialog):
    def __init__(self, parent, existing=None):
        self._ex = existing or {}
        super().__init__(parent, "Edit Registration" if existing else "Add Registration")

    def _build_form(self):
        ex = self._ex
        self._add_field("Registration Number",            default=ex.get("registration_number", ""))
        self._add_field("Plate Number",                   default=ex.get("plate_number", ""))
        self._add_field("Registration Date (YYYY-MM-DD)", default=ex.get("registration_date", ""))
        self._add_field("Expiration Date (YYYY-MM-DD)",   default=ex.get("expiration_date", ""))
        self._add_field("Status", "combo", options=REG_STATUSES, default=ex.get("registration_status", "Active"))
        self._set_validator("Plate Number",                    lambda v: _valid_plate(v) if v else True)
        self._set_validator("Registration Date (YYYY-MM-DD)", _valid_date)
        self._set_validator("Expiration Date (YYYY-MM-DD)",   _valid_date)
        self._auto_upper("Plate Number")
        if self._ex:
            self._disable("Registration Number")
            self._disable("Plate Number")

    def _on_save(self):
        self.result = {
            "registration_number": self._get("Registration Number"),
            "plate_number":        " ".join(self._get("Plate Number").upper().split()),
            "registration_date":   self._get("Registration Date (YYYY-MM-DD)"),
            "expiration_date":     self._get("Expiration Date (YYYY-MM-DD)"),
            "registration_status": self._get("Status"),
        }
        if not all(self.result.values()):
            messagebox.showerror("Validation", "All fields are required.", parent=self)
            self.result = None; return
        if not _valid_plate(self.result["plate_number"]):
            messagebox.showerror("Validation", "Plate number must be in format AAA 1234 or AA 123 (e.g. ABC 1234).", parent=self)
            self.result = None; return
        if not _valid_date(self.result["registration_date"]):
            messagebox.showerror("Validation", "Registration date is not a valid date.", parent=self)
            self.result = None; return
        if not _valid_date(self.result["expiration_date"]):
            messagebox.showerror("Validation", "Expiration date is not a valid date.", parent=self)
            self.result = None; return
        if self.result["registration_date"] > self.result["expiration_date"]:
            messagebox.showerror("Validation", "Registration date cannot be after expiration date.", parent=self)
            self.result = None; return
        self.destroy()


class ViolationForm(FormDialog):
    def __init__(self, parent, existing=None):
        self._ex = existing or {}
        super().__init__(parent, "Edit Violation" if existing else "Add Violation")

    def _build_form(self):
        ex = self._ex
        self._add_field("License Number",       default=ex.get("license_number", ""))
        self._add_field("Plate Number",         default=ex.get("plate_number", ""))
        self._add_field("Date (YYYY-MM-DD)",    default=ex.get("date", str(date.today())))
        self._add_field("Location",             default=ex.get("location", ""))
        self._add_field("Violation Type", "combo", options=VIOLATION_TYPES,
                        default=ex.get("violation_type", VIOLATION_TYPES[0]))
        self._add_field("Fine Amount (PHP)",    default=ex.get("fine_amount", ""))
        self._add_field("Apprehending Officer", default=ex.get("apprehending_officer", ""))
        self._add_field("Status", "combo", options=VIOLATION_STATUSES,
                        default=ex.get("violation_status", "Unpaid"))
        self._set_validator("License Number",    lambda v: _valid_license(v) if v else True)
        self._set_validator("Plate Number",      lambda v: _valid_plate(v)   if v else True)
        self._set_validator("Date (YYYY-MM-DD)", _valid_date)
        self._set_validator("Fine Amount (PHP)", _valid_fine)
        self._auto_upper("License Number")
        self._auto_upper("Plate Number")

    def _on_save(self):
        lic      = self._get("License Number")
        dt       = self._get("Date (YYYY-MM-DD)")
        location = self._get("Location")
        fine_str = self._get("Fine Amount (PHP)")
        if not dt or not location or not fine_str:
            messagebox.showerror("Validation", "Date, Location, and Fine Amount are required.", parent=self); return
        if lic and not _valid_license(lic):
            messagebox.showerror("Validation", "License number must be in format X##-##-###### (e.g. N01-22-123456).", parent=self); return
        plate_val = " ".join(self._get("Plate Number").upper().split())
        if plate_val and not _valid_plate(plate_val):
            messagebox.showerror("Validation", "Plate number must be in format AAA 1234 or AA 123 (e.g. ABC 1234).", parent=self); return
        if not _valid_date(dt):
            messagebox.showerror("Validation", "Violation date is not a valid date.", parent=self); return
        try:
            fine = float(fine_str)
        except ValueError:
            messagebox.showerror("Validation", "Fine amount must be a number.", parent=self); return
        if fine < 0:
            messagebox.showerror("Validation", "Fine amount cannot be negative.", parent=self); return
        plate = " ".join(self._get("Plate Number").upper().split())
        self.result = {
            "license_number":       lic.upper() if lic else None,
            "plate_number":         plate if plate else None,
            "date":                 dt,
            "location":             self._get("Location"),
            "violation_type":       self._get("Violation Type"),
            "fine_amount":          fine,
            "apprehending_officer": self._get("Apprehending Officer"),
            "violation_status":     self._get("Status"),
        }
        self.destroy()


class DriversFilterDialog(FormDialog):
    def __init__(self, parent):
        super().__init__(parent, "Filter Drivers")

    def _build_form(self):
        ttk.Label(self.frame, text="Leave blank to skip a filter.",
                  foreground="gray").grid(row=self._row, column=0, columnspan=3, pady=(0, 6))
        self._row += 1
        self._add_field("License Type",   "combo", options=[""] + LICENSE_TYPES)
        self._add_field("License Status", "combo", options=[""] + LICENSE_STATUSES)
        self._add_field("Sex",            "combo", options=[""] + SEX_OPTIONS)
        self._add_field("Min Age")
        self._add_field("Max Age")

    def _on_save(self):
        age_min = self._get("Min Age") or None
        age_max = self._get("Max Age") or None
        if age_min and (not age_min.isdigit() or int(age_min) < 0):
            messagebox.showerror("Validation", "Min Age must be a non-negative integer.", parent=self); return
        if age_max and (not age_max.isdigit() or int(age_max) < 0):
            messagebox.showerror("Validation", "Max Age must be a non-negative integer.", parent=self); return
        if age_min and age_max and int(age_min) > int(age_max):
            messagebox.showerror("Validation", "Min Age cannot be greater than Max Age.", parent=self); return
        self.result = {
            "license_type":   self._get("License Type")   or None,
            "license_status": self._get("License Status") or None,
            "sex":            self._get("Sex")            or None,
            "age_min":        age_min,
            "age_max":        age_max,
        }
        self.destroy()


class BaseTab(ttk.Frame):
    columns    = []
    headings   = []
    col_widths = {}
    status_col = None
    filters    = []  # list of (label, options) tuples

    def __init__(self, parent):
        super().__init__(parent)
        self._sort_asc   = {}
        self._filter_vars = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top = ttk.Frame(self, padding=(8, 8, 8, 2))
        top.pack(fill=tk.X)
        ttk.Label(top, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        self._search_entry = ttk.Entry(top, textvariable=self.search_var, width=32)
        self._search_entry.pack(side=tk.LEFT, padx=(5, 2))
        ttk.Button(top, text="×", width=2,
                   command=lambda: self.search_var.set("")).pack(side=tk.LEFT)

        if self.filters:
            ttk.Separator(top, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=(10, 8))
            for label, options in self.filters:
                ttk.Label(top, text=label + ":").pack(side=tk.LEFT, padx=(0, 3))
                var = tk.StringVar(value="All")
                var.trace_add("write", lambda *_: self.refresh())
                ttk.Combobox(top, textvariable=var, values=["All"] + list(options),
                             state="readonly", width=14).pack(side=tk.LEFT, padx=(0, 8))
                self._filter_vars[label] = var

        bf = ttk.Frame(self, padding=(8, 4, 8, 2))
        bf.pack(fill=tk.X)
        ttk.Button(bf, text="Add",     command=self.on_add).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(bf, text="Edit",    command=self.on_edit).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(bf, text="Delete",  command=self.on_delete).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(bf, text="Refresh", command=self.refresh).pack(side=tk.LEFT)

        tf = ttk.Frame(self, padding=(8, 2, 8, 4))
        tf.pack(fill=tk.BOTH, expand=True)
        sy = ttk.Scrollbar(tf, orient=tk.VERTICAL)
        sx = ttk.Scrollbar(tf, orient=tk.HORIZONTAL)
        self.tree = ttk.Treeview(tf, columns=self.columns, show="headings",
                                  yscrollcommand=sy.set, xscrollcommand=sx.set,
                                  selectmode="browse")
        sy.config(command=self.tree.yview)
        sx.config(command=self.tree.xview)

        for col, hdr in zip(self.columns, self.headings):
            self.tree.heading(col, text=hdr, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=self.col_widths.get(col, 120), minwidth=50)

        for tag, bg, fg in ROW_COLORS.values():
            self.tree.tag_configure(tag, background=bg, foreground=fg)

        sy.pack(side=tk.RIGHT,  fill=tk.Y)
        sx.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>",    lambda e: self.on_edit()   if self.tree.identify_row(e.y) else None)
        self.tree.bind("<Delete>",      lambda _: self.on_delete() if self.tree.selection()        else None)
        self.tree.bind("<Control-n>",   lambda _: self.on_add())
        self.tree.bind("<Control-e>",   lambda _: self.on_edit())
        self.tree.bind("<F5>",          lambda _: self.refresh())
        self.tree.bind("<Button-3>",    self._show_context_menu)

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, padding=(8, 2)).pack(anchor=tk.W)

    def _sort(self, col):
        asc = not self._sort_asc.get(col, False)
        self._sort_asc[col] = asc
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        def _sort_key(x):
            try:    return (0, float(x[0]))
            except (ValueError, TypeError): return (1, x[0].lower())
        data.sort(key=_sort_key, reverse=not asc)
        for i, (_, k) in enumerate(data):
            self.tree.move(k, "", i)
        arrow = " ▲" if asc else " ▼"
        for c, h in zip(self.columns, self.headings):
            self.tree.heading(c, text=h + (arrow if c == col else ""))

    def refresh(self):
        kw      = self.search_var.get() if hasattr(self, "search_var") else ""
        filters = {lbl: var.get() for lbl, var in self._filter_vars.items()
                   if var.get() != "All"}
        self.tree.delete(*self.tree.get_children())
        for c, h in zip(self.columns, self.headings):
            self.tree.heading(c, text=h)
        rows = []
        try:
            rows = self._load_rows(kw, filters)
            for row in rows:
                vals = [str(v) if v is not None else "" for v in row]
                tag  = ""
                if self.status_col is not None:
                    tag = ROW_COLORS.get(vals[self.status_col], ("",))[0]
                self.tree.insert("", tk.END, values=vals,
                                 tags=(tag,) if tag else ())
            self.status.set("No records found" if not rows else f"{len(rows)} record(s)")
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def selected_row(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a record first.")
            return None
        return self.tree.item(sel[0])["values"]

    def _db_exec(self, sql, params=()):
        conn = get_connection()
        cur  = None
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
        except Error:
            conn.rollback(); raise
        finally:
            if cur: cur.close()
            conn.close()

    def _db_fetch_one(self, sql, params=()):
        conn = get_connection()
        cur  = None
        try:
            cur  = conn.cursor()
            cur.execute(sql, params)
            row  = cur.fetchone()
            cols = [d[0] for d in cur.description] if cur.description else []
            return dict(zip(cols, row)) if row and cols else None
        finally:
            if cur: cur.close()
            conn.close()

    def _db_fetch(self, sql, params=()):
        conn = get_connection()
        cur  = None
        try:
            cur  = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            if cur: cur.close()
            conn.close()

    def _show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.tree.selection_set(item)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit",   command=self.on_edit)
        menu.add_command(label="Delete", command=self.on_delete)
        menu.tk_popup(event.x_root, event.y_root)

    def _load_rows(self, keyword, filters=None): raise NotImplementedError
    def on_add(self):    raise NotImplementedError
    def on_edit(self):   raise NotImplementedError
    def on_delete(self): raise NotImplementedError


class DriverTab(BaseTab):
    columns    = ("license_number","full_name","sex","license_type","license_status","license_expiry","address")
    headings   = ("License No.","Full Name","Sex","Type","Status","Expiry","Address")
    status_col = 4
    filters    = [("Status", LICENSE_STATUSES), ("Type", LICENSE_TYPES), ("Sex", SEX_OPTIONS)]
    col_widths = {
        "license_number": 130, "full_name": 200, "sex": 65,
        "license_type": 130, "license_status": 90,
        "license_expiry": 95, "address": 220,
    }

    def _load_rows(self, kw, filters=None):
        filters = filters or {}
        sql    = """
            SELECT license_number, full_name, sex, license_type,
                   license_status, license_expiry, address
            FROM driver
            WHERE (full_name LIKE %s OR license_number LIKE %s)
        """
        params = [f"%{kw}%", f"%{kw}%"]
        if filters.get("Status"): sql += " AND license_status=%s"; params.append(filters["Status"])
        if filters.get("Type"):   sql += " AND license_type=%s";   params.append(filters["Type"])
        if filters.get("Sex"):    sql += " AND sex=%s";            params.append(filters["Sex"])
        sql += " ORDER BY full_name"
        return self._db_fetch(sql, params)

    def on_add(self):
        dlg = DriverForm(self)
        if not dlg.result: return
        d = dlg.result
        try:
            self._db_exec("""
                INSERT INTO driver
                  (license_number, full_name, birthdate, sex, address,
                   license_type, license_expiry, license_issuance, license_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (d["license_number"], d["full_name"], d["birthdate"], d["sex"],
                  d["address"], d["license_type"], d["license_expiry"],
                  d["license_issuance"], d["license_status"]))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def on_edit(self):
        vals = self.selected_row()
        if not vals: return
        existing = self._db_fetch_one("SELECT * FROM driver WHERE license_number=%s", (vals[0],))
        if not existing: return
        dlg = DriverForm(self, existing=existing)
        if not dlg.result: return
        d = dlg.result
        try:
            self._db_exec("""
                UPDATE driver SET full_name=%s, birthdate=%s, sex=%s, address=%s,
                  license_type=%s, license_status=%s, license_issuance=%s, license_expiry=%s
                WHERE license_number=%s
            """, (d["full_name"], d["birthdate"], d["sex"], d["address"],
                  d["license_type"], d["license_status"],
                  d["license_issuance"], d["license_expiry"], d["license_number"]))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def on_delete(self):
        vals = self.selected_row()
        if not vals: return
        lic, name = vals[0], vals[1]
        if not messagebox.askyesno("Confirm Delete",
                f"Delete driver {name} ({lic})?\n\nOwned vehicles and violations will have their owner reference cleared."):
            return
        try:
            self._db_exec("DELETE FROM driver WHERE license_number=%s", (lic,))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))


class VehicleTab(BaseTab):
    columns    = ("plate_number","vehicle_type","make","model","year","color","owner")
    headings   = ("Plate No.","Type","Make","Model","Year","Color","Owner")
    status_col = None
    filters    = [("Type", VEHICLE_TYPES)]
    col_widths = {
        "plate_number": 95, "vehicle_type": 100, "make": 100,
        "model": 110, "year": 60, "color": 90, "owner": 200,
    }

    def _load_rows(self, kw, filters=None):
        filters = filters or {}
        sql    = """
            SELECT v.plate_number, v.vehicle_type, v.make, v.model,
                   v.year, v.color, d.full_name
            FROM vehicle v
            LEFT JOIN driver d ON v.license_number = d.license_number
            WHERE (v.plate_number LIKE %s OR v.make LIKE %s OR v.model LIKE %s)
        """
        params = [f"%{kw}%", f"%{kw}%", f"%{kw}%"]
        if filters.get("Type"): sql += " AND v.vehicle_type=%s"; params.append(filters["Type"])
        sql += " ORDER BY v.plate_number"
        return self._db_fetch(sql, params)

    def on_add(self):
        dlg = VehicleForm(self)
        if not dlg.result: return
        d = dlg.result
        try:
            self._db_exec("""
                INSERT INTO vehicle
                  (plate_number, engine_number, chassis_number, vehicle_type,
                   make, model, year, color, license_number)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (d["plate_number"], d["engine_number"], d["chassis_number"],
                  d["vehicle_type"], d["make"], d["model"], d["year"],
                  d["color"], d["license_number"]))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def on_edit(self):
        vals = self.selected_row()
        if not vals: return
        existing = self._db_fetch_one("SELECT * FROM vehicle WHERE plate_number=%s", (vals[0],))
        if not existing: return
        dlg = VehicleForm(self, existing=existing)
        if not dlg.result: return
        d = dlg.result
        try:
            self._db_exec("""
                UPDATE vehicle SET engine_number=%s, chassis_number=%s, vehicle_type=%s,
                  make=%s, model=%s, year=%s, color=%s, license_number=%s
                WHERE plate_number=%s
            """, (d["engine_number"], d["chassis_number"], d["vehicle_type"],
                  d["make"], d["model"], d["year"], d["color"],
                  d["license_number"], d["plate_number"]))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def on_delete(self):
        vals = self.selected_row()
        if not vals: return
        plate = vals[0]
        if not messagebox.askyesno("Confirm Delete",
                f"Delete vehicle {plate}?\n\nLinked violations and registrations will have their plate reference cleared."):
            return
        try:
            self._db_exec("DELETE FROM vehicle WHERE plate_number=%s", (plate,))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))


class RegistrationTab(BaseTab):
    columns    = ("registration_number","plate_number","make","model","registration_date","expiration_date","registration_status")
    headings   = ("Reg. No.","Plate","Make","Model","Reg. Date","Exp. Date","Status")
    status_col = 6
    filters    = [("Status", REG_STATUSES)]
    col_widths = {
        "registration_number": 170, "plate_number": 85,
        "make": 90, "model": 100,
        "registration_date": 100, "expiration_date": 100,
        "registration_status": 85,
    }

    def _load_rows(self, kw, filters=None):
        filters = filters or {}
        sql    = """
            SELECT vr.registration_number, vr.plate_number, v.make, v.model,
                   vr.registration_date, vr.expiration_date, vr.registration_status
            FROM vehicle_registration vr
            LEFT JOIN vehicle v ON vr.plate_number = v.plate_number
            WHERE (vr.registration_number LIKE %s OR vr.plate_number LIKE %s)
        """
        params = [f"%{kw}%", f"%{kw}%"]
        if filters.get("Status"): sql += " AND vr.registration_status=%s"; params.append(filters["Status"])
        sql += " ORDER BY vr.expiration_date DESC"
        return self._db_fetch(sql, params)

    def on_add(self):
        dlg = RegistrationForm(self)
        if not dlg.result: return
        d = dlg.result
        try:
            self._db_exec("""
                INSERT INTO vehicle_registration
                  (registration_number, registration_status,
                   registration_date, expiration_date, plate_number)
                VALUES (%s,%s,%s,%s,%s)
            """, (d["registration_number"], d["registration_status"],
                  d["registration_date"], d["expiration_date"], d["plate_number"]))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def on_edit(self):
        vals = self.selected_row()
        if not vals: return
        existing = self._db_fetch_one(
            "SELECT * FROM vehicle_registration WHERE registration_number=%s", (vals[0],))
        if not existing: return
        dlg = RegistrationForm(self, existing=existing)
        if not dlg.result: return
        d = dlg.result
        try:
            self._db_exec("""
                UPDATE vehicle_registration
                SET registration_status=%s, registration_date=%s, expiration_date=%s
                WHERE registration_number=%s
            """, (d["registration_status"], d["registration_date"],
                  d["expiration_date"], d["registration_number"]))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def on_delete(self):
        vals = self.selected_row()
        if not vals: return
        reg = vals[0]
        if not messagebox.askyesno("Confirm Delete", f"Delete registration {reg}?"):
            return
        try:
            self._db_exec("DELETE FROM vehicle_registration WHERE registration_number=%s", (reg,))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))


class ViolationTab(BaseTab):
    columns    = ("violation_id","full_name","plate_number","violation_type","date","fine_amount","violation_status")
    headings   = ("ID","Driver","Plate","Violation","Date","Fine (PHP)","Status")
    status_col = 6
    filters    = [("Status", VIOLATION_STATUSES)]
    col_widths = {
        "violation_id": 45, "full_name": 180, "plate_number": 85,
        "violation_type": 170, "date": 95,
        "fine_amount": 90, "violation_status": 80,
    }

    def _load_rows(self, kw, filters=None):
        filters = filters or {}
        sql    = """
            SELECT tv.violation_id, d.full_name, tv.plate_number,
                   tv.violation_type, tv.date, tv.fine_amount, tv.violation_status
            FROM traffic_violation tv
            LEFT JOIN driver d ON tv.license_number = d.license_number
            WHERE (CAST(tv.violation_id AS CHAR) LIKE %s
               OR d.full_name LIKE %s
               OR tv.plate_number LIKE %s
               OR tv.violation_type LIKE %s)
        """
        params = [f"%{kw}%"] * 4
        if filters.get("Status"): sql += " AND tv.violation_status=%s"; params.append(filters["Status"])
        sql += " ORDER BY tv.date DESC"
        return self._db_fetch(sql, params)

    def on_add(self):
        dlg = ViolationForm(self)
        if not dlg.result: return
        d = dlg.result
        try:
            self._db_exec("""
                INSERT INTO traffic_violation
                  (date, location, fine_amount, violation_type, apprehending_officer,
                   violation_status, license_number, plate_number)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (d["date"], d["location"], d["fine_amount"], d["violation_type"],
                  d["apprehending_officer"], d["violation_status"],
                  d["license_number"], d["plate_number"]))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def on_edit(self):
        vals = self.selected_row()
        if not vals: return
        existing = self._db_fetch_one(
            "SELECT * FROM traffic_violation WHERE violation_id=%s", (vals[0],))
        if not existing: return
        dlg = ViolationForm(self, existing=existing)
        if not dlg.result: return
        d = dlg.result
        try:
            self._db_exec("""
                UPDATE traffic_violation SET date=%s, location=%s, violation_type=%s,
                  fine_amount=%s, apprehending_officer=%s, violation_status=%s,
                  license_number=%s, plate_number=%s
                WHERE violation_id=%s
            """, (d["date"], d["location"], d["violation_type"], d["fine_amount"],
                  d["apprehending_officer"], d["violation_status"],
                  d["license_number"], d["plate_number"], int(vals[0])))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def on_delete(self):
        vals = self.selected_row()
        if not vals: return
        vid = vals[0]
        if not messagebox.askyesno("Confirm Delete", f"Delete violation #{vid}?"):
            return
        try:
            self._db_exec("DELETE FROM traffic_violation WHERE violation_id=%s", (int(vid),))
            self.refresh()
        except Error as e:
            messagebox.showerror("DB Error", str(e))


REPORTS = [
    ("Drivers by Filter",                            "drivers_filter"),
    ("Vehicles by Driver",                           "vehicles_by_driver"),
    ("Expired Registrations as of Date",             "expired_regs"),
    ("Inactive Drivers (Expired/Suspended/Revoked)", "inactive_drivers"),
    ("Driver Violations in Date Range",              "violations_range"),
    ("Violations per Type for Year",                 "violations_year"),
    ("Vehicles in Violations by City",               "violations_city"),
]

class ReportsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        left = ttk.LabelFrame(self, text="Select Report", padding=12)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self._key = tk.StringVar(value=REPORTS[0][1])
        self._key.trace_add("write", lambda *_: self._clear())
        for label, key in REPORTS:
            ttk.Radiobutton(left, text=label, variable=self._key, value=key).pack(
                anchor=tk.W, pady=3)
        ttk.Button(left, text="▶  Run Report", command=self._run).pack(
            fill=tk.X, pady=(16, 0))

        right = ttk.Frame(self)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        sy = ttk.Scrollbar(right, orient=tk.VERTICAL)
        sx = ttk.Scrollbar(right, orient=tk.HORIZONTAL)
        self.tree = ttk.Treeview(right, show="headings",
                                  yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.config(command=self.tree.yview)
        sx.config(command=self.tree.xview)
        sy.pack(side=tk.RIGHT,  fill=tk.Y)
        sx.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status, padding=(10, 2)).pack(anchor=tk.W)

    def _clear(self):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []
        self.status.set("")

    def _show(self, headers, rows):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = headers
        for h in headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=140, minwidth=60)
        for row in rows:
            self.tree.insert("", tk.END, values=[str(v) if v is not None else "" for v in row])
        self.status.set("No records found" if not rows else f"{len(rows)} record(s)")

    def _ask(self, prompt, default=""):
        return simpledialog.askstring("Input", prompt, initialvalue=default, parent=self) or ""

    def _query(self, sql, params=()):
        conn = get_connection()
        cur  = None
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()
        finally:
            if cur: cur.close()
            conn.close()

    def _run(self):
        try:
            getattr(self, f"_rpt_{self._key.get()}")()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _rpt_drivers_filter(self):
        dlg = DriversFilterDialog(self)
        if not dlg.result: return
        f   = dlg.result
        sql = """
            SELECT license_number, full_name,
                   TIMESTAMPDIFF(YEAR, birthdate, CURDATE()) AS age,
                   sex, license_type, license_status, license_expiry
            FROM driver WHERE 1=1
        """
        params = []
        if f["license_type"]:   sql += " AND license_type=%s";   params.append(f["license_type"])
        if f["license_status"]: sql += " AND license_status=%s"; params.append(f["license_status"])
        if f["sex"]:            sql += " AND sex=%s";            params.append(f["sex"])
        if f["age_min"]:
            sql += " AND TIMESTAMPDIFF(YEAR,birthdate,CURDATE())>=%s"
            params.append(int(f["age_min"]))
        if f["age_max"]:
            sql += " AND TIMESTAMPDIFF(YEAR,birthdate,CURDATE())<=%s"
            params.append(int(f["age_max"]))
        sql += " ORDER BY full_name"
        self._show(["License No.","Full Name","Age","Sex","Type","Status","Expiry"],
                   self._query(sql, params))

    def _rpt_vehicles_by_driver(self):
        lic = self._ask("Enter Driver License Number:")
        if not lic: return
        if not _valid_license(lic):
            messagebox.showerror("Validation", "License number must be in format X##-##-###### (e.g. N01-22-123456).", parent=self); return
        self._show(["License No.","Driver","Plate","Type","Make","Model","Year","Color"],
                   self._query("""
            SELECT d.license_number, d.full_name, v.plate_number, v.vehicle_type,
                   v.make, v.model, v.year, v.color
            FROM driver d
            LEFT JOIN vehicle v ON d.license_number = v.license_number
            WHERE d.license_number=%s
        """, (lic.upper(),)))

    def _rpt_expired_regs(self):
        as_of = self._ask("As of date (YYYY-MM-DD):", default=str(date.today()))
        if not as_of: return
        if not _valid_date(as_of):
            messagebox.showerror("Validation", "Date must be in YYYY-MM-DD format.", parent=self); return
        self._show(["Plate","Make","Model","Year","Owner","Reg. No.","Expiry","Status"],
                   self._query("""
            SELECT vr.plate_number, v.make, v.model, v.year,
                   d.full_name, vr.registration_number,
                   vr.expiration_date, vr.registration_status
            FROM vehicle_registration vr
            LEFT JOIN vehicle v ON vr.plate_number = v.plate_number
            LEFT JOIN driver d ON v.license_number = d.license_number
            WHERE vr.expiration_date < %s
            ORDER BY vr.expiration_date
        """, (as_of,)))

    def _rpt_inactive_drivers(self):
        self._show(["License No.","Full Name","Sex","Address","Type","Status","Expiry"],
                   self._query("""
            SELECT license_number, full_name, sex, address,
                   license_type, license_status, license_expiry
            FROM driver
            WHERE license_status IN ('Expired','Suspended','Revoked')
            ORDER BY license_status, full_name
        """))

    def _rpt_violations_range(self):
        lic    = self._ask("Driver License Number:")
        d_from = self._ask("From date (YYYY-MM-DD):")
        d_to   = self._ask("To date (YYYY-MM-DD):")
        if not (lic and d_from and d_to): return
        if not _valid_license(lic):
            messagebox.showerror("Validation", "License number must be in format X##-##-###### (e.g. N01-22-123456).", parent=self); return
        if not _valid_date(d_from):
            messagebox.showerror("Validation", "From date is not a valid date.", parent=self); return
        if not _valid_date(d_to):
            messagebox.showerror("Validation", "To date is not a valid date.", parent=self); return
        if d_from > d_to:
            messagebox.showerror("Validation", "From date cannot be after To date.", parent=self); return
        self._show(["ID","Date","Location","Violation","Fine","Officer","Status","Plate"],
                   self._query("""
            SELECT violation_id, date, location, violation_type, fine_amount,
                   apprehending_officer, violation_status, plate_number
            FROM traffic_violation
            WHERE license_number=%s AND date BETWEEN %s AND %s
            ORDER BY date
        """, (lic.upper(), d_from, d_to)))

    def _rpt_violations_year(self):
        year = self._ask("Enter year (e.g. 2025):")
        if not year: return
        if not _valid_year(year):
            messagebox.showerror("Validation", f"Year must be a number between 1886 and {date.today().year + 10}.", parent=self); return
        self._show(["Violation Type","Total","Total Fines (PHP)","Paid","Unpaid"],
                   self._query("""
            SELECT violation_type, COUNT(*) AS total, SUM(fine_amount),
                   SUM(CASE WHEN violation_status='Paid'   THEN 1 ELSE 0 END),
                   SUM(CASE WHEN violation_status='Unpaid' THEN 1 ELSE 0 END)
            FROM traffic_violation
            WHERE YEAR(date)=%s
            GROUP BY violation_type ORDER BY total DESC
        """, (int(year),)))

    def _rpt_violations_city(self):
        city = self._ask("City or region keyword:")
        if not city: return
        self._show(["Plate","Make","Model","Year","Driver","Location","Violation","Date"],
                   self._query("""
            SELECT DISTINCT tv.plate_number, v.make, v.model, v.year,
                   d.full_name, tv.location, tv.violation_type, tv.date
            FROM traffic_violation tv
            LEFT JOIN vehicle v ON tv.plate_number = v.plate_number
            LEFT JOIN driver d ON tv.license_number = d.license_number
            WHERE tv.location LIKE %s
            ORDER BY tv.date DESC
        """, (f"%{city}%",)))


class LTOApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LTO Information Management System")
        self.geometry("1200x680")
        self.minsize(960, 520)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=26)

        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h   = 1200, 680
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        header = tk.Frame(self, bg="#1565C0", height=52)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="LTO Information Management System",
                 font=(_FONT, 14, "bold"),
                 bg="#1565C0", fg="white").pack(side=tk.LEFT, padx=16, pady=8)
        tk.Label(header, text="Land Transportation Office  •  trafficdb",
                 font=(_FONT, 9),
                 bg="#1565C0", fg="#90CAF9").pack(side=tk.LEFT, pady=14)

        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True, padx=6, pady=(4, 4))
        nb.add(DriverTab(nb),       text="  Drivers  ")
        nb.add(VehicleTab(nb),      text="  Vehicles  ")
        nb.add(RegistrationTab(nb), text="  Registrations  ")
        nb.add(ViolationTab(nb),    text="  Violations  ")
        nb.add(ReportsTab(nb),      text="  Reports  ")

        def _on_tab_change(_):
            tab = nb.nametowidget(nb.select())
            if hasattr(tab, "_search_entry"):
                tab.after(50, tab._search_entry.focus_set)
        nb.bind("<<NotebookTabChanged>>", _on_tab_change)

        bar = tk.Frame(self, bg="#E3F2FD", height=22)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        tk.Label(bar, text="  Double-click a row to edit  •  Delete key to delete  •  Click column header to sort",
                 font=(_FONT, 8), bg="#E3F2FD", fg="#555").pack(side=tk.LEFT)


if __name__ == "__main__":
    app = LTOApp()
    app.mainloop()
