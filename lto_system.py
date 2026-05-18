#!/usr/bin/env python3
"""
LTO Information Management System
CMSC 127 – File Processing and Database Systems
2nd Semester AY 2025-2026
"""

import mysql.connector
from mysql.connector import Error
from datetime import date


# ─────────────────────────────────────────────
#  DATABASE CONNECTION
# ─────────────────────────────────────────────

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="lto",
        password="lto",
        database="trafficdb"
    )


# ─────────────────────────────────────────────
#  DISPLAY HELPERS
# ─────────────────────────────────────────────

def print_header(title):
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)

def print_table(headers, rows):
    if not rows:
        print("  (No records found.)")
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val) if val is not None else "NULL"))
    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in col_widths)
    print()
    print(fmt.format(*headers))
    print("  " + "  ".join("─" * w for w in col_widths))
    for row in rows:
        print(fmt.format(*[str(v) if v is not None else "NULL" for v in row]))
    print(f"\n  {len(rows)} record(s) found.")

def prompt(label, required=True, default=None):
    while True:
        hint = f" [{default}]" if default is not None else ""
        val = input(f"  {label}{hint}: ").strip()
        if not val and default is not None:
            return default
        if val or not required:
            return val if val else None
        print("  ✗ This field is required.")

def confirm(msg="Confirm? (y/n): "):
    return input(f"\n  {msg}").strip().lower() == 'y'

def pause():
    input("\n  Press Enter to continue...")


# ─────────────────────────────────────────────
#  DRIVER MANAGEMENT
# ─────────────────────────────────────────────

def driver_menu():
    while True:
        print_header("DRIVER MANAGEMENT")
        print("  [1] Add Driver")
        print("  [2] Update Driver")
        print("  [3] Delete Driver")
        print("  [4] Search Driver")
        print("  [5] View All Drivers")
        print("  [0] Back")
        choice = input("\n  Select option: ").strip()
        if   choice == '1': add_driver()
        elif choice == '2': update_driver()
        elif choice == '3': delete_driver()
        elif choice == '4': search_driver()
        elif choice == '5': view_all_drivers()
        elif choice == '0': break
        else: print("  ✗ Invalid option.")

def add_driver():
    print_header("ADD DRIVER")
    license_number   = prompt("License Number (e.g. N01-22-123456)")
    full_name        = prompt("Full Name")
    birthdate        = prompt("Birthdate (YYYY-MM-DD)")
    sex              = prompt("Sex (Male/Female)")
    address          = prompt("Address")
    license_type     = prompt("License Type (Student Permit / Non-Professional / Professional)")
    license_status   = prompt("License Status (Valid / Expired / Suspended / Revoked)")
    license_issuance = prompt("License Issuance Date (YYYY-MM-DD)")
    license_expiry   = prompt("License Expiry Date (YYYY-MM-DD)")

    print(f"\n  Adding driver: {full_name} ({license_number})")
    if not confirm(): return

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO driver
              (license_number, full_name, birthdate, sex, address,
               license_type, license_expiry, license_issuance, license_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (license_number, full_name, birthdate, sex, address,
              license_type, license_expiry, license_issuance, license_status))
        conn.commit()
        print("  ✓ Driver added successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def update_driver():
    print_header("UPDATE DRIVER")
    license_number = prompt("Enter License Number to update")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM driver WHERE license_number = %s", (license_number,))
        row = cur.fetchone()
        if not row:
            print("  ✗ Driver not found.")
            pause(); return

        cols    = [d[0] for d in cur.description]
        current = dict(zip(cols, row))
        print(f"\n  Current record for: {current['full_name']}")
        print("  (Press Enter to keep current value)")

        full_name        = prompt("Full Name",                  required=False, default=current['full_name'])
        birthdate        = prompt("Birthdate (YYYY-MM-DD)",     required=False, default=str(current['birthdate']))
        sex              = prompt("Sex",                        required=False, default=current['sex'])
        address          = prompt("Address",                    required=False, default=current['address'])
        license_type     = prompt("License Type",               required=False, default=current['license_type'])
        license_status   = prompt("License Status",             required=False, default=current['license_status'])
        license_issuance = prompt("Issuance Date (YYYY-MM-DD)", required=False, default=str(current['license_issuance']))
        license_expiry   = prompt("Expiry Date (YYYY-MM-DD)",   required=False, default=str(current['license_expiry']))

        if not confirm("Save changes? (y/n): "): return

        cur.execute("""
            UPDATE driver SET
              full_name=%s, birthdate=%s, sex=%s, address=%s,
              license_type=%s, license_status=%s,
              license_issuance=%s, license_expiry=%s
            WHERE license_number=%s
        """, (full_name, birthdate, sex, address, license_type,
              license_status, license_issuance, license_expiry, license_number))
        conn.commit()
        print("  ✓ Driver updated successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def delete_driver():
    print_header("DELETE DRIVER")
    license_number = prompt("Enter License Number to delete")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT full_name FROM driver WHERE license_number = %s", (license_number,))
        row = cur.fetchone()
        if not row:
            print("  ✗ Driver not found.")
            pause(); return

        print(f"\n  ⚠  This will delete driver: {row[0]} ({license_number})")
        print("     All associated vehicles and violations will also be affected.")
        if not confirm("Proceed with deletion? (y/n): "): return

        cur.execute("DELETE FROM driver WHERE license_number = %s", (license_number,))
        conn.commit()
        print("  ✓ Driver deleted successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def search_driver():
    print_header("SEARCH DRIVER")
    keyword = prompt("Enter name or license number")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT license_number, full_name, sex, address,
                   license_type, license_status, license_expiry
            FROM driver
            WHERE full_name LIKE %s OR license_number LIKE %s
        """, (f"%{keyword}%", f"%{keyword}%"))
        rows = cur.fetchall()
        headers = ["License No.", "Full Name", "Sex", "Address", "Type", "Status", "Expiry"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def view_all_drivers():
    print_header("ALL DRIVERS")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT license_number, full_name, sex,
                   license_type, license_status, license_expiry
            FROM driver ORDER BY full_name
        """)
        rows = cur.fetchall()
        headers = ["License No.", "Full Name", "Sex", "Type", "Status", "Expiry"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()


# ─────────────────────────────────────────────
#  VEHICLE MANAGEMENT
# ─────────────────────────────────────────────

def vehicle_menu():
    while True:
        print_header("VEHICLE MANAGEMENT")
        print("  [1] Add Vehicle")
        print("  [2] Update Vehicle")
        print("  [3] Delete Vehicle")
        print("  [4] Search Vehicle")
        print("  [5] View All Vehicles")
        print("  [0] Back")
        choice = input("\n  Select option: ").strip()
        if   choice == '1': add_vehicle()
        elif choice == '2': update_vehicle()
        elif choice == '3': delete_vehicle()
        elif choice == '4': search_vehicle()
        elif choice == '5': view_all_vehicles()
        elif choice == '0': break
        else: print("  ✗ Invalid option.")

def add_vehicle():
    print_header("ADD VEHICLE")
    plate_number   = prompt("Plate Number")
    engine_number  = prompt("Engine Number")
    chassis_number = prompt("Chassis Number")
    vehicle_type   = prompt("Vehicle Type (Car / SUV / Motorcycle / Truck / Van / Jeepney / Tricycle)")
    make           = prompt("Make (e.g., Toyota)")
    model          = prompt("Model (e.g., Vios)")
    year           = prompt("Year")
    color          = prompt("Color")
    license_number = prompt("Owner's License Number")

    print(f"\n  Adding vehicle: {year} {make} {model} ({plate_number})")
    if not confirm(): return

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO vehicle
              (plate_number, engine_number, chassis_number, vehicle_type,
               make, model, year, color, license_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (plate_number, engine_number, chassis_number, vehicle_type,
              make, model, int(year), color, license_number))
        conn.commit()
        print("  ✓ Vehicle added successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def update_vehicle():
    print_header("UPDATE VEHICLE")
    plate_number = prompt("Enter Plate Number to update")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM vehicle WHERE plate_number = %s", (plate_number,))
        row = cur.fetchone()
        if not row:
            print("  ✗ Vehicle not found.")
            pause(); return

        cols    = [d[0] for d in cur.description]
        current = dict(zip(cols, row))
        print(f"\n  Current: {current['year']} {current['make']} {current['model']}")
        print("  (Press Enter to keep current value)")

        engine_number  = prompt("Engine Number",  required=False, default=current['engine_number'])
        chassis_number = prompt("Chassis Number", required=False, default=current['chassis_number'])
        vehicle_type   = prompt("Vehicle Type",   required=False, default=current['vehicle_type'])
        make           = prompt("Make",           required=False, default=current['make'])
        model          = prompt("Model",          required=False, default=current['model'])
        year           = prompt("Year",           required=False, default=str(current['year']))
        color          = prompt("Color",          required=False, default=current['color'])
        license_number = prompt("Owner License",  required=False, default=current['license_number'])

        if not confirm("Save changes? (y/n): "): return

        cur.execute("""
            UPDATE vehicle SET
              engine_number=%s, chassis_number=%s, vehicle_type=%s,
              make=%s, model=%s, year=%s, color=%s, license_number=%s
            WHERE plate_number=%s
        """, (engine_number, chassis_number, vehicle_type, make, model,
              int(year), color, license_number, plate_number))
        conn.commit()
        print("  ✓ Vehicle updated successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def delete_vehicle():
    print_header("DELETE VEHICLE")
    plate_number = prompt("Enter Plate Number to delete")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT make, model, year FROM vehicle WHERE plate_number = %s", (plate_number,))
        row = cur.fetchone()
        if not row:
            print("  ✗ Vehicle not found.")
            pause(); return

        print(f"\n  ⚠  Delete vehicle: {row[2]} {row[0]} {row[1]} ({plate_number})?")
        if not confirm("Proceed? (y/n): "): return

        cur.execute("DELETE FROM vehicle WHERE plate_number = %s", (plate_number,))
        conn.commit()
        print("  ✓ Vehicle deleted successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def search_vehicle():
    print_header("SEARCH VEHICLE")
    keyword = prompt("Enter plate number, make, or model")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT v.plate_number, v.vehicle_type, v.make, v.model, v.year,
                   v.color, d.full_name
            FROM vehicle v
            LEFT JOIN driver d ON v.license_number = d.license_number
            WHERE v.plate_number LIKE %s
               OR v.make LIKE %s
               OR v.model LIKE %s
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        rows = cur.fetchall()
        headers = ["Plate No.", "Type", "Make", "Model", "Year", "Color", "Owner"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def view_all_vehicles():
    print_header("ALL VEHICLES")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT v.plate_number, v.vehicle_type, v.make, v.model,
                   v.year, v.color, d.full_name
            FROM vehicle v
            LEFT JOIN driver d ON v.license_number = d.license_number
            ORDER BY v.plate_number
        """)
        rows = cur.fetchall()
        headers = ["Plate No.", "Type", "Make", "Model", "Year", "Color", "Owner"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()


# ─────────────────────────────────────────────
#  VEHICLE REGISTRATION MANAGEMENT
# ─────────────────────────────────────────────

def registration_menu():
    while True:
        print_header("VEHICLE REGISTRATION MANAGEMENT")
        print("  [1] Add Registration")
        print("  [2] Update Registration")
        print("  [3] Delete Registration")
        print("  [4] Search Registration")
        print("  [5] View All Registrations")
        print("  [0] Back")
        choice = input("\n  Select option: ").strip()
        if   choice == '1': add_registration()
        elif choice == '2': update_registration()
        elif choice == '3': delete_registration()
        elif choice == '4': search_registration()
        elif choice == '5': view_all_registrations()
        elif choice == '0': break
        else: print("  ✗ Invalid option.")

def add_registration():
    print_header("ADD REGISTRATION")
    reg_number   = prompt("Registration Number")
    plate_number = prompt("Plate Number")
    reg_date     = prompt("Registration Date (YYYY-MM-DD)")
    exp_date     = prompt("Expiration Date (YYYY-MM-DD)")
    status       = prompt("Status (Active / Expired / Suspended)")

    print(f"\n  Adding registration {reg_number} for plate {plate_number}")
    if not confirm(): return

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO vehicle_registration
              (registration_number, registration_status,
               registration_date, expiration_date, plate_number)
            VALUES (%s, %s, %s, %s, %s)
        """, (reg_number, status, reg_date, exp_date, plate_number))
        conn.commit()
        print("  ✓ Registration added successfully.")
        if exp_date < str(date.today()):
            print("  ⚠  Note: Expiry date is in the past — trigger auto-set status to Expired.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def update_registration():
    print_header("UPDATE REGISTRATION")
    reg_number = prompt("Enter Registration Number to update")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM vehicle_registration WHERE registration_number = %s", (reg_number,))
        row = cur.fetchone()
        if not row:
            print("  ✗ Registration not found.")
            pause(); return

        cols    = [d[0] for d in cur.description]
        current = dict(zip(cols, row))
        print(f"\n  Current: Plate {current['plate_number']} | Status: {current['registration_status']}")
        print("  (Press Enter to keep current value)")

        status   = prompt("Status",                          required=False, default=current['registration_status'])
        reg_date = prompt("Registration Date (YYYY-MM-DD)",  required=False, default=str(current['registration_date']))
        exp_date = prompt("Expiration Date (YYYY-MM-DD)",    required=False, default=str(current['expiration_date']))

        if not confirm("Save changes? (y/n): "): return

        cur.execute("""
            UPDATE vehicle_registration
            SET registration_status=%s, registration_date=%s, expiration_date=%s
            WHERE registration_number=%s
        """, (status, reg_date, exp_date, reg_number))
        conn.commit()
        print("  ✓ Registration updated successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def delete_registration():
    print_header("DELETE REGISTRATION")
    reg_number = prompt("Enter Registration Number to delete")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT plate_number FROM vehicle_registration WHERE registration_number = %s", (reg_number,))
        row = cur.fetchone()
        if not row:
            print("  ✗ Registration not found.")
            pause(); return

        print(f"\n  ⚠  Delete registration {reg_number} (Plate: {row[0]})?")
        if not confirm("Proceed? (y/n): "): return

        cur.execute("DELETE FROM vehicle_registration WHERE registration_number = %s", (reg_number,))
        conn.commit()
        print("  ✓ Registration deleted successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def search_registration():
    print_header("SEARCH REGISTRATION")
    keyword = prompt("Enter registration number or plate number")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT vr.registration_number, vr.plate_number, v.make, v.model,
                   vr.registration_date, vr.expiration_date, vr.registration_status
            FROM vehicle_registration vr
            JOIN vehicle v ON vr.plate_number = v.plate_number
            WHERE vr.registration_number LIKE %s OR vr.plate_number LIKE %s
            ORDER BY vr.expiration_date DESC
        """, (f"%{keyword}%", f"%{keyword}%"))
        rows = cur.fetchall()
        headers = ["Reg. No.", "Plate", "Make", "Model", "Reg. Date", "Exp. Date", "Status"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def view_all_registrations():
    print_header("ALL REGISTRATIONS")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT vr.registration_number, vr.plate_number, v.make, v.model,
                   vr.registration_date, vr.expiration_date, vr.registration_status
            FROM vehicle_registration vr
            JOIN vehicle v ON vr.plate_number = v.plate_number
            ORDER BY vr.expiration_date DESC
        """)
        rows = cur.fetchall()
        headers = ["Reg. No.", "Plate", "Make", "Model", "Reg. Date", "Exp. Date", "Status"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()


# ─────────────────────────────────────────────
#  TRAFFIC VIOLATION MANAGEMENT
# ─────────────────────────────────────────────

def violation_menu():
    while True:
        print_header("TRAFFIC VIOLATION MANAGEMENT")
        print("  [1] Add Violation")
        print("  [2] Update Violation")
        print("  [3] Delete Violation")
        print("  [4] Search Violation")
        print("  [5] View All Violations")
        print("  [0] Back")
        choice = input("\n  Select option: ").strip()
        if   choice == '1': add_violation()
        elif choice == '2': update_violation()
        elif choice == '3': delete_violation()
        elif choice == '4': search_violation()
        elif choice == '5': view_all_violations()
        elif choice == '0': break
        else: print("  ✗ Invalid option.")

def add_violation():
    print_header("ADD VIOLATION")
    license_number = prompt("Driver License Number")
    plate_number   = prompt("Vehicle Plate Number")
    date_val       = prompt("Date (YYYY-MM-DD)")
    location       = prompt("Location")
    violation_type = prompt("Violation Type (e.g. Overspeeding, Reckless Driving)")
    fine_amount    = prompt("Fine Amount (PHP)")
    officer        = prompt("Apprehending Officer", required=False)
    status         = prompt("Status (Unpaid / Paid / Contested)")

    print(f"\n  Adding violation: {violation_type} on {date_val}")
    if not confirm(): return

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO traffic_violation
              (date, location, fine_amount, violation_type,
               apprehending_officer, violation_status,
               license_number, plate_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (date_val, location, float(fine_amount), violation_type,
              officer, status, license_number, plate_number))
        conn.commit()
        print(f"  ✓ Violation recorded (ID: {cur.lastrowid}).")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def update_violation():
    print_header("UPDATE VIOLATION")
    violation_id = prompt("Enter Violation ID to update")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT * FROM traffic_violation WHERE violation_id = %s", (violation_id,))
        row = cur.fetchone()
        if not row:
            print("  ✗ Violation not found.")
            pause(); return

        cols    = [d[0] for d in cur.description]
        current = dict(zip(cols, row))
        print(f"\n  Current: {current['violation_type']} | Fine: {current['fine_amount']} | Status: {current['violation_status']}")
        print("  (Press Enter to keep current value)")

        date_val       = prompt("Date (YYYY-MM-DD)",            required=False, default=str(current['date']))
        location       = prompt("Location",                     required=False, default=current['location'])
        violation_type = prompt("Violation Type",               required=False, default=current['violation_type'])
        fine_amount    = prompt("Fine Amount",                  required=False, default=str(current['fine_amount']))
        officer        = prompt("Apprehending Officer",         required=False, default=current['apprehending_officer'] or "")
        status         = prompt("Status (Unpaid/Paid/Contested)", required=False, default=current['violation_status'])

        if not confirm("Save changes? (y/n): "): return

        cur.execute("""
            UPDATE traffic_violation SET
              date=%s, location=%s, violation_type=%s,
              fine_amount=%s, apprehending_officer=%s, violation_status=%s
            WHERE violation_id=%s
        """, (date_val, location, violation_type, float(fine_amount),
              officer, status, int(violation_id)))
        conn.commit()
        print("  ✓ Violation updated successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def delete_violation():
    print_header("DELETE VIOLATION")
    violation_id = prompt("Enter Violation ID to delete")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("SELECT violation_type, date FROM traffic_violation WHERE violation_id = %s", (violation_id,))
        row = cur.fetchone()
        if not row:
            print("  ✗ Violation not found.")
            pause(); return

        print(f"\n  ⚠  Delete violation #{violation_id}: {row[0]} on {row[1]}?")
        if not confirm("Proceed? (y/n): "): return

        cur.execute("DELETE FROM traffic_violation WHERE violation_id = %s", (int(violation_id),))
        conn.commit()
        print("  ✓ Violation deleted successfully.")
    except Error as e:
        conn.rollback()
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def search_violation():
    print_header("SEARCH VIOLATION")
    keyword = prompt("Enter violation ID, driver name, or plate number")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT tv.violation_id, d.full_name, tv.plate_number,
                   tv.violation_type, tv.date, tv.location,
                   tv.fine_amount, tv.violation_status
            FROM traffic_violation tv
            JOIN driver d ON tv.license_number = d.license_number
            WHERE CAST(tv.violation_id AS CHAR) LIKE %s
               OR d.full_name LIKE %s
               OR tv.plate_number LIKE %s
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        rows = cur.fetchall()
        headers = ["ID", "Driver", "Plate", "Violation", "Date", "Location", "Fine", "Status"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def view_all_violations():
    print_header("ALL VIOLATIONS")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT tv.violation_id, d.full_name, tv.plate_number,
                   tv.violation_type, tv.date, tv.fine_amount, tv.violation_status
            FROM traffic_violation tv
            JOIN driver d ON tv.license_number = d.license_number
            ORDER BY tv.date DESC
        """)
        rows = cur.fetchall()
        headers = ["ID", "Driver", "Plate", "Violation", "Date", "Fine (PHP)", "Status"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()


# ─────────────────────────────────────────────
#  REPORTS
# ─────────────────────────────────────────────

def reports_menu():
    while True:
        print_header("REPORTS")
        print("  [1] Drivers filtered by license type, status, age range, sex")
        print("  [2] Vehicles owned by a given driver")
        print("  [3] Vehicles with expired registrations as of a date")
        print("  [4] Drivers with expired or suspended licenses")
        print("  [5] Violations by a driver within a date range")
        print("  [6] Total violations per type for a given year")
        print("  [7] Vehicles involved in violations within a city/region")
        print("  [0] Back")
        choice = input("\n  Select report: ").strip()
        if   choice == '1': report_drivers_filtered()
        elif choice == '2': report_vehicles_by_driver()
        elif choice == '3': report_expired_registrations()
        elif choice == '4': report_expired_suspended_licenses()
        elif choice == '5': report_violations_by_driver()
        elif choice == '6': report_violations_by_type_year()
        elif choice == '7': report_vehicles_by_city()
        elif choice == '0': break
        else: print("  ✗ Invalid option.")

def report_drivers_filtered():
    print_header("REPORT: DRIVERS BY FILTER")
    print("  Leave blank to skip a filter.\n")
    license_type   = prompt("License Type (Student Permit / Non-Professional / Professional)", required=False)
    license_status = prompt("License Status (Valid / Expired / Suspended / Revoked)",         required=False)
    sex            = prompt("Sex (Male / Female)",                                             required=False)
    age_min        = prompt("Minimum Age",                                                     required=False)
    age_max        = prompt("Maximum Age",                                                     required=False)

    query = """
        SELECT license_number, full_name,
               TIMESTAMPDIFF(YEAR, birthdate, CURDATE()) AS age,
               sex, address, license_type, license_status, license_expiry
        FROM driver
        WHERE 1=1
    """
    params = []
    if license_type:
        query += " AND license_type = %s";   params.append(license_type)
    if license_status:
        query += " AND license_status = %s"; params.append(license_status)
    if sex:
        query += " AND sex = %s";            params.append(sex)
    if age_min:
        query += " AND TIMESTAMPDIFF(YEAR, birthdate, CURDATE()) >= %s"; params.append(int(age_min))
    if age_max:
        query += " AND TIMESTAMPDIFF(YEAR, birthdate, CURDATE()) <= %s"; params.append(int(age_max))
    query += " ORDER BY full_name"

    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        headers = ["License No.", "Full Name", "Age", "Sex", "Address", "Type", "Status", "Expiry"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def report_vehicles_by_driver():
    print_header("REPORT: VEHICLES BY DRIVER")
    license_number = prompt("Enter Driver's License Number")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT d.license_number, d.full_name,
                   v.plate_number, v.vehicle_type, v.make, v.model, v.year, v.color
            FROM driver d
            LEFT JOIN vehicle v ON d.license_number = v.license_number
            WHERE d.license_number = %s
        """, (license_number,))
        rows = cur.fetchall()
        headers = ["License No.", "Driver", "Plate", "Type", "Make", "Model", "Year", "Color"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def report_expired_registrations():
    print_header("REPORT: VEHICLES WITH EXPIRED REGISTRATIONS")
    as_of_date = prompt("As of date (YYYY-MM-DD)", default=str(date.today()))
    try:
        conn = get_connection()
        cur  = conn.cursor()
        # Filter by expiration date only — avoids missing rows where the
        # status column is stale/inconsistent with the actual expiry date.
        cur.execute("""
            SELECT vr.plate_number, v.make, v.model, v.year,
                   d.full_name, vr.registration_number,
                   vr.expiration_date, vr.registration_status
            FROM vehicle_registration vr
            JOIN vehicle v ON vr.plate_number = v.plate_number
            JOIN driver  d ON v.license_number = d.license_number
            WHERE vr.expiration_date < %s
            ORDER BY vr.expiration_date
        """, (as_of_date,))
        rows = cur.fetchall()
        headers = ["Plate", "Make", "Model", "Year", "Owner", "Reg. No.", "Expiry", "Status"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def report_expired_suspended_licenses():
    print_header("REPORT: DRIVERS WITH EXPIRED OR SUSPENDED LICENSES")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT license_number, full_name, sex, address,
                   license_type, license_status, license_expiry
            FROM driver
            WHERE license_status IN ('Expired', 'Suspended', 'Revoked')
            ORDER BY license_status, full_name
        """)
        rows = cur.fetchall()
        headers = ["License No.", "Full Name", "Sex", "Address", "Type", "Status", "Expiry"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def report_violations_by_driver():
    print_header("REPORT: VIOLATIONS BY DRIVER IN DATE RANGE")
    license_number = prompt("Driver's License Number")
    date_from      = prompt("From date (YYYY-MM-DD)")
    date_to        = prompt("To date   (YYYY-MM-DD)")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT tv.violation_id, tv.date, tv.location,
                   tv.violation_type, tv.fine_amount,
                   tv.apprehending_officer, tv.violation_status,
                   tv.plate_number
            FROM traffic_violation tv
            WHERE tv.license_number = %s
              AND tv.date BETWEEN %s AND %s
            ORDER BY tv.date
        """, (license_number, date_from, date_to))
        rows = cur.fetchall()
        headers = ["ID", "Date", "Location", "Violation", "Fine", "Officer", "Status", "Plate"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def report_violations_by_type_year():
    print_header("REPORT: TOTAL VIOLATIONS PER TYPE FOR A GIVEN YEAR")
    year = prompt("Enter Year (e.g., 2025)")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT violation_type,
                   COUNT(*) AS total_violations,
                   SUM(fine_amount) AS total_fines,
                   SUM(CASE WHEN violation_status = 'Paid'   THEN 1 ELSE 0 END) AS paid,
                   SUM(CASE WHEN violation_status = 'Unpaid' THEN 1 ELSE 0 END) AS unpaid
            FROM traffic_violation
            WHERE YEAR(date) = %s
            GROUP BY violation_type
            ORDER BY total_violations DESC
        """, (int(year),))
        rows = cur.fetchall()
        headers = ["Violation Type", "Total", "Total Fines (PHP)", "Paid", "Unpaid"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()

def report_vehicles_by_city():
    print_header("REPORT: VEHICLES IN VIOLATIONS BY CITY/REGION")
    city = prompt("Enter city or region keyword (e.g., Pasig, Laguna, Metro Manila)")
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            SELECT DISTINCT tv.plate_number, v.make, v.model, v.year,
                            d.full_name, tv.location, tv.violation_type, tv.date
            FROM traffic_violation tv
            JOIN vehicle v ON tv.plate_number = v.plate_number
            JOIN driver  d ON tv.license_number = d.license_number
            WHERE tv.location LIKE %s
            ORDER BY tv.date DESC
        """, (f"%{city}%",))
        rows = cur.fetchall()
        headers = ["Plate", "Make", "Model", "Year", "Driver", "Location", "Violation", "Date"]
        print_table(headers, rows)
    except Error as e:
        print(f"  ✗ Error: {e}")
    finally:
        cur.close(); conn.close()
    pause()


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

def main():
    while True:
        print_header("LTO INFORMATION MANAGEMENT SYSTEM")
        print("  Land Transportation Office — Database Management\n")
        print("  [1] Driver Management")
        print("  [2] Vehicle Management")
        print("  [3] Vehicle Registration Management")
        print("  [4] Traffic Violation Management")
        print("  [5] Reports")
        print("  [0] Exit")
        choice = input("\n  Select option: ").strip()

        if   choice == '1': driver_menu()
        elif choice == '2': vehicle_menu()
        elif choice == '3': registration_menu()
        elif choice == '4': violation_menu()
        elif choice == '5': reports_menu()
        elif choice == '0':
            print("\n  Goodbye!\n")
            break
        else:
            print("  ✗ Invalid option.")


if __name__ == "__main__":
    main()