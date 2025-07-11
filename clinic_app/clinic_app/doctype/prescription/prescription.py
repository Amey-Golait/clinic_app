import frappe
from frappe.model.document import Document

class Prescription(Document):
    def validate(self):
        # Auto-fetch patient and doctor from selected appointment
        if self.appointment and (not self.patient or not self.doctor):
            try:
                appointment = frappe.get_doc("Clinic Appointment", self.appointment)
                self.patient = appointment.patient
                self.doctor = appointment.doctor
            except frappe.DoesNotExistError:
                frappe.throw(f"Appointment '{self.appointment}' does not exist.")
