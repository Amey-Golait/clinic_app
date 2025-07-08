import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class ClinicAppointment(Document):
    def validate(self):
        # Set display title
        if self.doctor and self.patient and self.appointment_date:
            doctor_name = frappe.db.get_value("Doctor", self.doctor, "doctor_name") or self.doctor
            patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
            self.display_title = f"{doctor_name} - {patient_name} - {self.appointment_date}"

        # Auto-set end_time = appointment_time + 30 minutes
        if self.appointment_time and self.appointment_date:
            self.end_time = (datetime.combine(self.appointment_date, self.appointment_time) + timedelta(minutes=30)).time()

        # Check for overlapping appointments
        if self.appointment_time and self.end_time and self.doctor and self.appointment_date:
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

    def on_submit(self):
        self.status = "Scheduled"

    def on_cancel(self):
        self.status = "Cancelled"
