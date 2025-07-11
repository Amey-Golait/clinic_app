import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta, time

class ClinicAppointment(Document):
    def validate(self):
        # --- Normalize date and time
        if isinstance(self.appointment_date, str):
            self.appointment_date = datetime.strptime(self.appointment_date, "%Y-%m-%d").date()

        if isinstance(self.appointment_time, str):
            self.appointment_time = datetime.strptime(self.appointment_time, "%H:%M:%S").time()
        elif isinstance(self.appointment_time, timedelta):
            self.appointment_time = (datetime.min + self.appointment_time).time()
        elif not isinstance(self.appointment_time, time):
            frappe.throw("Invalid type for appointment_time")

        # --- Compute end_time
        try:
            self.end_time = (
                datetime.combine(self.appointment_date, self.appointment_time)
                + timedelta(minutes=30)
            ).time()
        except Exception as e:
            frappe.throw(f"Failed to calculate end_time: {e}")

        # --- Set display title and custom_display
        doctor_name = frappe.db.get_value("Doctor", self.doctor, "doctor_name") or self.doctor
        patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient

        self.display_title = f"{doctor_name} - {patient_name} - {self.appointment_date}"
        self.custom_display = f"{self.appointment_date} - {doctor_name} - {patient_name}"

        # --- Check for overlapping appointments
        overlapping = frappe.db.sql("""
            SELECT name FROM `tabClinic Appointment`
            WHERE doctor = %s
              AND appointment_date = %s
              AND name != %s
              AND (
                    (appointment_time < %s AND end_time > %s) OR
                    (appointment_time < %s AND end_time > %s) OR
                    (appointment_time >= %s AND end_time <= %s)
              )
        """, (
            self.doctor,
            self.appointment_date,
            self.name,
            self.end_time, self.end_time,
            self.appointment_time, self.appointment_time,
            self.appointment_time, self.end_time
        ))

        if overlapping:
            frappe.throw("Overlapping appointment exists for this doctor during the selected time slot.")

        # --- Check if doctor is available in time slots
        day_of_week = self.appointment_date.strftime("%A")

        slots = frappe.get_all(
            "Doctor Time Slot",
            filters={
                "parent": self.doctor,
                "parenttype": "Doctor",
                "day_of_week": day_of_week,
                "is_active": 1
            },
            fields=["start_time", "end_time"]
        )

        if not slots:
            frappe.throw(f"Doctor is not available on {day_of_week}.")

        fits = False
        for s in slots:
            start = s["start_time"]
            end = s["end_time"]

            if isinstance(start, str):
                start = datetime.strptime(start, "%H:%M:%S").time()
            elif isinstance(start, timedelta):
                start = (datetime.min + start).time()

            if isinstance(end, str):
                end = datetime.strptime(end, "%H:%M:%S").time()
            elif isinstance(end, timedelta):
                end = (datetime.min + end).time()

            if self.appointment_time >= start and self.end_time <= end:
                fits = True
                break

        if not fits:
            frappe.throw("Appointment time is outside the doctor's working hours for this day.")

    def on_submit(self):
        self.status = "Scheduled"

    def on_cancel(self):
        self.status = "Cancelled"

    def get_title(self):
        return self.custom_display